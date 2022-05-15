### PANDE-MIC
<b>P</b>ipeline <b>A</b>nalysing sequences of <b>N</b>ucleic acids <b>DE</b>signed for <b>M</b>on<b>I</b>toring of sequen<b>C</b>ing runs

---------------------------------------------------------------------------

This repository contains a monitoring tool primarily designed for monitoring of SARS-CoV-2 sequencing runs.

---------------------------------------------------------------------------

## Short overview of contents of the repository:

### config

config files

### python/main.py

creates a PipelineRunner instance and runs the pipeline.

### python/pipelinerunner.py

contains the PipelineRunner class which is a wrapper for the snakemake pipeline

the run() method in the class repeats the following steps in a loop:
1. create n batches (min<n<max) by linking files from a specified directory
2. run snakemake on new n batches 
3. merge processed batches into the summary, 
4. find variants
5. remove links

### Pipeline

Snakemake pipeline, run from PipelineRunner class (pipeline.run() called in main.py)

### rules

rules for the snakemake pipeline

### bash

helper scripts for the pipeline 


---------------------------------------------------------------------------

# Install instructions

## Install (mini)conda 
## (if you don't already have some [conda](https://docs.conda.io/en/latest/) distribution installed)

installers can be found at:
https://docs.conda.io/en/latest/miniconda.html#linux-installers

run the `.sh` installer downloaded from the website

