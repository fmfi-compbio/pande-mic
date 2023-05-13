rule debarcoding_summary:
    input:
        debarcoding_out = config["output_dir"]+"{batch}/debarcoded/",
    log: 
        concat_log = config["output_dir"]+"{batch}/log/concat_barcodes/concat.log",
        concat_err = config["output_dir"]+"{batch}/log/concat_barcodes/concat.err",
    params:
        barcode_summary_dir = config["output_dir"]+"{batch}/barcode_summary/",
        barcodes = config["barcodes"],
        out_dir = config["output_dir"]+"{batch}",
        fast5_path = config["batch_path"]+"{batch}",
        scripts_dir = config["scripts_dir"],
        time_dir = config["output_dir"]+"timers/barcode_summary/{batch}_debarcoding_summary.txt"
    output:
        barcode_summary_files = [config["output_dir"]+"{batch}"+barcode for barcode in expand("/barcode_summary/{barcode}.fastq",barcode=SAMPLES)]
    shell:
        """
        START=$(date +%s.%N)
        mkdir -p {params.barcode_summary_dir}
        {params.scripts_dir}bash/concat_barcodes.sh {params.barcodes} {input.debarcoding_out} {params.barcode_summary_dir} {params.scripts_dir} > {log.concat_log} 2> {log.concat_err}
        END=$(date +%s.%N)
        DIFF=$(echo "$END - $START" | bc)
        echo {input.debarcoding_out}, $DIFF >> {params.time_dir}
        """
