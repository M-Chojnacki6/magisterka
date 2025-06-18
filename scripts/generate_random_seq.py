import itertools
import random
import numpy as np
import argparse
import re
import os


def parse_args():

	parser = argparse.ArgumentParser(description="""Script creating random data - both in .fasta and .txt format""")

	parser.add_argument('o', nargs=1, help="""Name of output [name][.fasta, .txt] files, to which 
		sequences 2000 nt (.fasta) and 300 nt (.txt) will be saved;""",default=None)
	parser.add_argument('-n','--number', nargs=1, help="""Number of sequences to generate in tousands;
		defaul: 40""",type=int,default=40)
	parser.add_argument('-s','--start', nargs=1, help="""Index number from which shorter sequence will start in longer;
	default: 749 """,type=int,default=749)
	parser.add_argument('-l1','--length_1', nargs=1, help="""Length of longer sequences (.fasta); default: 2000;
		""",type=int,default=2000)
	parser.add_argument('-l2','--length_2', nargs=1, help="""Length of shorter sequences (.txt); default: 300;
		""",type=int,default=300)

	args = parser.parse_args()


	n=40
	if isinstance(args.number, int):
		n=args.number
	else:
		n=args.number[0]

	k=749
	if isinstance(args.start, int):
		k=args.start
	else:
		k=args.start[0]

	if k>=1699 or k<0:
		k=749

	out1=None
	out2=None
	if args.o is None:
		out1=open(f"Random_sequences_{n}k.fasta","W")
		out2=open(f"Random_sequences_{n}k.txt","W")
	elif os.path.isfile(args.o[0]) or os.path.isfile(os.path.abspath(args.o[0])) :
		print("provided file out exists;\noverwriting...\n")
		data_out = args.o[0]
		out1 = open(f"{data_out}.fasta",'r+')
		out2 = open(f"{data_out}.txt",'r+')
	elif not re.search("//",args.o[0]):
		data_out = args.o[0]
		out1 = open(f"{data_out}.fasta",'w')
		out2 = open(f"{data_out}.txt",'w')
	else:
		print("!!!	Provided path to output file is not correct")

	l1=2000
	l2=300
	if isinstance(args.length_1, int):
		l1=args.length_1
	else:
		l1=args.length_1[0]
	if isinstance(args.length_2, int):
		l2=args.length_2
	else:
		l2=args.length_2[0]
	if out1 and out2:
		return [out1, out2,n,k,l1,l2]
	else:
		return None

num_to_nt = {0:"A",1:"C",2:"G",3:"T"}
def main():
	inputs=parse_args()
	
	if not inputs is None:
		print(f"{' '*7}> Run generate_random_seq.py < \n\n{'#'*20}START{'#'*20}")
		print(f"\nOutput file (fasta):\t\t{inputs[0]}\nOutput file (txt):\t\t{inputs[1]}\nNumber of sequences:\t\t{inputs[2]}\nStart shorter from:\t\t{inputs[3]} position\nLength of longer sequences:\t{inputs[4]}\nLength of shorter sequences:\t{inputs[5]}")
		out1=inputs[0]
		out2=inputs[1]
		for n in range(inputs[2]*1000):
			seq_tmp=random.choices(np.arange(4), k=inputs[4])
			seq=""
			for x in seq_tmp:
				seq+=num_to_nt[x]
			out1.write(f"> random_{n}\n{seq}\n")
			out2.write(f"{seq[inputs[3]:inputs[3]+inputs[5]]}\n")

		
		out1.close()
		out2.close()


if __name__ == "__main__":
	main()
