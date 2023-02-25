import argparse  
from pipelinerunner import PipelineRunner
import yaml
import os

def main():
    parser = argparse.ArgumentParser()
    #parser.add_argument("-o", "--output_path", help = "output path", required=True) #output_dir
    #parser.add_argument("-i", "--input_path", help = "input path (folder containing fast5 files to make batches from)", required=True) #input_path
    #parser.add_argument("-s", "--scripts_dir", help = "path to the scripts dir", required=True) #scripts_dir
    parser.add_argument("-conf", "--config_dir", help = "path to the config dir", required=True)
    #parser.add_argument("-b", "--num_of_barcodes", help = "num of bercodes", required=True) #barcodes
    #parser.add_argument("-bmin", "--min_batches", help = "minimal number of new batches needed to run the pipeline", default=3) #min_batches
    #parser.add_argument("-bmax", "--max_batches", help = "maximal number of batches to be processed at one time", default=5) #max_batches
    #parser.add_argument("-bs", "--batch_size", help = "number of files in a batch", default=10) #batch_size
    #parser.add_argument("-bf", "--batch_folder", help = "where to create the batches", default=None) #batch_path
    #parser.add_argument("-mut", "--mut_file", help = "path to file defining SNPs for a variant", required=True) #mut_file
    #parser.add_argument("-ref", "--reference", help = "path to a file containing reference genome", required=True) #reference_genome
    #parser.add_argument("-ca", "--clear_annotated", dest='clear_annotated', action='store_true') #clear_annotated
    #parser.add_argument("-cor", "--cores", help = "maximal number of cores provided for the snakemake pipeline", default=1)
    #parser.add_argument("-sb", "--store_batches", dest='store_batches', action='store_true') #store_batches
    #parser.add_argument("-vct", "--variant_calling_threshold", help = "threshold for variant calling script - min covarage for a SNP that is considered as relevant", default=42) #variant_calling_threshold
    #parser.set_defaults(clear_annotated=False)
    #parser.set_defaults(store_batches=False)

    args = parser.parse_args()
    """
    num_of_barcodes = int(args.num_of_barcodes)
    batch_min = int(args.min_batches)
    batch_max = int(args.max_batches)
    batch_size = int(args.batch_size)
    variant_calling_threshold = int(args.variant_calling_threshold)
    """
    yaml_args = load_config(args.config_dir)
    check, missing = check_config(yaml_args) #check config and attempt to get missing values
    if check:
        for key in missing:
            yaml_args[key] = missing[key]
            print("setting new "+str(key))
                
        pipeline = PipelineRunner(args.config_dir, yaml_args)
        pipeline.run()
            
        

def load_config(config_dir):
    config_yaml = os.path.join(config_dir,'config.yaml')
    yaml_args = {}
    with open(config_yaml) as config:
        yaml_args = yaml.safe_load(config)
    numbers = ["barcodes", "min_batches", "max_batches", "batch_size", "cores", "blitz_beam_size", "blitz_threads", "blitz_network_type", "alignment_low_cutoff", "coverage_threshold", "variant_calling_threshold"]
    for number in numbers:
        if not number in yaml_args:
            print("value "+number+" is not set")
        else:
            try:
                yaml_args[number] = int(yaml_args[number])
            except ValueError:
                print("invalid literal for int() with base 10: "+yaml_args[number]+" see config options for details")
    return yaml_args

