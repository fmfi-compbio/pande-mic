# param $2 = dir of dirs of barcodes
# param $3 = output dir
# param $4 = scripts dir
if test $1 -gt 0
then

for i in $(eval echo {001..$1});
do
        for f in $2/run$i/*; do cat $f >> $3/run$i.fastq; done
        echo $(eval $4/bash/count_reads_and_bases.sh $3/run$i.fastq),run$i >> $3/summary.csv;
done;

fi

