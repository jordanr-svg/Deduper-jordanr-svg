#!/usr/bin/env python

##########################################
#### Deduplicating fastq reads
## DUE: 11/2/2026
import argparse
import re

### arguments for oneline fasta function

def my_args():
    parser = argparse.ArgumentParser(description="This script removes duplicate reads from sorted sam file of single-end reads, arguments are to handle the all input files and 1 output file. Output is a properly formatted sam file")
    parser.add_argument("-f","--file", type = str, required = True, help = "Input file to be deduplicated, should be a sorted sam file")
    parser.add_argument("-o","--outfile",type = str, required = True, help ="Output file, should be SAM")
    parser.add_argument("-u","--umi",type = str, required = True, help = "File with all known UMIs")
    return parser.parse_args()
args = my_args()

umi = args.umi
file = args.file
out = args.outfile
umi_dict:dict = {}

uniiq_reads = 0
duplicates_removed = 0

### read in file with umis, put them in dictionary
with open(umi, "r") as um_file:
    while True:
        line = um_file.readline().strip()
        try:
            if line == "":
                break
        except:
            continue
        umi_dict[line] = 0



def umi_present(qname:str )-> str:
    '''Function takes in qname string and checks if umi is in dictionary. Returns {UMI} if it in dictionary, returns False if not.'''
    umi_list = qname.split(":")
    umi = umi_list[7]
    if umi in umi_dict:
        flag = umi
    else:
       flag = False
    return flag

def strand_direction(flag:int) -> str:
    '''Takes bit 16 and outputs strand direction based on value'''
    if (flag & 16) == 16:
        dir_strand = "neg"
    else:
        dir_strand = "plus"
    return dir_strand


def five_prime_pos(left_pos:int, cigar:str, strand:str) -> int:
    '''Calculates true five prime position from cigar string, strand direction, and left most position'''
### add all number in cigar string except I (.) in regex, subtract 1 -> for negative strand
    cigar_list = re.findall(r"(\d*)(.{1})", cigar)
    if strand == "neg": ### need to add soft clipping to end site
        sum = 0
        for num, letter in cigar_list:
            if letter == "I" or letter == "S":
                continue
            else:
                sum += int(num)
        num,letter = cigar_list[-1]
        if letter == "S":
            sum += int(num)
        final_pos = left_pos + int(sum) - 1
        # else:
        #     final_pos = left_pos + int(sum)
    elif strand == "plus": ### need to subtract soft clipping from start site
        num,letter = cigar_list[0]
        if letter == "S":
            final_pos = left_pos - int(num)
        else:
            final_pos = left_pos

    return final_pos

bad_umi_count = 0
prev_chrom = 0


#### initializing dictionaries
### Empty set when moving to next chromosome,
#  chromosome dictionary will keep track of how many reads are output for each chromosome

unique_reads = set()
chrom_dict:dict = {}
duplicate_dict:dict = {}
umi_count:dict = {}
header_lines = 0

with open(file, "r") as sam: #open sam file
    with open(out, "w") as out: # open output file
        for line in sam: # for every line in the file
            if line.startswith("@"): # if the line is not a header line
                header_lines += 1
                out.write(line)
            else:
                curr_read = line.strip().split() # split line into list of strings
                qname = str(curr_read[0]) # take the object in the first index as the ID
                #print(qname)
                chrom = curr_read[2] # take the object in the second index as the flag (cast as integer)
                #print(chrom)
                left_pos = int(curr_read[3])
                cigar = str(curr_read[5]) ### col 6 is cigar string
                strand_flag = int(curr_read[1]) ### col 5 is bitwise flag
                #print(f"chrom: {chrom}")
                #print(f"qname: {qname}")


                if prev_chrom == 0: ### keeping track of chromosome
                    prev_chrom = chrom

                if prev_chrom != chrom: ### resetting dictionaries when moving to new chromosome
                    unique_reads = set()
                    prev_chrom = 0
                if umi_present(qname) == False: ### if not a valid umi move on (we do not want to output those)
                    bad_umi_count += 1 ### keeping track of not valid umis
                    continue
                else:
                    umi = umi_present(qname)
                    try:
                        umi_count[umi] += 1
                    except KeyError:
                        umi_count[umi] = 1

                    strand_dir = strand_direction(strand_flag)
                    position = five_prime_pos(left_pos,cigar,strand_dir)
                    #print(f"position: {position}")
                    read = (position,umi,strand_dir,chrom)

                    if read in unique_reads: ### check if reads are unique
                        duplicates_removed += 1
                    else:
                        unique_reads.add(read) ### keep track of reads
                        try: ### trying to incriment chromosome tracker
                            chrom_dict[chrom] += 1
                        except KeyError: ### add chrom to dictionary with count 1
                            chrom_dict[chrom] = 1
                        uniiq_reads += 1 ### count total unique reads
                        out.write(line)


with open("dedup_statsOut.txt","w") as stats:
#print(f"strand_direction: {strand_direction(strand_flag)}")

    #stats.write(f"Unique reads for each chromosome: {chrom_dict}\n")
    #stats.write(f"Reads per UMI: {umi_count}\n")
    stats.write(f"Unique reads for each chromosome:\n")
    for chrom in chrom_dict:
        stats.write(f"{chrom}: {chrom_dict[chrom]}\n")
    stats.write(f"Bad UMI counts: {bad_umi_count}\n")
    stats.write(f"Header lines: {header_lines}\n")
    stats.write(f"uniq reads: {uniiq_reads}\n")
    stats.write(f"duplicates: {duplicates_removed}")