rule count_bases_in_alignment:
    wildcard_constraints:
        batch="batch[0-9]*"
    input:
        bam = config["output_dir"]+"{batch}/aligned/{sample}.bam"
    params:
        reference = config["reference_genome"],
        alignment_low_cutoff = config["alignment_low_cutoff"],
        time_dir = config["output_dir"]+"timers/coverage_per_base/{batch}_count_bases_in_alignment.txt",
        scripts_dir = config["scripts_dir"]
    log:
        err = config["output_dir"]+"{batch}/log/count_bases/{sample}__count_observed_counts.err",
        log = config["output_dir"]+"{batch}/log/count_bases/{sample}__count_observed_counts.log"
    output:
        observed_counts = config["output_dir"]+"{batch}/coverage_per_base/{sample}.csv"
    shell:
        """
        START=$(date +%s.%N)
        python {params.scripts_dir}python/count_observed_counts.py {params.reference} {input.bam} --output {output.observed_counts} --alignment_low_cutoff {params.alignment_low_cutoff} > {log.log} 2> {log.err}
        END=$(date +%s.%N)
        DIFF=$(echo "$END - $START" | bc)
        echo {input.bam}, $DIFF >> {params.time_dir}
        """
