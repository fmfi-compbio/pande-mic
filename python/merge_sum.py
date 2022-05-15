import sys, os, shutil
import argparse

def merge(group_start, count_first, count_second, has_header_first, has_header_second, group_by_first, group_by_second, fnames, fname2, output):
    #print("merging "+fname1+" with "+fname2)
    count_len = len(count_first)
    if len(count_first)!=len(count_second):
        print("count_arr lengths must be equal", file=sys.stderr)
        exit(1)

    if group_by_first >= 0 and group_by_second >= 0: #grouping enabled
        summary = {}
        for fname1 in fnames:
            with open(fname1, "r") as f:
                line_counter = 0 if has_header_first else 1
                for line in f:
                    l = line.strip().split(",")
                    if line_counter == 0:
                        head_arr = [l[i] for i in count_first]
                        head_group = l[group_by_first]
                    if line_counter > 0:
                        if not l[group_by_first] in summary:
                            summary[l[group_by_first]]=[0 for _ in count_first]
                        for i in range(count_len):
                            summary[l[group_by_first]][i]+=int(l[count_first[i]])
                                
                    line_counter+=1

        with open(fname2,"r") as f2:
            line_counter = 0 if has_header_second else 1
            for line in f2:
                l = line.strip().split(",")
                if line_counter > 0:
                    if not l[group_by_second] in summary:
                        summary[l[group_by_second]]=[0 for _ in count_second]
                    for i in range(count_len):
                        summary[l[group_by_second]][i]+=int(l[count_second[i]])
                            
                line_counter+=1    


        with open(output, "w") as out: 
            if group_start:        
                if has_header_first:
                    print(head_group+","+(",").join(head_arr), file=out)
                for key in summary:
                    print(key+","+(",").join([str(_) for _ in summary[key]]), file=out)
            else:
                if has_header_first:
                    print((",").join(head_arr)+","+head_group, file=out)
                for key in summary:
                    print((",").join([str(_) for _ in summary[key]])+","+key, file=out)
                
    elif group_by_first == -1 and group_by_second == -1: #no grouping
        summ = [0 for _ in count_first]
        for fname1 in fnames:
            with open(fname1, "r") as f:
                line_counter = 0 if has_header_first else 1
                for line in f:
                    l = line.strip().split(",")
                    if line_counter == 0:
                        head_arr = [l[i] for i in count_first]
                    if line_counter > 0:
                        for i in range(count_len):
                            summ[i]+=int(l[count_first[i]])
                line_counter+=1
            
        with open(fname2, "r") as f2:
            line_counter = 0 if has_header_second else 1
            for line in f2:
                l = line.strip().split(",")
                if line_counter > 0:
                    for i in range(count_len):
                        summ[i]+=int(l[count_second[i]])
            line_counter+=1
            
        with open(output, "w") as out: 
            if has_header_first:
                print((",").join(head_arr), file=out)
            print((",").join([str(_) for _ in summ]), file=out)
        

    else:
        print("you have to specify group_by in both files or in none of them", file=sys.stderr)
        exit(1)


def replace_merged_file(file):
    prev = file
    newfile = file+".merging"
    os.rename(prev, prev+'.bkp')
    os.rename(newfile, prev)
    os.unlink(prev+".bkp")

def create_merge_file_copy(file):
    if os.path.exists(file+".merging"):
        os.unlink(file+".merging")
    shutil.copyfile(file, file+".merging") 



def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-f1", "--first_file_name", help = "first file to merge/or file names of multiple files with same structure separated by comma")
    parser.add_argument("-f2", "--second_file_name", help = "second file to merge")
    parser.add_argument("-cf","--count_first", help = "columns to be summed in first file seperated by ,")
    parser.add_argument("-gpf", "--group_by_first", default = -1, help = "column to use for grupping in first file or -1")
    parser.add_argument("-hf","--has_header_first", default = 1, help = "1 if first file has a header, 0 otherwise")
    parser.add_argument("-cs","--count_second", help = "columns to be summed in second file seperated by ,")
    parser.add_argument("-gps","--group_by_second", default = -1, help = "column to use for grupping in second file or -1")
    parser.add_argument("-hs","--has_header_second", default = 1, help = "1 if second file has a header, 0 otherwise")
    parser.add_argument("-gs","--group_start", default = 1, help = "whether the output should start with group (1) or not (0)")
    parser.add_argument("-o","--out", help = "output file")


    args = parser.parse_args()


    group_start = True if int(args.group_start) == 1 else False
    count_first = args.count_first.split(",")
    count_first = [int(_) for _ in count_first]
    count_second = args.count_second.split(",")
    count_second = [int(_) for _ in count_second]
    has_header_first = True if int(args.has_header_first) == 1 else False
    has_header_second = True if int(args.has_header_second) == 1 else False
    group_by_first = int(args.group_by_first)
    group_by_second = int(args.group_by_second)
    fname1 = args.first_file_name.split(",")
    fname2 = args.second_file_name
    output = args.out

    merge(group_start, count_first, count_second, has_header_first, has_header_second, group_by_first, group_by_second, fname1, fname2, output)

if __name__ == "__main__":
    main()
