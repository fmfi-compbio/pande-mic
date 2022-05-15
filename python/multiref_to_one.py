def load_fasta(filename: str):
    with open(filename) as f:
        yield from load_fasta_fd(f)


def load_fasta_fd(f):
    label, buffer = "", []
    for line in f:
        if len(line) > 0 and line[0] == ">":
            # new label
            if len(buffer) > 0:
                yield label, "".join(buffer)
            label = line.strip()[1:]
            buffer = []
        else:
            buffer.append(line.strip())
    if len(buffer) > 0:
        yield label, "".join(buffer)

def create_ref(ref_array, filename):
    with open(filename, "w") as f:
        print(">reference", file=f)
        for ref in ref_array:
            print(ref[1], file=f)
            print("N"*100, file=f)

def generate_contig_boundaries(ref_array, filename):
    positions = []
    positions2 = []
    position=0
    with open(filename, "w") as f:
        i=0
        for ref in ref_array:
            if i%2==0:
                positions.append([position, position+len(ref[1])])
            #print(position, position+len(ref[1]), file=f)
            else:
                positions2.append([position, position+len(ref[1])])
            position = position+len(ref[1])+101
            i+=1
        dictionary = {}
        dictionary["name"]= "Chromosomes"  
        dictionary["amplicons"]=positions+positions2 
        dict_str = str(dictionary)
        replaced = dict_str.replace("'",'"')
        print(replaced, file=f)

arr = list(load_fasta("ref.fasta"))
create_ref(arr, "new_ref.fasta")
generate_contig_boundaries(arr, "amplicons.json")
