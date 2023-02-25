import os, shutil
import time
from datetime import datetime
from variant_calling_from_counts import * 
from pipelinestate import *
import yaml
import math
import shutil
from test_utils import Test

class PipelineRunner:
    """
    The purpose of this class is to create the batches and run snakemake in a loop.
    """

    def __init__(self, config_dir, yaml_args):
    
        """
        set params, [clear annotated], print init. values, create summary dir and subdirs and empty .csv files
        """
        try:
            print(str(datetime.now())+":::"+"initializing...")

            self.state = InitState(self)
            self.should_stop = False
            self.output_path = yaml_args["output_dir"]
            self.input_path = yaml_args["input_path"]
            self.scripts_dir = yaml_args["scripts_dir"]
            self.config_dir = config_dir
            self.num_of_barcodes = yaml_args["barcodes"]
            self.batch_min = yaml_args["min_batches"]
            self.batch_max = yaml_args["max_batches"]
            self.batch_size = yaml_args["batch_size"]
            self.batches = 0
            self.fast5_batched = [] 
            self.not_summarized = []
            self.summarized = []
            self.reference = yaml_args["reference_genome"]
            self.mutations = yaml_args["mut_file"]
            self.iterations = 1
            self.cores = yaml_args["cores"]
            self.variant_calling_threshold = yaml_args["variant_calling_threshold"]
            self.blitz_threads = yaml_args["blitz_threads"]
            self.guppy_threads = yaml_args["guppy_threads"]
            self.guppy_path = yaml_args["guppy_path"]
            self.config_dir_copy = None
            self.yaml_args = yaml_args
            self.test = Test(self)

            if not os.path.exists(self.output_path):
                os.mkdir(self.output_path)
                print(str(datetime.now())+":::"+"created output dir (did not exist)")

            if yaml_args["clear_annotated"]:
                print(str(datetime.now())+":::"+"clear annotated flag set - clearing annotated files")
                self.clean_outdir()
            else:
                self.load_processed()

            self.create_config_copy()

            if yaml_args["batch_path"]==None:
                print(str(datetime.now())+":::"+"batch folder is None")
                yaml_args["batch_path"] = os.path.join(self.output_path, "batch/")

            self.batch_folder = yaml_args["batch_path"]

            if not os.path.exists(self.batch_folder):
                os.mkdir(self.batch_folder)
                print(str(datetime.now())+":::"+"created batch folder "+self.batch_folder)

            self.print_init_values()
            self.create_dirs()
            
            if not self.guppy_setup():
                print("cannot set up guppy, interrupting")
                self.interrupt_cleanup()
                try:
                    sys.exit(0)
                except SystemExit:
                    os._exit(0)

        except KeyboardInterrupt:
            self.stop()
            
    def guppy_setup(self):
        print("export GUPPYDIR="+self.guppy_path)
        res = os.system("export GUPPYDIR="+self.guppy_path)
        if res == 0:
            print("export LD_LIBRARY_PATH=$GUPPYDIR/lib:${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}")
            res2 = os.system("export LD_LIBRARY_PATH=$GUPPYDIR/lib:${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}")
            if res2 == 0:
                res3 = os.system("export PATH=$GUPPYDIR/bin:$PATH")
                print("export PATH=$GUPPYDIR/bin:$PATH")
                return res3 == 0
        return False

    def create_config_copy(self):
        """
        creates a copy of the config directory inside the output directory
        """
        if not os.path.exists(os.path.join(self.output_path,"config/")):
            src = self.config_dir
            dst = os.path.join(self.output_path,"config/")
            shutil.copytree(src, dst)
            os.rename(dst+"config.yaml", dst+"config_original.yaml")
            config_yaml = dst+"config.yaml"
            with open(config_yaml, 'w') as config_file:
                yaml.dump(self.yaml_args, config_file)
            self.config_dir_copy = dst
            print(str(datetime.now())+":::"+"created copy of config dir in output dir")


    def print_init_values(self, out=sys.stdout):
        print(file=out)
        print(str(datetime.now())+":::"+"init. values:", file=out)
        print("input path: "+self.input_path, file=out)
        print("output path: "+self.output_path, file=out)
        print("scripts dir: "+self.scripts_dir, file=out)
        print("num of barcodes: "+str(self.num_of_barcodes), file=out)
        print("minimal number of new batches: "+str(self.batch_min), file=out)
        print("maximal number of new batches: "+str(self.batch_max), file=out)
        print("batch size: "+str(self.batch_size), file=out)
        print("batch folder: "+self.batch_folder, file=out)
        print("mut (SNPs) file: "+self.mutations, file=out)
        print("reference: "+self.reference, file=out)
        print(file=out)

    def create_dirs(self):
        """
        creates the directories and files structure for the output files of the pipeline inside the output directory
        """
        #initialize summary dir
        directory = "summary"  
        path = os.path.join(self.output_path, directory)

        if not os.path.exists(path):
            os.mkdir(path)
            print(str(datetime.now())+":::"+"created summary dir")

        log_path = os.path.join(self.output_path, "log")
        if not os.path.exists(log_path):
            os.mkdir(log_path)
            print(str(datetime.now())+":::"+"created log dir")

        timers_path = os.path.join(self.output_path, "timers")
        if not os.path.exists(timers_path):
            os.mkdir(timers_path)
            print(str(datetime.now())+":::"+"created timers dir")

        batches_done = os.path.join(self.output_path, "batches_done")
        if not os.path.exists(batches_done):
            os.mkdir(batches_done)
            print(str(datetime.now())+":::"+"created batches_done dir")
        self.batches_done_path = batches_done

        summary_yaml_path = os.path.join(self.config_dir,'summary.yaml')
        #print("summary yaml path:", summary_yaml_path)
        self.summary_config = {}
        with open(summary_yaml_path) as f:
            self.summary_config = yaml.safe_load(f)
            #print("config loaded from summary yaml:", self.summary_config)
        summary_subdirs = list(self.summary_config['summary_subdirs'])
        print("summary subdirs:", summary_subdirs)
        #self.stop()
            
        not_exist = False
        for subdir in summary_subdirs:
            d = os.path.join(path, subdir)
            if not os.path.exists(d):
                os.mkdir(d)
                not_exist = True
        if not_exist:
            print(str(datetime.now())+":::"+"created summary subdirs")
        
        summarization_timers = os.path.join(timers_path, "summary")
        if not os.path.exists(summarization_timers):
            os.mkdir(summarization_timers)

        for subdir in summary_subdirs: #subdirs for timers dir
            d = os.path.join(timers_path, subdir)
            if not os.path.exists(d):
                os.mkdir(d)
            summary_d = os.path.join(summarization_timers, subdir)
            if not os.path.exists(summary_d):
                os.mkdir(summary_d)

    def load_processed(self):
        """
        loads the list of files that are already processed, counts and sets the number of iterations and processed batches
        """
        #load arr of processed files
        processed_path = self.output_path+"processed.csv"
        if os.path.exists(processed_path):
            with open(processed_path, "r") as f:
                for line in f:
                    self.batches+=1
                    l = line.split(",") # batch no., file1, file2, ..
                    for i in range(1, len(l)):
                        self.fast5_batched.append(l[i].strip())
            #print(self.batches, self.batch_max)
            self.iterations = math.ceil(self.batches/self.batch_max) #approx. iterations
            print("loaded data form previous run, "+str(len(self.fast5_batched))+" processed files found ("+str(self.batches)+" batches, "+str(self.iterations)+" iterations)")
            #self.batches+=1 #batches are numbered from 0
            self.iterations+=1
        self.state.switch(InitState)

    def find_unprocessed(self):
        """
        create a list of unprocessed files form the input directory (using os.listdir)
        """
        fast5s = [filename for filename in os.listdir(self.input_path) if os.path.splitext(filename)[1]==".fast5"]
        unprocessed = [fast5 for fast5 in fast5s if fast5 not in self.fast5_batched]
        return unprocessed
    
    def create_batches(self):
        """
        find unprocessed files (compare listdir with the array of previously batched files), 
        wait till we have enough files to create a batch, create batch(es) 
        - link files (os.symlink), 
        add files to the array of batched files
        """
        print(str(datetime.now())+":::"+"creating batches, starting at "+str(self.batches)+" (0-based)")
        self.state.switch(BatchingState)
        counter = 0
        self.not_summarized = []
        self.batch_strings = {} 
        unprocessed = self.find_unprocessed()
        print("# of unprocessed files: ", len(unprocessed))
        print("# of processed files:", len(self.fast5_batched))
        wait_count = 0
        while(len(unprocessed)<self.batch_min*self.batch_size): #wait until we have enough data 
            if not os.path.exists(self.batches_done_path): #if the directory is empty at the end of the pipeline run, sometimes it dissapears unexpectedly ?! 
                os.mkdir(self.batches_done_path)
                print(str(datetime.now())+":::"+"created batches_done dir")
            DONE_NOT_SUMMARIZED = [batch_done.split(".")[0] for batch_done in os.listdir(os.path.join(self.output_path,"batches_done")) if ( batch_done[0]!="." and  batch_done.split(".")[1] == "done") ]
            if len(unprocessed) == 0 and len(DONE_NOT_SUMMARIZED)>0:
                print("no new data, but there are batches to be summarized")
                break #break loop -> create 0 batches, run pipeline (summary)
            print(len(unprocessed), "unprocessed files")
            print("waiting for data...")
            missing_files = self.batch_size*self.batch_min-len(unprocessed)
            time.sleep(missing_files*10)
            unprocessed = self.find_unprocessed()
            # at the end of the run or during the times when our pipeline runs faster than the sequencing process, we want to process the observed files even though there is not enough of them
            wait_count+=1
            if wait_count == 3 and len(DONE_NOT_SUMMARIZED)>0:
                print("there might not be enough data to create a new batch, but there are batches to be summarized")
                break #break loop -> create 0 batches, run pipeline (summary)
            if wait_count == 3 and len(unprocessed)>0:
                print("there might not be enough data to create a batch of defined size and everything is summarized, but there are some unprocessed files - creating smaller batch")
                break
        if len(unprocessed)>=self.batch_min*self.batch_size: # we have enough data to create the minimal amount of batches specified in the config
            bmax = self.batches + self.batch_max 
            i = 0 #index in unprocessed files list
            while self.batches<bmax:
                if len(unprocessed)-i<self.batch_size: #if there is not enough files to create a batch, break
                        break
                line = str(self.batches)
                batch_dir = os.path.join(self.batch_folder, "batch"+str(self.batches))
                if not os.path.exists(batch_dir):
                    os.mkdir(batch_dir)
                    self.not_summarized.append(self.batches)
                    for j in range(self.batch_size):
                        link_from = os.path.join(self.input_path, unprocessed[i])
                        link_to = os.path.join(batch_dir, unprocessed[i])
                        if not os.path.exists(link_to):
                            os.symlink(link_from, link_to)
                        self.fast5_batched.append(unprocessed[i])
                        line += ","+unprocessed[i]
                        i+=1
                    self.batch_strings[self.batches] = line
                else: # the batch already exists - was created in the prevois pipeline run
                    print("batch "+str(self.batches)+" exists")
                    self.not_summarized.append(self.batches)
                    files = os.listdir(batch_dir)
                    for file in files:
                        line+=","+file
                        self.fast5_batched.append(file)
                    self.batch_strings[self.batches] = line
                self.batches += 1
                counter += 1
        elif len(unprocessed)<self.batch_min*self.batch_size and len(unprocessed)>0: #we do not have enough data to create the batches as specified in the config, but long enough time has passed, so we create one batch from all the unpocessed files
            unprocessed_files = len(unprocessed)
            line = str(self.batches)
            batch_dir = os.path.join(self.batch_folder, "batch"+str(self.batches))
            if not os.path.exists(batch_dir):
                os.mkdir(batch_dir)
                self.not_summarized.append(self.batches)
                for i in range(unprocessed_files):
                    link_from = os.path.join(self.input_path, unprocessed[i])
                    link_to = os.path.join(batch_dir, unprocessed[i])
                    if not os.path.exists(link_to):
                        os.symlink(link_from, link_to)
                    self.fast5_batched.append(unprocessed[i])
                    line += ","+unprocessed[i]
                self.batch_strings[self.batches] = line
            else:
                print("batch "+str(self.batches)+" exists")
                self.not_summarized.append(self.batches)
                files = os.listdir(batch_dir)
                for file in files:
                    line+=","+file
                    self.fast5_batched.append(file)
                self.batch_strings[self.batches] = line
            self.batches += 1
            counter += 1
        # if none of the above confitions is met, we will not create any new batch but the pipeline will run because there might be some bathces taht are not summarized
        print(str(datetime.now())+":::"+str(counter)+" batches created")
        #print("batch strings:", self.batch_strings)
        #print("not summarized:", self.not_summarized)

    def run_snakemake(self):
        """
        run the Snakemake pipeline
        """
        print(str(datetime.now())+":::"+"running snakemake pipeline, logging to "+self.output_path+"log/pipeline_run"+str(self.iterations)+".{out, err}", )
        self.state.switch(SnakemakeState)
        pipeline_path = os.path.join(self.scripts_dir, "Pipeline")
        out = os.path.join(self.output_path, "log/snake")
        t=time.time()
        #dag_command = "snakemake --rulegraph --snakefile "+pipeline_path+" --directory "+out+" --cores "+str(self.cores)+" --config scripts_dir="+self.scripts_dir+" config_dir="+self.config_dir+" > gvfile.txt"
        pipeline_run_command = "snakemake --snakefile "+pipeline_path+" --directory "+out+" --cores "+str(self.cores)+" --rerun-incomplete --config scripts_dir="+self.scripts_dir+" config_dir="+self.config_dir_copy+" >> "+self.output_path+"log/pipeline_run"+str(self.iterations)+"_"+str(t)+".out"+" 2>> "+self.output_path+"log/pipeline_run"+str(self.iterations)+"_"+str(t)+".err"
        print(str(datetime.now())+":::"+"starting pipeline, command: "+pipeline_run_command)
        #os.system(dag_command)
        res = os.system(pipeline_run_command)
        if res == 0:
            print(str(datetime.now())+":::"+"pipeline run completed")
            print("batches_done path exists after snakemake run completed:",os.path.exists(self.batches_done_path))
            return True 
        else:
            print(str(datetime.now())+":::"+"pipeline run ended with an error/interrupt")
            return False

    def clean_batches(self):
        """
        remove processed batch folders with symlinks
        """
        print(str(datetime.now())+":::"+"removing batch links")
        self.state.switch(BatchCleaningState)
        self.clear_dir(self.batch_folder)
        print(str(datetime.now())+":::"+"batch links removed")

    def clean_outdir(self):
        """
        clean the output directory
        """
        print(str(datetime.now())+":::"+"cleaning output directory "+self.output_path)
        self.clear_dir(self.output_path)
        print(str(datetime.now())+":::"+"directory "+self.output_path+" is now empty")

    def run(self):
        """
        The key method of the whole class, 
        repaet in a loop:
        1. create n batches (min<n<max) by linking files from a specified directory
        2. run snakemake on new n batches and merge processed batches into the summary, find variants
        3. remove links
        4. write processed batches and files into the log file
        """
        try:
            while True:
                print()
                print(str(datetime.now())+":::"+"iteration "+str(self.iterations)+" started")
                iteration_start = time.time()
                self.create_batches()
                snakemake_start = time.time()
                if(self.run_snakemake()):
                    print("run completed")
                    clean_batches_start = time.time()
                    self.clean_batches()
                    self.not_summarized = []
                    write_bathces_start =  time.time()
                    self.write_batches()
                    it_end = time.time()
                    self.iterations += 1
                    with open(os.path.join(self.output_path,"runtime.log"), "a+") as log:
                        print(str(self.iterations-1)+","+str(iteration_start)+","+str(snakemake_start)+","+str(clean_batches_start)+","+str(write_bathces_start)+","+str(it_end), file = log)
                else:
                    print(str(datetime.now())+":::"+"snakemake ended with an error/interrupt, look into the log files for details")
                    self.interrupt_cleanup()
                    break
                self.test.write_variants_log(self.iterations-1, len(self.fast5_batched))
        except KeyboardInterrupt:
            self.stop()

    def write_batches(self):
        """
        write lists of processed files for each processed batch into the log file (processed.csv)
        """
        self.state.switch(WriteBatchesState)
        with open(self.output_path+"processed.csv", "a+") as f:
            for batch in self.batch_strings:
                #time.sleep(3)
                if self.batch_strings[batch]!=None:
                    print(self.batch_strings[batch], file=f)
                    self.batch_strings[batch] = None

    def clear_dir(self, folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
    
    def stop(self):
        """
        method to be called when keyboard interrupt is detected
        """
        print(str(datetime.now())+":::"+"keyboard interrupt")
        self.interrupt_cleanup()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    
    def interrupt_cleanup(self):
        """
        handling interrupts using the State design pattern (see the PipelineState class)
        """
        print(str(datetime.now())+":::"+"interrupt detected, starting necessary cleanup, please wait")
        with open(os.path.join(self.output_path, "pipelinerunner.log"), 'a+') as f:
            self.print_init_values(out=f)
            self.test.timers_summary(out=f)
        self.state.handle_interrupt()
