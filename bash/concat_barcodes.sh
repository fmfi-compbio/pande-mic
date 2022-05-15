# param $2 = dir of dirs of barcodes
# param $3 = output dir
# param $4 = scripts dir
if test $1 -gt 0
then

for i in $(eval echo {01..$1});
do
        for f in $2/barcode$i/*; do cat $f >> $3/barcode$i.fastq; done
        echo $(eval $4/bash/count_reads_and_bases.sh $3/barcode$i.fastq),barcode$i >> $3/summary.csv;
done;

fi

#cat $2/*/unclassified/* >> $3/unclassified.fastq
for f in $2/unclassified/*; do cat $f >> $3/unclassified.fastq; done
echo $(eval $4/bash/count_reads_and_bases.sh $3/unclassified.fastq),unclassified >> $3/summary.csv