rule summarize_batch:
    wildcard_constraints:
        batch="batch[0-9]*"
    input:
        observed_counts = expand(config["output_dir"]+"{batch}/coverage_per_base/{sample}.csv.summarized", sample=SAMPLES, allow_missing=True),
        basecalling = config["output_dir"]+"{batch}/basecalled/count.csv.summarized",
        barcode_summary = config["output_dir"]+"{batch}/barcode_summary/summary.csv.summarized",
        aligned = config["output_dir"]+"{batch}/aligned/mapped.csv.summarized",
        SNPs = expand(config["output_dir"]+"{batch}/SNPs/{sample}.csv.summarized", sample=SAMPLES, allow_missing=True)
        # 1 riadok + rule pre kazdy sumarizovany typ suboru
    output:
        batch_summarized = os.path.join(config["output_dir"],"batches_done")+"/{batch}.summarized"
    priority: 10 #execute this rule first
    shell:
        """
        touch {output.batch_summarized}
        """