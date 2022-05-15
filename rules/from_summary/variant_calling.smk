rule variant_calling:
    input:
        observed_counts_summarized = expand(config["output_dir"]+"{batch}/coverage_per_base/{sample}.csv.summarized", batch=DONE_NOT_SUMMARIZED, allow_missing=True)
    params:
        observed_counts = config["output_dir"]+"summary/coverage_per_base/{sample}.csv", #nemoze byt input, ak nemoze byt output v summarize_coverage_per_base rule
        reference = config["reference_genome"],
        threshold = config["variant_calling_threshold"],
        fraction = config["coverage_fraction"],
        mut_file = config["mut_file"],
        time_dir = config["output_dir"]+"timers/variants/variant_calling.txt",
        scripts_dir = config["scripts_dir"]
    log:
        err = config["output_dir"]+"log/variant_calling/{sample}__variant_calling_from_counts.err",
        log = config["output_dir"]+"log/variant_calling/{sample}__variant_calling_from_counts.log"
    output:
        variants = config["output_dir"]+"summary/variants/{sample}.json"
    shell:
        """
        START=$(date +%s.%N)
        python {params.scripts_dir}python/variant_calling_from_counts.py {params.observed_counts} {params.reference} {params.mut_file} --threshold {params.threshold} --fraction {params.fraction}\
        --output {output.variants} > {log.log} 2> {log.err}
        END=$(date +%s.%N)
        DIFF=$(echo "$END - $START" | bc)
        echo {params.observed_counts}, $DIFF >> {params.time_dir}
        """
