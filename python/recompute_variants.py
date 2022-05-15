import argparse  
from main import load_config
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-conf", "--config_dir", help = "path to the config dir", required=True)
    parser.add_argument("-mut", "--mut_file", help = "path to mut file to use", default="")

    args = parser.parse_args()
    yaml_args = load_config(args.config_dir)
    #print(yaml_args)
    mut_file = args.mut_file
    if args.mut_file == "":
        mut_file = yaml_args["mut_file"]

    SAMPLES = ["barcode0"+str(i) for i in range(1,10)]+["barcode"+str(i) for i in range(10,yaml_args["barcodes"]+1)]+["unclassified"]
    base_counts_dir = os.path.join(yaml_args["output_dir"],"summary/coverage_per_base/")
    variants_dir = os.path.join(yaml_args["output_dir"],"summary/variants/")
    reference = yaml_args["reference_genome"]

    #print(yaml_args["output_dir"])
    #print(base_counts_dir)

    for sample in SAMPLES:
        input = os.path.join(base_counts_dir, sample+".csv")
        output = os.path.join(variants_dir, sample+".json")
        command = "python variant_calling_from_counts.py "+input+" "+reference+" "+mut_file+" --threshold "+str(yaml_args["coverage_threshold"])+" --fraction "+str(yaml_args["coverage_fraction"])+" --output "+output
        #print(command)
        os.system(command)

if __name__ == "__main__":
    main()