(optional: run `conda config --set auto_activate_base false` if you don't want to auto-activate base conda environment each time you open the terminal)

## clone the pipeline repository

`git clone https://github.com/fmfi-compbio/pande-mic.git`

## create a conda environment

go inside the cloned repository:

`cd pande-mic`

run:

`conda env create -f env.yaml`

`conda activate monitoring_env`

## Install DeepNano-Blitz

full instructions can be found here: https://github.com/fmfi-compbio/deepnano-blitz

in short:

install rust:
`curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`

(you may also need to run `source $HOME/.cargo/env`)

ask for the nightly version:
`rustup default nightly-2021-01-03`

IMPORTANT!: our-pipeline-specific - we want to install blitz into the environment we have created, which already contains the other tools needed for the pipeline 

to do so,

activate monitoring env:
`conda activate monitoring_env`

clone deepnano-blitz repo:
`git clone https://github.com/fmfi-compbio/deepnano-blitz.git`

go inside the cloned dir:
`cd deepnano-blitz`

run the installer:
`python setup.py install`

## Download guppy v4.4.1

https://community.nanoporetech.com/docs/prepare/library_prep_protocols/Guppy-protocol/v/gpb_2003_v1_revac_14dec2018/barcoding-demultiplexing

extract the compressed directory, note the path where it is stored, we will need it later

## Configure the pipeline

go inside `pande-mic/config` directory

create a new directory containing files `amplicons.json`, `config.yaml`, `mut.txt`,
`ref.fasta`, `setup_guppy`, `summary.yaml`

Note: the files  `amplicons.json`, `mut.txt`, `ref.fasta`, `setup_guppy` can also be placed somewhere else (see `config.yaml`) and can have different names.

You might copy those from some of the pre-existing example configs

Now you have to edit those files.

### amplicons.json
this file contains the list of amplicons in JSON format, should have a structure similar to this:
```
{
	"name": "SARS-CoV-2 primer scheme 2000bp",
        "amplicons": [
		[30, 2079],
		[3580, 5548],
		[7092, 9123],
		[10676, 12679],
		[14176, 15978],
		[17571, 19485],
		[20883, 22996],
		[24649, 26542],
		[27914, 29790],
		[1925, 3737],
		[5394, 7255],
		[8879, 10837],
		[12519, 14328],
		[15827, 17754],
		[19310, 21241],
		[22850, 24812],
		[26386, 28351]
        ]
}
```
it should contain a name of the amplicon scheme and a list of amplicons.

### config.yaml
this is the main configuration file for the pipeline. Please copy this sample version and adjust the paths and parameters.
```
##############################
# general pipeline settings
##############################


#path to scripts directory (pipeline root dir)
scripts_dir: /<where is the clone of the repository>/pande-mic/

#where to store pipeline output
# IMPORTANT! - the path should end with / 
output_dir: /<anywhere>/  

# # of barcodes
# number of sequenced samples
barcodes: 12

# minimal number of new batches needed to run the pipeline
min_batches: 1
# maximal number of batches to be processed at one time
max_batches: 4
# number of files in a batch
batch_size: 25 

#maximal number of cores provided for the snakemake pipeline, NOTE: recomm.: max_batches =< cores
cores: 4

#whether the output directory should be cleaned before the pipeline run
# BE AWARE, setting this to True will remove any data from the directory specified as output_dir each time the application is started!
clear_annotated: False

##########################################
# settings for rules and specific scripts
##########################################

#basecalling
# IMPORTANT! - the path should end with / 
input_path: /<where are the input .fast5 files>/fast5/

#where to store temporary directories with linked files (batches to be processed)
# IMPORTANT! - the path should end with / 
batch_path: /<anywhere>/batches/

#deepnano blitz params
deepnanoblitz_path: /<path to the clone of deepnano-blitz repository>/deepnano-blitz/scripts/
blitz_beam_size: 5
blitz_threads: 1 
blitz_network_type: 48

#debarcoding
guppy_setup_path: /<path to the config directory containing the setup-guppy config file>/setup-guppy
#guppy_arrangements_files: barcode_arrs_nb96.cfg #outdated? - depends on the version of guppy
guppy_config: configuration.cfg #guppy configutarion file, it will be looked for inside the guppy dir specified in setup-guppy
guppy_barcode_kits: EXP-NBD196 #barcode kits used
guppy_threads: 1 #recommended value is 1

#alignment
#the reference genome
reference_genome: /<anywhere>/ref.fasta

#base counting script
alignment_low_cutoff: 50 #coverage below this value will be considered low

#find SNPs
coverage_threshold: 50 #coverage below this value will be considered low
coverage_fraction: 0.5 #fraction of mutated bases that need to be at a specific position compared to the coverage at this position to denote a SNP

#variant calling
mut_file: /<anywhere>/mut.txt #path to the configuration file containing definitions of SNPs for the variants of the virus
variant_calling_threshold: 50 #coverage below this value will be considered low

```

### mut.txt
configuration file for variant calling

The file defines the variants. 

This file specifies the variants (of SARS-CoV-2 in our case) to look for and mutations that are specific for a variant.
Each line starts with a label of a variant at the beginning, 
followed by exactly one space and then a number of mutations that we want to match so that we can say that a barcode corresponds to this variant.
Then there are mutations that are typical for a variant separated by spaces.
Lines starting with `#` are comments and are ignored when parsing the file.

#### Example
```
UK 5 C3267T C5388A ... G28280C A28281T T28282A
```
this line specifies a variant that should be displayed as "UK", 

the line starts with "UK", which is our label for this variant. 

the label is followed by a number, 5, which says that "if at least 5 of the following mutations are present in the sample, classify the sample as this variant"

the number is followed by mutations (for example C is changed to T at the position 3267 mapped to the reference genome) that are typical for this variant, separated by spaces.

#### Tree-like structure
You can also provide other variants in a tree-like structure, using syntax `start_sub` and `end_sub` in separate lines:
```
#UK variant
UK 5 C3267T ... T28282A

#more specific variants for UK
start_sub
UK-subvariant_1 1 A17615G

#subvariants for UK-subvariant_1
start_sub
.
.
UK-subvariant_1-Poland 4 C5301T C7420T C9693T G23811T C25350T C28677T G29348T
UK-subvariant_1-Gambia 3 T6916C T18083C G22132A C23929T
end_sub

end_sub

#CZ variant
CZ 3 G12988T G15598A G18028T T24910C T26972C 
```

This means that we will look for the UK variant, and if we will find at least 5 mutations from the list provided in the UK line, we will also continue searching for other more specific variants.

For example, if the UK variant is matched, we will check whether there is also a mutation in position A17615G, 

if it is, then we will check if there are some of the mutations specified in its subsection - UK-subvariant_1-Poland or UK-subvariant_1-Gambia. 

We will stop searching at the point when there are no more subsections specified or when less than the required count of mutations was found for a sample.

We will look for the CZ variant too. This one has no subvariants specified in this example file, so no further search would be made.

### ref.fasta 
the reference genome in FASTA format

```
>MN908947.3
ATTAAAGGTTTATACCTTCCCAGGTAACAAACCAACCAACTTTCGATCTCTTGTAGATCTGTTCTCT.....
```

**Important note:** for reference genomes that are split into multiple contigs, you can use the the [`multiref_to_one.py`](../python/multiref_to_one.py) script, as *this version of the pipeline does not support genomes that have multiple contigs/chromosomes*. It will create a new .fasta file with all the contigs concateneted into one long string, where the contigs will be separated by regions of 100 Ns to avoid alignemnts in between the contigs. It will also create an `amplicons.json` file containing the start and end positions of the contigs that can be used for marking the positions in the Flask application (although the name of the file is misleading in this case, as the file is primarily used for another purpose - to mark the amplicons in the covarage plot). 

### setup-guppy
guppy setup file. This file is there to configure the guppy path, set the LD_LIBRARY_PATH, or anything that you need to set up to run guppy on your machine. The file should be written in bash and is executed before the guppy debarcoder command
an example:
```
export GUPPYDIR=/<anywhere>/<where_is_guppy>

export LD_LIBRARY_PATH=$GUPPYDIR/lib:$LD_LIBRARY_PATH

#or this, if the above does not work: export LD_LIBRARY_PATH=$GUPPYDIR/lib:${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH} 

export PATH=$GUPPYDIR/bin:$PATH
```
### summary.yaml
list of summary subdirectories (recommended to leave as is, unless you want to extend the pipeline)
```
summary_subdirs:
  - basecalled
  - debarcoded
  - aligned
  - variants
  - coverage_per_base 
  - SNPs
  - barcode_summary
```

### clone the repository with the Flask part of the tool (Dashboard)
https://github.com/fmfi-compbio/pande-mic-dashboard

follow the instructions in the repository

--------------------------------------------------------------------------

# Docs

## Run

First, you have to install and configure the tool and its dependencies. If you don't already have it done, please follow the instructions above.

To start the analysis, go inside the cloned repository and run this command:

`python -u ./python/main.py --config_dir <path to the pipeline directory>/configs/<your configuration directory>/`

## Short overview of the scripts

### main.py

The main script. It loads the main configuration file and starts the analysis.

```
usage: main.py [-h] -conf CONFIG_DIR

optional arguments:
  -h, --help            show this help message and exit
  -conf CONFIG_DIR, --config_dir CONFIG_DIR
                        path to the config dir
```

### PipelineRunner class:  

A class instance of which is created in the main.py file. The purpose of this class is to create the batches and run snakemake in a loop.

short overview of its essential methods:

`init()`: set params, [clear annotated], print init. values, create summary dir and subdirs and empty .csv files  
-    `create_config_copy()`: creates a copy of the config directory inside the output directory
-    `create_dirs()`: creates the directories and files structure for the output files of the pipeline inside the output directory
-    `load_processed()`: loads the list of files that are already processed, counts and sets the number of iterations and processed batches


`run()`: while True: create batches, run snakemake, clean batches, merge results to the summary  
-    `create_batches()`: find unprocessed (compare listdir with the array of previously batched files), wait till we have enough files to create a batch, create batch(es) - link files (os.symlink), add files to the array of batched files  
-    `run_snakemake()`: run snakemake (os.system(snakemake [params])), uses scripts_dir/Pipeline, scripts_dir/rules  
-    `clean_batches()`: remove processed batch folders with symlinks  
-    `write_batches()`: write lists of processed files for each processed batch into processed.csv  

### PipelineState class (and subclasses):  
used for handling keyboard interrupts in PipelineRunner  
(state d.p.)  

### merge_sum.py

a helper script/function for merging two .csv files. supports "aggregation" over one column - "sum()" applied to other columns

supported arguments:

```
   -f1 FIRST_FILE_NAME, --first_file_name FIRST_FILE_NAME
                        first file to merge/or file names of multiple files with same
                        structure separated by comma
  -f2 SECOND_FILE_NAME, --second_file_name SECOND_FILE_NAME
                        second file to merge
  -cf COUNT_FIRST, --count_first COUNT_FIRST
                        columns to be summed in first file seperated by ,
  -gpf GROUP_BY_FIRST, --group_by_first GROUP_BY_FIRST
                        column to use for grupping in first file or -1
  -hf HAS_HEADER_FIRST, --has_header_first HAS_HEADER_FIRST
                        1 if first file has a header, 0 otherwise
  -cs COUNT_SECOND, --count_second COUNT_SECOND
                        columns to be summed in second file seperated by ,
  -gps GROUP_BY_SECOND, --group_by_second GROUP_BY_SECOND
                        column to use for grupping in second file or -1
  -hs HAS_HEADER_SECOND, --has_header_second HAS_HEADER_SECOND
                        1 if second file has a header, 0 otherwise
  -gs GROUP_START, --group_start GROUP_START
                        whether the output should start with group (1) or not (0)
  -o OUT, --out OUT     output file
```

function ` merge(group_start, count_first, count_second, has_header_first, has_header_second, group_by_first, group_by_second, fnames, fname2, output)`:
params:
- `group_start`: whether the output should start with group (1) or not (0)
- `count_first`: array of columns to be summed in first file (0-based)
- `count_second`: array of columns to be summed in second file (0-based)
- `has_header_first`: 1 if first file has a header, 0 otherwise
- `has_header_second`: 1 if second file has a header, 0 otherwise
- `group_by_first`: column to use for grupping in first file or -1 if none
- `group_by_second`: column to use for grupping in second file or -1 if none
- `fnames`: list of files (they sholud have the same structure) to be merged
- `fname2`: second file to merge
- `output`: output file

## Pipeline
    
`<pande-mic repository>/Pipeline`, config in `<pande-mic repository>/configs/<some config dir>/config.yaml` (<pande-mic repository> should be specified as a parameter for the main.py script),  

### Pipeline (file):  
has 3 phases:

for all batches in `batch_path` (form `config.yaml`), `samples` = barcode01,..., barcodeXY (XY = barcodes from `config.yaml`) create SNPs = output_dir/batch/SNPs/sample.csv (output dir form `config.yaml`)  
at the end of the iteartion,`{batch}.done` files in `batch_done` directory are created for each processed batch

for all batches that were marked as summarized in the previous iteration (do the `{batch}.done` files exist for them) create `{batch}.summarized` file in `batches_done` directory - this forces the run of the summarization process for each of the batches processed in the previous iteration

variant calling from the summary directory

### rules:  
 There are 3 directories containing the rules for the pipeline
 - the `batches` directory contains the rules that need to be done for each batch before summarization
 - the `summary` directory contains the rules for summarization of the batches
 - the `from_summary` directory contains the rules for tasks that should be done after the summarization

#### `batches`

#### 1. rules/batches/basecalling.smk:  
`fast5_dir = config["batch_path"]+"{batch}" ` -> `fastq = config["output_dir"]+"{batch}/basecalled/{batch}.fastq"  `  
dependency: deepnano blitz  
bash: count_reads_and_bases.sh  

#### 2. rules/batches/debarcoding.smk:  
` fastq = config["output_dir"]+"{batch}/basecalled/{batch}.fastq" ` -> `out = directory(config["output_dir"]+"{batch}/debarcoded/{batch}")  `  
dependency: guppy  v4.4.1
bash: count_reads_and_bases.sh  

#### 3. rules/batches/debarcoding_summary.smk:   
` debarcoding_out = config["output_dir"]+"{batch}/debarcoded/{batch}" ` -> `barcode_summary_files = [config["output_dir"]+"{batch}"+barcode for barcode in expand("/barcode_summary/{barcode}.fastq",barcode=barcodes)]+[config["output_dir"]+"{batch}/barcode_summary/unclassified.fastq"]`   
bash: concat_barcodes.sh  

#### 4. rules/batches/alignment.smk:   
` fastq = config["output_dir"]+"{batch}/barcode_summary/{sample}.fastq" ` -> `bam = config["output_dir"]+"{batch}/aligned/{sample}.bam" `,  
dependency: minimap2, samtools  

#### 5. rules/batches/count_bases_in_alignment.smk:  
` bam = config["output_dir"]+"{batch}/aligned/{sample}.bam" ` -> `observed_counts = config["output_dir"]+"{batch}/coverage_per_base/{sample}.csv"  `  
dependency: python: count_observed_counts.py  

#### 6. rules/batches/find_SNPs.smk:  
`observed_counts = config["output_dir"]+"{batch}/"+"coverage_per_base/{sample}.csv"` -> `SNPs = config["output_dir"]+"{batch}/"+"SNPs/{sample}.csv"`  
dependency: python: find_SNPs_for_csv.py   
    

### output files for a batch:  

#### 1. rules/basecalling.smk:  

directory `{batch}/basecalled` , containing basecalled (.fastq) file (1 for all .fast5 files in a batch together) -> `{batch}/basecalled/{batch}.fastq` 

`{batch}/basecalled/count.csv` -> file path, num of reads, num of bases  
(one line)  

#### 2. rules/debarcoding.smk:  

directory `{batch}/debarcoded/{batch}` containing up to <num of barcodes +1> directories (one for each barcode (`barcodeXY`) + `unclassified`) with debarcoded `.fastq` files  

`barcoding_summary.txt` (guppy), ignored ... maybe we can use it somehow  

`{batch}/debarcoded/count.csv` (one line for each .fastq -> file path, num of reads, num of bases, barcode)  

#### 3. rules/debarcoding_summary.smk:   

directory `{batch}/barcode_summary` containing `barcodeXY.fastq` (for each barcode), `unclassified.fastq` - conctenated `.fastq` files from guppy output (from `{batch}/debarcoded/{batch}` + empty `.fastq` files for barcodes that are not in guppy output)  

`{batch}/barcode_summary/summary.csv` (one line for each `.fastq` -> file path, num of reads, num of bases, barcode)  

#### 4. rules/alignment.smk:  

directory `{batch}/aligned` containing `barcodeXY.bam`, `barcodeXY.bam.bai` for each barcode, `unlassified.bam`, `unclassified.bam.bai`  

#### 5. rules/count_bases_in_alignment.smk:  

directory `{batch}/coverage_per_base` containig `barcodeXY.csv` for each barcode, `unclassified.csv` -   
containting lines [position,A,C,G,T] for each position in the reference genome (counts of bases mapped to the reference)  

#### 6. rules/find_SNPs.smk:  

directory `{batch}/SNPs`, containing `barcodeXY.csv`, for each barcode, `unclassified.csv` -   
containting lines [snp,same_as_ref,mutated] - snp, num of bases same as ref, num of bases same as mutation  
 

\+ log directory (`<output directory>/{batch}/log/{align,basecalling,concat_barcodes,count_bases,debarcoding,find_SNPs}/`)   

\+ timer files in timers directory (`<output_directory>/timers/...)  


## Summary

generated using `summary` and `from_summary` rules of the Snakemake pipeline

`<output directory>/processed.csv` - processed batches (with lists of files), that were successfully merged into the summary and deleted

### summary directory:
     
This directory can be used as the input for the [pande-mic dashboard](https://github.com/fmfi-compbio/pande-mic-dashboard
)

`aligned/mapped.csv`: barcode, num of mapped reads
`basecalled/count.csv`: num of reads, num of bases  
`barcode_summary/summary.csv`: num of reads, num of bases, barcode  
`coverage_per_base/{barcodeXY, unlassified}.csv` [position, A,C,G,T]  
`SNPs/{barcodeXY, unlassified}.csv` [snp, same_as_ref, mutated]  
`variants/{barcode, unclassified}.json`   
   
    [{
        "name": <variant name>, 
        "mutations":
            [
                {"position": 3267, 
                "from": "C", 
                "to": "T", 
                "same_as_reference": 44, 
                "same_as_mutation": 220},
                {..}.{..}
            ],
        "subs": [{"name:"... }]
    }]


