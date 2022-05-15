rule summarize_coverage_per_base:
    input:
        observed_counts = expand(config["output_dir"]+"{batch}/coverage_per_base/{sample}.csv", batch=DONE_NOT_SUMMARIZED, allow_missing=True)
    output:
        observed_counts_summarized = expand(config["output_dir"]+"{batch}/coverage_per_base/{sample}.csv.summarized", batch=DONE_NOT_SUMMARIZED, allow_missing=True)
        #observed_counts_summarized = config["output_dir"]+"{batch}/coverage_per_base/{sample}.csv.summarized",
    params:
        time_dir = config["output_dir"]+"timers/summary/coverage_per_base/count_bases_in_alignment_summary.txt",
        summary_file = config["output_dir"]+"summary/coverage_per_base/{sample}.csv",  #nemoze byt ako output file, lebo by sa prepisal
        summary_file_log = config["output_dir"]+"summary/coverage_per_base/{sample}.log" #nemoze byt ako output file, lebo by sa prepisal
    run:
        start = time.time()
        if not os.path.exists(params.summary_file): #create empty output file for barcode if not exists
            with open(params.summary_file, "w+"):
                pass
        for file in input.observed_counts:
            if not os.path.exists(file): #create empty file for barcode if not exists
                with open(file, "w+"):
                    pass
        create_merge_file_copy(params.summary_file)#create temporary file (to ensure that the original one wont be damaged on interrupt)
        merge(True, [1,2,3,4], [1,2,3,4], True, True, 0, 0, input.observed_counts, params.summary_file+".merging", params.summary_file+".merging")
        for file in input.observed_counts: #mark all files as summarized
            shell("mv "+file+" "+file+".summarized")
        with open(params.summary_file_log, "a+") as f: #print summarized files to log file
            for ifile in input.observed_counts:
                print(ifile, file = f)
        replace_merged_file(params.summary_file) #replace previous file with the new one
        with open(params.time_dir, "a+") as f:
            print(str(input.observed_counts)+","+str(time.time()-start), file = f)
    