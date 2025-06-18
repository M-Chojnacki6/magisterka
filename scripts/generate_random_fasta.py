from numpy.random import choice
import random
import argparse
import re
import os
from typing import List


def parse_args():

	parser = argparse.ArgumentParser(description="""Script generating chosen number n*1000 of random nucleotid sequences, each 
		sequence will be in saved to different .fasta file. """,formatter_class=argparse.RawDescriptionHelpFormatter)

	parser.add_argument('n',metavar='N', nargs=1,  help="""Script will generat n * 1000.""",default=os.getcwd(),type=int)

	parser.add_argument('d',metavar='DIR', nargs=1,  help="""Path to output directory; default: current directory.""",default=os.getcwd())

	parser.add_argument('-CG', nargs=1, help="""The percentage of C (cytosine ) and G (guanine) bases in generated sequences; 
should be 0 < CG < 1; default: 0.5""",type=float,default=0.5)

	parser.add_argument('-chr', nargs = 24,help="""The distribution of number of chromosome, where sequenceswill be located;
it should sum to 1000; default distribution:
chr1:  97, chr2:  76, chr3:  60, chr4:  40, chr5:  51, chr6:  47, chr7:  54, chr8:  41
chr9:  40, chr10: 40, chr11: 56, chr12: 52, chr13: 22, chr14: 33, chr15: 33, chr16: 40
chr17: 52, chr18: 18, chr19: 50, chr20: 28, chr21: 14, chr22: 22, chrX:  29, chrY:  5""",
default=[97,76,60,40,51,47,54,41,40,40,56,52,22,33,33,40,52,18,50,28,14,22,29,5])
	parser.add_argument('-l',metavar='L', nargs=1,  help="""Length of the qenerated sequences. Default: 2000""",default=2000,type=int)



	args = parser.parse_args()

	n=None
	if args.n is None:
		print("Provide number of n * 1000 sequences to generate\n")
	elif isinstance(args.n, int):
		n=args.n
	else:
		n=args.n[0]

	out=None
	if isinstance(args.d, list):
		if os.path.isdir(args.d[0]):
			out=os.path.abspath(args.d[0])
		else:
			print("provided path: {args.out[0]} does not exist; changing to current directory")
			out= os.getcwd()
	else:
		print("data path set to current directory")
		out=args.d

	if isinstance(args.CG, float):
		CG=args.CG
	else:
		CG=args.CG[0]
		if CG<=0 or CG>=1:
			CG=0.5
	chrom=args.chr
	if isinstance(chrom[0], str):
		for i in range(24):
			chrom[i]=int(chrom[i])
	if sum(chrom)!=1000:
		print(f"distribution sequences over chromosomes doasn't sum up to 1000; changing to default values")
		chrom=[97,76,60,40,51,47,54,41,40,40,56,52,22,33,33,40,52,18,50,28,14,22,29,5]

	if isinstance(args.l, int):
		l=args.l
	else:
		l=args.l[0]
		if l<100:
			l=2000
	if n and out:
		return [n, out,CG, chrom,l]
	else:
		return None



def generate_fasta_file(file_path, chr_number, sequence_length,weights):
	nucleotides = ['A', 'T', 'C', 'G']
	if chr_number==23:
		chr_number="X"
	elif chr_number==24:
		chr_number="Y"
	random_number = random.randint(10000000, 999999999)
	with open(os.path.join(file_path,f"{chr_number}:{random_number}.fasta"), 'w') as file:
		header = f"> chr{chr_number} + {random_number} random"
		sequence = ''.join(choice(nucleotides,p=weights) for _ in range(sequence_length))

		file.write(f"{header}\n{sequence}\n")




def main():
	inputs=parse_args()
	
	if inputs:
		print(f"{' '*6}> Run generate_random_fasta.py < \n\n{'#'*20}START{'#'*20}")
		print(f"\nn:\t\t\t\t{inputs[0]}\nOutput directory:\t\t{inputs[1]}\n% CG:\t\t\t\t{inputs[2]}\ndistribution over chromosomes:\t{inputs[3]}\nsequence length:\t\t{inputs[4]}")
		weights = [0.25]*4
		weights[0] = (1-inputs[2])/2
		weights[1] = (1-inputs[2])/2
		weights[2] = inputs[2]/2
		weights[0] = inputs[2]/2
		for i in range(24):
			for chrom in range(inputs[3][i]*inputs[0]):
				generate_fasta_file(inputs[1], i+1, inputs[4],weights)

if __name__ == "__main__":
	main()
