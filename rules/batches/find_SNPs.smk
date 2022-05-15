rule find_SNPs:
    wildcard_constraints:
        batch="batch[0-9]*"
    input:
        observed_counts = config["output_dir"]+"{batch}/"+"coverage_per_base/{sample}.csv"
    params:
        reference = config["reference_genome"],
        threshold = config["coverage_threshold"],
        time_dir = config["output_dir"]+"timers/SNPs/{batch}_find_SNPs.txt",
        scripts_dir = config["scripts_dir"]
    log:
        err = config["output_dir"]+"{batch}/"+"log/find_SNPs/{sample}__find_SNPs.err",
        log = config["output_dir"]+"{batch}/"+"log/find_SNPs/{sample}__find_SNPs.log"
    output:
        SNPs = config["output_dir"]+"{batch}/"+"SNPs/{sample}.csv"
    shell:
        """
        START=$(date +%s.%N)
        python {params.scripts_dir}python/find_SNPs_for_csv.py {input.observed_counts} {params.reference} --threshold {params.threshold} \
        --output_dir {output.SNPs} > {log.log} 2> {log.err}
        END=$(date +%s.%N)
        DIFF=$(echo "$END - $START" | bc)
        echo {input.observed_counts}, $DIFF >> {params.time_dir}
        """
