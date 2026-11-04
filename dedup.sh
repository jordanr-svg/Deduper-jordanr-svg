#!/bin/bash
#SBATCH --account=bgmp
#SBATCH --partition=bgmp
#SBATCH --cpus-per-task=8
#SBATCH --mem=16GB
#SBATCH--job-name=deduperRodgers
/usr/bin/time -v ./dedup.py -f /projects/bgmp/jordanro/bioinfo/Bi624/Deduper-jordanr-svg/sorted_uniq_align.sam -o /projects/bgmp/jordanro/bioinfo/Bi624/Deduper-jordanr-svg/dedup_output.sam -u STL96.txt