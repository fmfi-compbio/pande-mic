import os
import sys
import argparse
import json

from helpers import load_fasta, l2n, letters

class Tree:
    def __init__(self, name, min_num):
        self.children = []
        self.data = []
        self.name = name
        self.min_num = min_num

def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", type=str)
    parser.add_argument("reference", type=str)
    parser.add_argument("mutations", type=str)
    parser.add_argument("--threshold", type=int, default=42) #minimal number of reads needed
    parser.add_argument("--fraction", type=float, default=0.5)
    parser.add_argument("-o", "--output", type=str, required=True) #json file
    return parser.parse_args(argv)
    
def load_base_counts_file(file_path, reference):
    barcode_array = [[0 for _ in letters] for _ in reference]
    with open(file_path, "r") as f:
        first = True
        for line in f:
            if not first:
                l = line.split(",")
                #print("split line:", l)
                position = int(l[0])-1
                A = int(l[1])
                C = int(l[2])
                G = int(l[3])
                T = int(l[4])
                #print("A,C,G,T:", A, C, G, T)
                barcode_array[position][0]+=A
                barcode_array[position][1]+=C
                barcode_array[position][2]+=G
                barcode_array[position][3]+=T   
            first = False
    return barcode_array


def load_mutations(mutations_path):    #loading .txt file containing mutations for each variant
    
    mutations = Tree("root", 0)
    stack = []
    index = 0
    stack.append(mutations)
    
    with open (mutations_path, "r") as txtfile:
        mut_name = ""
        maybeparent = mutations
        for line in txtfile:
            line = line.strip()
            if line == "start_sub":
                stack.append(maybeparent)
                index += 1
            elif line == "end_sub":
                stack.pop()   
                index -= 1       
            elif not line.startswith('#') and line:
                variant_row = line.split() #split on any whitespace
                parent = stack[index]  
                child = Tree(variant_row[0], int(variant_row[1]))
                for i in range(2, len(variant_row)):
                    if len(variant_row[i])>2 and variant_row[i][2].isdigit(): #append only SNPs
                        child.data.append(variant_row[i])

                parent.children.append(child)
                maybeparent = child            

    return mutations

def find_variants(barcode_array, variants, jsonfile, threshold, fraction): #looking for possible variants for a barcode
    barcode_variants = []
    for v in variants.children:
        variant=check_variant(barcode_array, threshold, v, fraction)
        if variant != None:
            barcode_variants.append(variant)
    print(json.dumps(barcode_variants), file=jsonfile)    
    return len(barcode_variants)!=0


def check_variant(barcode, threshold, variant, fraction): #check whether this variant meets our conditions
    num_of_mutations = 0
    variant_dict = {}
    variant_dict['name'] = variant.name
    variant_dict['mutations'] = []
    #print(variant.data)
    for mut in variant.data:
        #if mut[2].isdigit():
        position = int(mut[1:len(mut)-1])-1
                    
        #check that the position is within range        
        if position < 0 or position >= len(barcode):
            continue
        
        same_as_reference = barcode[position][l2n[mut[0]]] #num of bases same as reference
        same_as_mutation = barcode[position][l2n[mut[len(mut)-1]]]; #num of bases same as mutation
        reads_coverage = barcode[position][0]+barcode[position][1]+barcode[position][2]+barcode[position][3]
                
        if same_as_reference < same_as_mutation and reads_coverage >= threshold and same_as_mutation>=fraction*reads_coverage:                     
            num_of_mutations += 1
            mutation_dict = {}
            mutation_dict['position'] = position+1
            mutation_dict['from'] = mut[0]
            mutation_dict['to'] = mut[len(mut)-1]
            mutation_dict['same_as_reference'] = same_as_reference
            mutation_dict['same_as_mutation'] = same_as_mutation
            variant_dict['mutations'].append(mutation_dict)
               
   
    variant_dict['subs'] = []
    #we found a variant 
    if num_of_mutations >= variant.min_num:
        #if the variant has subvariants, check them.
        if (len(variant.children) > 0):
            for subv in variant.children:
                subv_dict = check_variant(barcode, threshold, subv, fraction)
                if (subv_dict != None):
                    variant_dict['subs'].append(subv_dict)
        return variant_dict 
    #if there is not enough mutations matched for this variant
    else:
    	return None


def variant_calling(file_path, reference, mutations, threshold, output):
    reference = list(load_fasta(reference))[0][1]
    barcode_array = load_base_counts_file(file_path, reference)
    variants = load_mutations(mutations)
    with  open(output, "w") as jsonfile:
         variant_found = find_variants(barcode_array, variants, jsonfile, threshold)
    if variant_found:
        return 1
    else:
        return 0


def main():
    args = parse_args(sys.argv[1:])   
    reference = list(load_fasta(args.reference))[0][1]
    barcode_array = load_base_counts_file(args.file_path, reference)
    variants = load_mutations(args.mutations)
    threshold = args.threshold
    with  open(args.output, "w") as jsonfile:
    	find_variants(barcode_array, variants, jsonfile, threshold, args.fraction)

    
if __name__ == "__main__":
    main()
