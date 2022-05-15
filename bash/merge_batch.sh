# $1 path to output dir
# $2 batch folder name
# $3 # of barcodes

#echo "merging basecalled/count.csv to summary"
python /projects/monitoring/pipeline/scripts/v2/python/sum.py --first_file_name $1$2/basecalled/count.csv --second_file_name $1summary/basecalled/count.csv --count_first 1,2 --group_by_first -1 --has_header_first 0 --count_second 0,1 --group_by_second -1 --has_header_second 0 --group_start 0 --out $1summary/basecalled/count.csv
#echo "merging barcode_summary/summary.csv to summary"
python /projects/monitoring/pipeline/scripts/v2/python/sum.py --first_file_name $1$2/barcode_summary/summary.csv --second_file_name $1summary/barcode_summary/summary.csv --count_first 1,2 --group_by_first 3 --has_header_first 0 --count_second 0,1 --group_by_second 2 --has_header_second 0 --group_start 0 --out $1summary/barcode_summary/summary.csv
#python /projects/monitoring/pipeline/scripts/v2/python/sum.py --first_file_name $1$2/filtered/count.csv --second_file_name $1/summary/filtered/count.csv --count_first 1,2 --group_by_first 3 --has_header_first 0 --count_second 0,1 --group_by_second 2 --has_header_second 0 --group_start 0 > $1/summary/filtered/count.csv



for i in $(eval echo {01..$3});
do
        #echo "merging coverage_per_base/barcode$i.csv to summary"
        python /projects/monitoring/pipeline/scripts/v2/python/sum.py --first_file_name $1$2/coverage_per_base/barcode$i.csv --second_file_name $1summary/coverage_per_base/barcode$i.csv --count_first 1,2,3,4 --group_by_first 0 --has_header_first 1 --count_second 1,2,3,4 --group_by_second 0 --has_header_second 1 --group_start 1 --out $1/summary/coverage_per_base/barcode$i.csv ;
        #echo "merging SNPs/barcode$i.csv to summary"
        python /projects/monitoring/pipeline/scripts/v2/python/sum.py --first_file_name $1$2/SNPs/barcode$i.csv --second_file_name $1summary/SNPs/barcode$i.csv --count_first 1,2 --group_by_first 0 --has_header_first 1 --count_second 1,2 --group_by_second 0 --has_header_second 1 --group_start 1 --out $1summary/SNPs/barcode$i.csv ;
        echo "calculating variants for barcode$i ..."
        python /projects/monitoring/pipeline/scripts/v2/python/variant_calling_from_counts.py $1/summary/coverage_per_base/barcode$i.csv /projects/monitoring/pipeline/scripts/v2/config/ref.fasta /projects/monitoring/pipeline/scripts/v2/config/mut.txt --threshold 1 --output $1summary/variants/barcode$i.json ;
done;

#echo "merging coverage_per_base/unclassified.csv to summary"
python /projects/monitoring/pipeline/scripts/v2/python/sum.py --first_file_name $1$2/coverage_per_base/unclassified.csv --second_file_name $1summary/coverage_per_base/unclassified.csv --count_first 1,2,3,4 --group_by_first 0 --has_header_first 1 --count_second 1,2,3,4 --group_by_second 0 --has_header_second 1 --group_start 1 --out $1/summary/coverage_per_base/unclassified.csv ;
#echo "merging SNPs/unclassified.csv to summary"
python /projects/monitoring/pipeline/scripts/v2/python/sum.py --first_file_name $1$2/SNPs/unclassified.csv --second_file_name $1summary/SNPs/unclassified.csv --count_first 1,2 --group_by_first 0 --has_header_first 1 --count_second 1,2 --group_by_second 0 --has_header_second 1 --group_start 1 --out $1summary/SNPs/unclassified.csv ;
#echo "calculating variants for unclassified"
python /projects/monitoring/pipeline/scripts/v2/python/variant_calling_from_counts.py $1summary/coverage_per_base/unclassified.csv /projects/monitoring/pipeline/scripts/v2/config/ref.fasta /projects/monitoring/pipeline/scripts/v2/config/mut.txt --threshold 1 --output $1summary/variants/unclassified.json


