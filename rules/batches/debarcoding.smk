rule debarcoding:
    wildcard_constraints:
        batch="batch[0-9]*"
    input:
        fastq = config["output_dir"]+"{batch}/basecalled/{batch}.fastq"
    params:
        fastq_tmp_dir = config["output_dir"]+"{batch}/tmp{batch}/",
        fastq_tmp = config["output_dir"]+"{batch}/tmp{batch}/{batch}.fastq",
        out_dir = config["output_dir"]+"{batch}/debarcoded/{batch}",
        counting_file = config["output_dir"]+"{batch}/debarcoded/count.csv",
        time_dir = config["output_dir"]+"timers/debarcoded/{batch}_debarcoding.txt",
        #guppy_setup_path = config["guppy_setup_path"],
        scripts_dir = config["scripts_dir"],
        guppy_config = config["guppy_config"],
        barcode_kits = config["guppy_barcode_kits"]
    threads: config["guppy_threads"]
    benchmark:
        config["output_dir"]+"timers/debarcoded_benchmark/{batch}_debarcoding.tsv"
    log:
        debarcoding_log = config["output_dir"]+"{batch}/log/debarcoding/{batch}__debarcoding.log",
        debarcoding_err = config["output_dir"]+"{batch}/log/debarcoding/{batch}__debarcoding.err"
    output:
        out = directory(config["output_dir"]+"{batch}/debarcoded/{batch}")
    shell:
        """
        START=$(date +%s.%N)
        mkdir {params.fastq_tmp_dir}
        ln -s {input.fastq} {params.fastq_tmp}
        guppy_barcoder --require_barcodes_both_ends \
                -i {params.fastq_tmp_dir} -s {params.out_dir} --worker_threads {threads} \
                --config "{params.guppy_config}" \
                --barcode_kits "{params.barcode_kits}" > {log.debarcoding_log} 2> {log.debarcoding_err}
        for d in {params.out_dir}/*/ ; do
            echo $({params.scripts_dir}bash/count_reads_and_bases.sh $d$(ls $d)),$(basename $d) >> {params.counting_file}
        done
        unlink {params.fastq_tmp}
        rm -rf {params.fastq_tmp_dir}
        END=$(date +%s.%N)
        DIFF=$(echo "$END - $START" | bc)
        echo {input.fastq}, $DIFF >> {params.time_dir}
        """
