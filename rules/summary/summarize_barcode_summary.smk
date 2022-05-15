rule summarize_barcode_summary:
    input:
        barcode_summary = expand(config["output_dir"]+"{batch}/barcode_summary/summary.csv", batch=DONE_NOT_SUMMARIZED)
    output:
        barcode_summary = expand(config["output_dir"]+"{batch}/barcode_summary/summary.csv.summarized", batch=DONE_NOT_SUMMARIZED),
        #observed_counts_summarized = config["output_dir"]+"{batch}/coverage_per_base/{sample}.csv.summarized",
    params:
        time_dir = config["output_dir"]+"timers/summary/barcode_summary/debarcoding_summary.txt",
        summary_file = config["output_dir"]+"summary/barcode_summary/summary.csv", #nemoze byt ako output file, lebo by sa prepisal
        summary_file_log = config["output_dir"]+"summary/barcode_summary/summary.log" #nemoze byt ako output file, lebo by sa prepisal
        
    run:
        start = time.time()
        if not os.path.exists(params.summary_file): #create empty output file if not exists
            with open(params.summary_file, "w+"):
                pass
        for file in input.barcode_summary:
            if not os.path.exists(file): #create empty file if not exists
                with open(file, "w+"):
                    pass
        create_merge_file_copy(params.summary_file)#create temporary file (to ensure that the original one wont be damaged on interrupt)
        #merge(group_start, count_first, count_second, has_header_first, has_header_second, group_by_first, group_by_second, fname1, fname2, output)
        merge(False, [1,2], [0,1], False, False, 3, 2, input.barcode_summary, params.summary_file+".merging", params.summary_file+".merging")
        for file in input.barcode_summary: #mark all files as summarized
            shell("mv "+file+" "+file+".summarized") #mark file as summarized
        with open(params.summary_file_log, "a+") as f: #print summarized files to log file
            for ifile in input.barcode_summary:
                print(ifile, file = f)  
        replace_merged_file(params.summary_file) #replace previous file with the new one
        with open(params.time_dir, "a+") as f:
            print(str(input.barcode_summary)+","+str(time.time()-start), file = f)