def check_config(yaml_args):
    missing_args={}
    
    ############## scripts dir ################
    
    if "scripts_dir" in yaml_args:
        if not os.path.exists(yaml_args["scripts_dir"]):
            print("scripts dir path "+yaml_args["scripts_dir"]+" does not exist")
            #path in config file doeas not exist, attempt to get a valid path from the user:
            scrips_dir_path_input = input("Please enter a valid path to the /pande-mic/ directory:\n")
            if not os.path.exists(scrips_dir_path_input):
                print("sorry, the path is not valid, interrupting")
                return False, missing_args
            else:
                missing_args["scripts_dir"] = scrips_dir_path_input
    else:
        print("scripts dir path not set")
        scrips_dir_path_input = input("Please enter a path to the /pande-mic/ directory:\n")
        if not os.path.exists(scrips_dir_path_input):
            print("sorry, the path is not valid, interrupting")
            return False, missing_args
        else:
            missing_args["scripts_dir"] = scrips_dir_path_input
    
    ############ input path ##################
    
    if "input_path" in yaml_args:
        if not os.path.exists(yaml_args["input_path"]):
            print("input path "+yaml_args["input_path"]+" does not exist")
            #input path doeas not exist, attempt to get a valid path from the user:
            input_path_input = input("Please enter a valid path to the directory containing fast5 files:\n")
            if not os.path.exists(input_path_input):
                print("sorry, the path is not valid, interrupting")
                return False, missing_args
            else:
                missing_args["input_path"] = input_path_input
    else:
        print("input path not set")
        input_path_input = input("Please enter a path to the directory containing fast5 files:\n")
        if not os.path.exists(input_path_input):
            print("sorry, the path is not valid, interrupting")
            return False, missing_args
        else: 
            missing_args["input_path"] = input_path_input
    
    ############  reference genome  ############
    
        
    if "reference_genome" in yaml_args:
        if not os.path.exists(yaml_args["reference_genome"]):
            print("reference genome path "+yaml_args["reference_genome"]+" does not exist")
            reference_path_input = input("Please enter a valid path to the reference genome:\n")
            if not os.path.exists(reference_path_input):
                print("sorry, the path is not valid, interrupting")
                return False, missing_args
            else:
                missing_args["reference_genome"] = reference_path_input
    else:
        print("reference genome path not set")
        reference_path_input = input("Please enter a path to the reference genome:\n")
        if not os.path.exists(reference_path_input):
            print("sorry, the path is not valid, interrupting")
            return False, missing_args
        else: 
            missing_args["reference_genome"] = reference_path_input
            
    ########## mut file #############
            
    if "mut_file" in yaml_args:
        if not os.path.exists(yaml_args["mut_file"]):
            print("variant calling config file "+yaml_args["mut_file"]+" does not exist")
            mut_path_input = input("Please enter a valid path to the file with SNPs:\n")
            if not os.path.exists(mut_path_input):
                print("sorry, the path is not valid, interrupting")
                return False, missing_args
            else:
                missing_args["mut_file"] = mut_path_input
    else:
        print("variant calling config file path not set")
        mut_path_input = input("Please enter a path to the file with SNPs:\n")
        if not os.path.exists(mut_path_input):
            print("sorry, the path is not valid, interrupting")
            return False, missing_args
        else: 
            missing_args["mut_file"] = mut_path_input
            
    ###### output path exists or subdir writable? ###### 
    ask_for_outdir = False
    if "output_dir" in yaml_args:
        if not os.path.exists(yaml_args["output_dir"]):
            print("output dir " +yaml_args["output_dir"]+ " does not exist, checking whether subdir exists and is writable:")
            out_parent = os.path.abspath(os.path.join(yaml_args["output_dir"], os.pardir))
            if not os.path.exists(out_parent):
                print("parent of output dir "+out_parent+" does not exist")
                ask_for_outdir = True
            elif not os.access(out_parent, os.W_OK):
                print("output directory not writable")
                ask_for_outdir = True
            else:
                print("ok")
        elif not os.access(yaml_args["output_dir"], os.W_OK):
            print("output directory not writable")
            ask_for_outdir = True
    else:
        print("output directory not set")
        ask_for_outdir = True
        
    if ask_for_outdir:
        out_dir_input = input("please enter a path where to store the output: \n")
        if not os.path.exists(out_dir_input) and not os.path.exists(os.path.abspath(os.path.join(out_dir_input, os.pardir))):
            print("sorry, but this path does not exist, interrupting")
            return False, missing_args
        elif not os.access(os.path.abspath(os.path.join(out_dir_input, os.pardir)), os.W_OK) and not os.access(out_dir_input):
            print("sorry, but the directory is not writable, interrupting")
            return False, missing_args
        else:
            missing_args["output_dir"] = out_dir_input
            
    #### batch dir #####
    if "batch_path" in yaml_args:
        if not os.path.exists(yaml_args["batch_path"]) and not os.path.exists(os.path.abspath(os.path.join(yaml_args["batch_path"], os.pardir))):
            missing_args["batch_path"] = None
    else:
        missing_args["batch_path"] = None # create inside output dir
        
    ##### deepnano - blitz #####
    if "deepnanoblitz_path" in yaml_args:
        if not os.path.exists(yaml_args["deepnanoblitz_path"]):
            print("deepnano - blitz path "+yaml_args["deepnanoblitz_path"]+" is not valid")
            
            
            print("attempting to find the path..") #the user used provided install script
            parent_of_scripts_dir = ""
            if "scripts_dir" in missing_args:
                parent_of_scripts_dir = os.path.abspath(os.path.join(missing_args["scripts_dir"], os.pardir))
            elif "scripts_dir" in yaml_args:
                parent_of_scripts_dir = os.path.abspath(os.path.join(yaml_args["scripts_dir"], os.pardir))
            
            guess_path = parent_of_scripts_dir+"/deepnano-blitz/scripts/"
            if os.path.exists(guess_path):
                print("found deepnano-blitz at "+guess_path)
                missing_args["deepnanoblitz_path"] = guess_path
                
            else: #attemt to get the path from the user
            
                deepnanoblitz_path_input = input("Please enter a valid path to deepnano-blitz scripts directory:\n")
                if not os.path.exists(deepnanoblitz_path_input):
                    print("sorry, the path is not valid, interrupting")
                    return False, missing_args
                else:
                    missing_args["deepnanoblitz_path"] = deepnanoblitz_path_input
    else:
        print("deepnano-blitz scripts directory path not set")
        deepnanoblitz_path_input = input("Please enter a path to the deepnano-blitz scripts directory:\n")
        if not os.path.exists(mut_path_input):
            print("sorry, the path is not valid, interrupting")
            return False, missing_args
        else: 
            missing_args["deepnanoblitz_path"] = deepnanoblitz_path_input
            
    ###### guppy debarcoder #####    
    if "guppy_setup_path" in yaml_args:
        if not os.path.exists(yaml_args["guppy_setup_path"]):
            guppy_setup = input("guppy setup path "+yaml_args["guppy_setup_path"]+" is not valid. This should be a path to a shell script with configuration needed to run guppy debarcoder on your machine. [If no configuration is needed to run 'guppy barcoder <..params..>', please provide a path to an empty .sh script.]: \n")
            if not os.path.exists(guppy_setup):
                print("sorry, the path does not exist, interrupting")
                return False, missing_args
                if not os.access(guppy_setup, os.X_OK):
                    print("sorry, the path is not executable (to fix it, try running chmod +x on the file), interrupring")
            else:
                missing_args["guppy_setup_path"] = guppy_setup
        elif not os.access(yaml_args["guppy_setup_path"], os.X_OK):
            print("sorry, the guppy setup path "+yaml_args["guppy_setup_path"]+" is not executable, interrupting (to fix the issue, try running chmod +x on the file)")
            return False, missing_args        
            
    #### everything ok #####    
    return True, missing_args

if __name__ == "__main__":
    main()
