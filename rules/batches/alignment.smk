rule alignment:
    wildcard_constraints:
        batch="batch[0-9]*"
    input:
        #fastq = config["output_dir"]+"{batch}/batch_summary/{sample}.fastq",
        #fastq = config["output_dir"]+"{batch}/barcode_summary/",
        fastq = config["output_dir"]+"{batch}/barcode_summary/{sample}.fastq",
        reference = config["reference_genome"]
    log:
        err = config["output_dir"]+"{batch}/log/align/{sample}__minimap2.err"
    params:
        time_dir = config["output_dir"]+"timers/aligned/{batch}_alignment.txt",
        sample = "{batch},{sample}",
        mapped = config["output_dir"]+"{batch}/aligned/mapped.csv"
    output:
        bam = config["output_dir"]+"{batch}/aligned/{sample}.bam",
        bai = config["output_dir"]+"{batch}/aligned/{sample}.bam.bai",
    shell:
        """
        START=$(date +%s.%N)
        minimap2 -t 2 -x map-ont -a {input.reference:q} {input.fastq:q} 2> {log.err} | samtools view -S -b -o - | \
        samtools sort - -o {output.bam:q} && samtools index {output.bam:q}
        MAPPED=$(samtools view -c -F 2308 {output.bam:q})
        echo {params.sample}, $MAPPED >> {params.mapped:q}
        END=$(date +%s.%N)
        DIFF=$(echo "$END - $START" | bc)
        echo {input.fastq}, $DIFF >> {params.time_dir}
        """
