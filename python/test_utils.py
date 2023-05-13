import json, sys, time, os

class Test:

    def __init__(self, pipelinerunner):
        self.pipelinerunner = pipelinerunner
        self.start_time = time.time()
        self.variants = {}

    ##times summary

    def timers_summary(self, out=sys.stdout):
        total_time_this_run = time.time() - self.start_time
        pipeline_real_time_sum, iterations = self.sum_pipeline_real_time()
        processed_files = len(self.pipelinerunner.fast5_batched)

        print(file=out)
        print("total time (real, this run):", total_time_this_run, file=out)
        print("pipeline real time:", pipeline_real_time_sum, file=out) 
        print("iterations:", iterations, file=out)
        print("# files processed:", processed_files, file=out)
        print("-------------", file=out)
        print("cpu times:", file=out)
        times_dict = self.sum_cpu_times()
        total_cpu_time = 0
        multiplier = ""
        for key in times_dict:
            if key == "debarcoded":
                multiplier = "x"+str(self.pipelinerunner.guppy_threads)
            elif key == "basecalled":
                multiplier = "x"+str(self.pipelinerunner.blitz_threads)
            elif "benchmark" in key:
                total_cpu_time+=times_dict[key]["cpu_time"]
            else:
                total_cpu_time+=times_dict[key]
            print(key+":", times_dict[key], multiplier, file = out)
        print("------------", file=out)
        print("total cpu time:", total_cpu_time, file=out)


    def sum_pipeline_real_time(self):
        real_time_sum = 0
        iterations = 0
        if not os.path.exists(os.path.join(self.pipelinerunner.output_path,"runtime.log")):
            return 0, 0
        with open(os.path.join(self.pipelinerunner.output_path,"runtime.log"), "r") as log:
            for line in log:
                l = line.split(',')
                iteration_time = float(l[5])-float(l[1])
                real_time_sum+=iteration_time
                iterations +=1
        return real_time_sum, iterations

    def sum_cpu_times(self):
        times_dict = {}
        dirs = os.listdir(os.path.join(self.pipelinerunner.output_path,"timers/"))
        for directory in dirs:
            if directory[0]!='.' and directory!="summary" and not ("benchmark" in directory):
                times_dict[directory]=self.sum_times_in_dir(os.path.join(self.pipelinerunner.output_path,"timers/")+directory)
            if "benchmark" in directory:
                times_dict[directory]=self.sum_snakemeke_benchmark_times_dir(os.path.join(self.pipelinerunner.output_path,"timers/")+directory)   
        dirs = os.listdir(os.path.join(self.pipelinerunner.output_path,"timers/summary/"))
        for directory in dirs:
            if directory[0]!='.':
                times_dict[directory+"_summary"]=self.sum_times_in_dir(os.path.join(self.pipelinerunner.output_path,"timers/summary/")+directory) 
        return times_dict
    
    def sum_times_in_dir(self,dir):
        sum_time = 0
        files = os.listdir(dir)
        for file in files:
            with open(os.path.join(dir, file)) as f:
                for line in f:
                    l = line.split(',')
                    sum_time+=float(l[1])
        return sum_time

    def sum_snakemeke_benchmark_times_dir(self, dir):
        res = {}
        cpu_time = 0
        real_time = 0
        files = os.listdir(dir)
        for file in files:
            with open(os.path.join(dir, file)) as f:
                f.readline()
                data = f.readline()
                splitline = data.split('\t')
                cpu_time+=float(splitline[9])
                real_time+=float(splitline[0])
        res["cpu_time"]=cpu_time
        res["real_time"]=real_time
        return res

    ##variant logging

    def write_variants_log(self, iterations, files):
        if self.pipelinerunner.iterations >= 1:
            self.read_variants()
        with open(os.path.join(self.pipelinerunner.output_path,"variant.log"), "a+") as log:
            print(iterations, files, time.time(), file=log)
            json.dump(self.variants, log)
            print(file=log)
            print(file=log)

    def read_variants(self):
        barcodes = ["barcode0"+str(i) for i in range(1,10)]+["barcode"+str(i) for i in range(10,self.pipelinerunner.num_of_barcodes+1)]+["unclassified"]
        self.variants = {}
        for barcode in barcodes:
            self.variants[barcode] = self.read_variants_for_barcode(barcode)

    def read_variants_for_barcode(self, barcode):
        json_path = self.pipelinerunner.output_path+"summary/variants/"+barcode+".json"
        if os.path.exists(json_path):
            with open(json_path, "r") as read_file:
                data = json.load(read_file)
            return data
        else: 
            return []
