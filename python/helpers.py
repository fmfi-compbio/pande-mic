import math
from collections import defaultdict

letters = "ACGT"
l2n = {letter: num for num, letter in enumerate(letters)}


def load_fasta(filename: str):
    with open(filename) as f:
        yield from load_fasta_fd(f)


def load_fasta_fd(f):
    label, buffer = "", []
    for line in f:
        if len(line) > 0 and line[0] == ">":
            # new label
            if len(buffer) > 0:
                yield label, "".join(buffer)
            label = line.strip()[1:]
            buffer = []
        else:
            buffer.append(line.strip())
    if len(buffer) > 0:
        yield label, "".join(buffer)


def load_observed_counts(fd):
    header = fd.readline().strip()
    assert header == "position,letter,count", f"Expected 'position,letter,count' header, got '{header}' instead"
    result_raw = defaultdict(dict)
    for line in fd:
        row = line.strip().split(",")
        pos, letter, count = int(row[0])-1, row[1], int(row[2])
        result_raw[pos][letter] = count
    result = [[result_raw.get(pos, {}).get(letter, 0) for letter in "ACGT"]
              for pos in range(1 + max(result_raw.keys(), default=-1))]
    return result


def apply_to_cigartuples(fun, alignment, *args, **kwargs):
    """
    M	BAM_CMATCH	0
    I	BAM_CINS	1
    D	BAM_CDEL	2
    N	BAM_CREF_SKIP	3
    S	BAM_CSOFT_CLIP	4
    H	BAM_CHARD_CLIP	5
    P	BAM_CPAD	6
    =	BAM_CEQUAL	7
    X	BAM_CDIFF	8
    B	BAM_CBACK	9 (????!)
    """
    query_pos = 0
    reference_pos = alignment.reference_start
    for op, length in alignment.cigartuples:
        fun(op, length, reference_pos, query_pos, alignment, *args, **kwargs)
        if op == 0 or op == 7 or op == 8:
            reference_pos += length
            query_pos += length
        elif op == 1 or op == 4:
            query_pos += length
        elif op == 2 or op == 3:
            reference_pos += length
        elif op == 5 or op == 6:
            pass
        else:
            raise Exception(f"Operation code of cigar tuple is outside of range [0-8]: "
                            f"op={op}, length={length}")

