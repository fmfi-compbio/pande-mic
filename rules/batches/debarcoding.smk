rule debarcoding:
    wildcard_constraints:
        batch="batch[0-9]*"
    input:
        fastq_dir = config["output_dir"]+"{batch}/basecalled/",
        basecall_done = config["output_dir"]+"{batch}/basecalled/.done"
    params:
        fastq_tmp_dir = config["output_dir"]+"{batch}/tmp{batch}/",
        fastq_tmp = config["output_dir"]+"{batch}/tmp{batch}/{batch}.fastq",
        out_dir = config["output_dir"]+"{batch}/debarcoded/",
        counting_file = config["output_dir"]+"{batch}/debarcoded/count.csv",
        time_dir = config["output_dir"]+"timers/debarcoded/{batch}_debarcoding.txt",
        scripts_dir = config["scripts_dir"],
        num_barcodes = config["barcodes"]
    threads: 1
    benchmark:
        config["output_dir"]+"timers/debarcoded_benchmark/{batch}_debarcoding.tsv"
    log:
        debarcoding_log = config["output_dir"]+"{batch}/log/debarcoding/{batch}__debarcoding.log",
        debarcoding_err = config["output_dir"]+"{batch}/log/debarcoding/{batch}__debarcoding.err"
    output:
        out = directory(config["output_dir"]+"{batch}/debarcoded/")
    shell:
        """
        START=$(date +%s.%N)
        python3 {params.scripts_dir}python/fake_debarcoder.py -i {input.fastq_dir} -o {params.out_dir} -n {params.num_barcodes}
        for d in {params.out_dir}/*/ ; do
            echo $({params.scripts_dir}bash/count_reads_and_bases.sh $d$(ls $d)),$(basename $d) >> {params.counting_file}
        done
        END=$(date +%s.%N)
        DIFF=$(echo "$END - $START" | bc)
        echo {input.fastq_dir}, $DIFF >> {params.time_dir}
        """
