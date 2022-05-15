
#for fasta
#echo $1
#echo $(( $( cat $1 | wc -l )/2 ))
#cat $1 | paste - - | cut -f 2 | tr -d '\n' | wc -c

#fastq
echo $1,$(( $( cat $1 | wc -l )/4 )),$(cat $1 | paste - - - - | cut -f 2 | tr -d '\n' | wc -c)

