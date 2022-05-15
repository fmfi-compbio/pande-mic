rule summarize_aligned:
    input:
        aligned = expand(config["output_dir"]+"{batch}/aligned/mapped.csv", batch=DONE_NOT_SUMMARIZED)
    output:
        aligned = expand(config["output_dir"]+"{batch}/aligned/mapped.csv.summarized", batch=DONE_NOT_SUMMARIZED),
        #observed_counts_summarized = config["output_dir"]+"{batch}/coverage_per_base/{sample}.csv.summarized",
    params:
        time_dir = config["output_dir"]+"timers/summary/aligned/alignment_summary.txt",
        summary_file = config["output_dir"]+"summary/aligned/mapped.csv", #nemoze byt ako output file, lebo by sa prepisal
        summary_file_log = config["output_dir"]+"summary/aligned/mapped.log" #nemoze byt ako output file, lebo by sa prepisal

    run:
        start = time.time()
        if not os.path.exists(params.summary_file): #create empty output file if not exists
            with open(params.summary_file, "w+"):
                pass
        for file in input.aligned:
            if not os.path.exists(file): #create empty file if not exists
                with open(file, "w+"):
                    pass
        create_merge_file_copy(params.summary_file)#create temporary file (to ensure that the original one wont be damaged on interrupt)
        #merge(group_start, count_first, count_second, has_header_first, has_header_second, group_by_first, group_by_second, fname1, fname2, output)
        merge(True, [2], [1], False, False, 1, 0, input.aligned, params.summary_file+".merging", params.summary_file+".merging")
        for file in input.aligned: #mark all files as summarized
            shell("mv "+file+" "+file+".summarized") #mark file as summarized
        with open(params.summary_file_log, "a+") as f: #print summarized files to log file
            for ifile in input.aligned:
                print(ifile, file = f)  
        replace_merged_file(params.summary_file) #replace previous file with the new one
        with open(params.time_dir, "a+") as f:
            print(str(input.aligned)+","+str(time.time()-start), file = f)