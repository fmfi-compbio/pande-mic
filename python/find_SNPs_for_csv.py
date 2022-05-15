import os
import sys
import argparse
import json

from helpers import load_fasta, l2n, letters

def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("base_counts_path", type=str)
    parser.add_argument("reference", type=str)
    parser.add_argument("-t", "--threshold", type=int, default=42) #minimal coverage
    parser.add_argument("--fraction", type=float, default=0.5)
    parser.add_argument("-o", "--output_dir", type=str, required=True)
    return parser.parse_args(argv)
    


def load_base_counts_file(file_path, reference):
    barcode_array = [[0 for _ in letters] for _ in reference]
    with open(file_path, "r") as f:
        first = True
        for line in f:
            if not first:
                l = line.split(",")
                print("split line:", l)
                position = int(l[0])-1
                A = int(l[1])
                C = int(l[2])
                G = int(l[3])
                T = int(l[4])
                print("A,C,G,T:", A, C, G, T)
                barcode_array[position][0]+=A
                barcode_array[position][1]+=C
                barcode_array[position][2]+=G
                barcode_array[position][3]+=T   
            first = False
    return barcode_array


def detect_SNPs_in_barcode(barcode, threshold, reference, fraction): 
    SNPs = [] # list of lists [mutation, #of bases same as ref, #mutated]
    ref_length = len(reference)
    for position in range(0, ref_length):
        #print("position", position)
        reference_base = reference[position].upper()
        coverage = barcode[position][0]+barcode[position][1]+barcode[position][2]+barcode[position][3]
        #print("position", position, "coverage is ", coverage)
        if coverage >= threshold:
            print("position", position, "coverage is ", coverage)
            for letter in "ACGT":
                print("letter", letter)
                if reference_base in letters and letter != reference_base and barcode[position][l2n[letter]] > barcode[position][l2n[reference_base]] and barcode[position][l2n[letter]]>=fraction*coverage:
                    SNPs.append([reference_base+str(position+1)+letter, \
                        str(barcode[position][l2n[reference_base]]), \
                        str(barcode[position][l2n[letter]])] )
                    print("SNP found:"+ reference_base+str(position+1)+letter + ",# of bases same as ref: "+\
                        str(barcode[position][l2n[reference_base]])+ ",# mutated: "+ str(barcode[position][l2n[letter]]))
    return SNPs

def write_SNPs_for_barcode_to_file(SNPs_list, fname):
    with open(fname, 'w') as f:
        print("snp, same_as_ref, mutated", file=f)
        for snp in SNPs_list:
            line = (",").join(snp) 
            print(line, file=f)
            
def main():
    args = parse_args(sys.argv[1:])   
    reference = list(load_fasta(args.reference))[0][1]
    base_counts = load_base_counts_file(args.base_counts_path, reference)
    threshold = args.threshold
    SNPs = detect_SNPs_in_barcode(base_counts, threshold, reference, args.fraction)
    output_dir = args.output_dir
    write_SNPs_for_barcode_to_file(SNPs, output_dir)
    

    
if __name__ == "__main__":
    main()
