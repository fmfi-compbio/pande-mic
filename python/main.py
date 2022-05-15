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
    if check_config(yaml_args):
        pipeline = PipelineRunner(args.config_dir, yaml_args["output_dir"], yaml_args["input_path"], yaml_args["scripts_dir"], yaml_args["barcodes"], yaml_args["min_batches"], yaml_args["max_batches"], yaml_args["batch_size"], yaml_args["variant_calling_threshold"],  yaml_args["batch_path"], yaml_args["reference_genome"], yaml_args["mut_file"], yaml_args["clear_annotated"], yaml_args["cores"], yaml_args["blitz_threads"], yaml_args["guppy_threads"])
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
    if "scripts_dir" in yaml_args:
        if not os.path.exists(yaml_args["scripts_dir"]):
            print("scripts dir path "+yaml_args["scripts_dir"]+" does not exist")
            return False
    else:
        print("scripts dir path not set")
        return False
    if "input_path" in yaml_args:
        if not os.path.exists(yaml_args["input_path"]):
            print("input path "+yaml_args["input_path"]+" does not exist")
            return False
    else:
        print("input path not set")
        return False
    if "reference_genome" in yaml_args:
        if not os.path.exists(yaml_args["reference_genome"]):
            print("reference genome path "+yaml_args["reference_genome"]+" does not exist")
            return False
    else:
        print("reference genome path not set")
        return False
    if "mut_file" in yaml_args:
        if not os.path.exists(yaml_args["mut_file"]):
            print("variant calling config file "+yaml_args["mut_file"]+" does not exist")
            return False
    else:
        print("variant calling config file path not set")
        return False
    return True

if __name__ == "__main__":
    main()
