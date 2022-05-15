#UNUSED
rule filtering:
    input:
        debarcoded_dir = config["output_dir"]+"debarcoded/"+config["batchname"]
    params:
        input_dir = config["output_dir"]+"debarcoded/"+config["batchname"],
        out_dir = config["output_dir"]+"filtered/"+config["batchname"],
        counting_file = config["output_dir"]+"filtered/count.csv",
        quality = config["quality"],
        length = config["length"],
        time_dir = config["output_dir"]+"timers/filtering.txt",
        scripts_dir = config["scripts_dir"]
    log:
        logfile = config["output_dir"]+"log/filtering/"+config["batchname"]+"__filtering.log",
        err = config["output_dir"]+"log/filtering/"+config["batchname"]+"__filtering.err"
    output:
        out = directory(config["output_dir"]+"filtered/"+config["batchname"]),
    shell:
        """
        START=$(date +%s.%N)
        mkdir {params.out_dir}
        for d in {params.input_dir}/*/ ; do
            SUBDIR=$(basename $d)
            mkdir {params.out_dir}/$SUBDIR
            for f in {params.input_dir}/$SUBDIR/*.fastq ; do
                FILE=$(basename $f)
                NanoFilt --quality {params.quality} --length {params.length} --logfile {log.logfile} $d$FILE >> {params.out_dir}/$SUBDIR/$FILE 2> {log.err}
                echo $({params.scripts_dir}/bash/count_reads_and_bases.sh {params.out_dir}/$SUBDIR/$FILE),$(basename $d) >> {params.counting_file}
            done
        done
        END=$(date +%s.%N)
        DIFF=$(echo "$END - $START" | bc)
        echo {input.debarcoded_dir}, $DIFF >> {params.time_dir}
        """
