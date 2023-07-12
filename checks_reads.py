 #! /usr/bin/env python3

#########################################################################
# -> check if reads are fastq files					#
# -> unzip if needed							#
# -> rename the files to save only the sample name & the read number	#
# -> combine reads if came from next seq				#
#########################################################################

import os
import sys

def createDir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


def unzipReads(dir):
    cmd = 'echo Unzipping... && gunzip ' + dir + '/*.gz'
    os.system(cmd)


def combineFiles(dir):
    print("Combining files")
    cmd ='cd ' + dir + ';'
    cmd+= 'ls ' + dir + ' | egrep "_L00" | '
    cmd+= 'awk \'BEGIN{FS=OFS="_"}{ print $1, $2 } \' | sort | uniq | '
    cmd+= 'while    read    line;do cat ' + dir + '/${line}_*_R1*.fastq > ${line}_R1.fastq && cat ' + dir + '/${line}_*_R2*.fastq > ${line}_R2.fastq; done;'
    cmd+= 'cd ..'
    os.system(cmd)

def renameFile(dir):
    for file in os.listdir(dir):
        if 'R1' in file:
            read = 'R1'
        else:
            read = 'R2'

        name = f"{file.split('_')[0]}_{read}.fastq"
        cmd = f'mv {os.path.join(dir, file)} {os.path.join(dir, name)} 2>/dev/null'
        print(name)
        os.system(cmd)  

def isPaired(list1, list2):
    if len(list1) != len(list2):
        print(len(list1), len(list2))
        return False

    count = 0
    for i in range(len(list1)):
        for j in range(len(list2)):
            if list1[i] in list2[j]:
                count += 1
                break

    if count == len(list1):
        return True
    else:
        return False

def exitProgram(message=""):
    sys.exit(message)


try:
    GENOME_DIR = sys.argv[1]
except IndexError:
    exitProgram("You need to add your genomes directory path in the command: python3 checks_reads.py [path]")
   

genomes = os.listdir(GENOME_DIR)

for genome in genomes:
    if not ('.fq' in genome or '.fastq' in genome):
        exitProgram("The reads must have '.fq' or '.fastq' extension")
    if '.gz' in genome:
        unzipReads(GENOME_DIR)
        break

# Check if reads from NextSeq
isMoreThanTwoReads = [s for s in genomes if "_L002" in s or "_L003" in s or "_L004" in s]

if(len(isMoreThanTwoReads) > 0):
    combineFiles(GENOME_DIR);

renameFile(GENOME_DIR)

R1 = [s for s in genomes if "R1" in s]
samples = [each.split('_')[0] for each in R1]
R2 = [s for s in genomes if "R2" in s]


if (isPaired(samples, R2) == False):
    exitProgram("The reads are not paired.")
