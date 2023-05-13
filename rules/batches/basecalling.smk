rule basecalling:
    wildcard_constraints:
        batch="batch[0-9]*"
    input:
        fast5_dir = config["batch_path"]+"{batch}"
    params:
        deepnanopath = config["deepnanoblitz_path"],
        counting_file = config["output_dir"]+"{batch}/basecalled/count.csv",
        time_dir = config["output_dir"]+"timers/basecalled/{batch}_basecalling.txt",
        scripts_dir = config["scripts_dir"],
        batch_dir = config["output_dir"]+"{batch}/",
        beam_size = config["blitz_beam_size"],
        network_type = config["blitz_network_type"]
    threads: config["blitz_threads"]
    benchmark:
        config["output_dir"]+"timers/basecalled_benchmark/{batch}_basecalling.tsv"
    log:
        dpb_log = config["output_dir"]+"{batch}/log/basecalling/{batch}__deepnanoblitz.log",
        dpb_err = config["output_dir"]+"{batch}/log/basecalling/{batch}__deepnanoblitz.err"
    output:
        fastq = config["output_dir"]+"{batch}/basecalled/{batch}.fastq"
    shell:
        """
        START=$(date +%s.%N)
        {params.deepnanopath}deepnano2_caller.py \
                   --output {output.fastq} \
                   --output-format fastq \
                   --directory {input.fast5_dir} \
                   --beam-size {params.beam_size} \
                   --threads {threads} \
                   --network-type {params.network_type} > {log.dpb_log} 2> {log.dpb_err}
        touch {params.counting_file}
        {params.scripts_dir}bash/count_reads_and_bases.sh {output.fastq} >> {params.counting_file}
        END=$(date +%s.%N)
        DIFF=$(echo "$END - $START" | bc)
        echo {input.fast5_dir}, $DIFF >> {params.time_dir}
        """

#command='{params.deepnanopath}deepnano2_caller.py \
#           --output {output.fastq} \
#           --output-format fastq \
#           --directory {input.fast5_dir} \
#           --beam-size {params.beam_size} \
#           --threads {threads} \
#           --network-type {params.network_type} > {log.dpb_log} 2> {log.dpb_err}'
#t=$({{ time -p $command ; }} 2>&1 | grep "user\|sys"| awk '{{sum+=$2}}END{{print sum;}}')
#echo {input.fast5_dir}, $t >> {params.time_dir}
