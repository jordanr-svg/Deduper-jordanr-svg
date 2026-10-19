# Deduper Pseudocode
Problem: There is duplicate reads in this SAM file that need to be found and removed.

Goal: Discover duplicates through the POS, QNAME, and CIGAR string. Output the first encountered read if duplicates are found. print as you go to not load everything into memory. Input is a sorted SAM file.

## Pseudocode

### Functions:

function is_UMI(current_read list):

    Input: Temp read list

    Output: True or False

    ''' takes in temp read list, looks at first item (QNAME string) uses python regex to identify UMI at the end of the string. If UMI detected, then check UMI is in the UMI list, if UMI is in UMI list then TRUE, if not FALSE. If no UMI was detected return 404 '''
        QNAME = curr_read[0]
        chrome = int(curr_read[2])
        regex = [A-Z]{8}$ to get UMI

    EX Input:
    NS500451:154:HWKTMBGXX:1:11101:15364:1139:GAACAGGT

    EX Return: TRUE

function five_end(read list):
   
    Input: read list
    output: 5' position and read length

    '''Takes in the read list (previous or current) and calculates the 5' end based off of cigar string (soft clipping) and left most read position'''


        POS = curr_read[3]
        CIGAR = curr_read[5]

    EX Input: [NS500451:154:HWKTMBGXX:1:11101:94095:71756:AACGCCAT, 0, 2, 76875970, 36, 3S15M470N56M,*,0,0, ...]
    EX Return:76875973
### Argparse

args:
file name, umi file name, output file name, help message

### Read in files and parse

- initialize empty UMI list

- initialize empty curr_read list
- initialize empty prev_read list


read in UMI file

- for each line in UMI 
- strip line and save as temp UMI variable
- file append UMI list with UMI variable


Read in input sorted SAM file one line (read) at a time. 

- For each line that does NOT start with an @ split and strip the line and save in a temporary string to evaluate each item (SAM column). 
- QNAME = curr_read[0]
- chrome = int(curr_read[2])
- pos = curr_read[3]
- CIGAR = curr_read[5]

if prev_read list is empty:

    reasign curr_list to prev_list
    prev_chrom = chrom
    prev_pos = five_end(curr_list)
    continue
else:
    
    call UMI function

    if is_UMI == TRUE:
        print the full read to the output file
    elif is_UMI == 404:
        UMI was not detected
        call five_end function
        if the prev_pos does not equal the curr_pos then
        print the full read to the output file
    elif is_UMI == FALSE:
        No UMI was found
        continue

print the full current read to the output file (making sure last thing in string gets output)