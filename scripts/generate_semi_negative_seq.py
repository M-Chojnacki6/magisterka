import itertools
import random
import numpy as np
import argparse
import re
import os


def parse_args():

	parser = argparse.ArgumentParser(description="""Script creating semi negative data in similar way to these
	described in DeePromotor publication, but with selected patritons substituted with noncoding genomic sequences rather than
	complitly random.""")

	parser.add_argument('ins',metavar='i', nargs=1,  help="""Input .txt multisequence format""",default=None)
	parser.add_argument('-o','--out', nargs=1,metavar='O', help="""Name of output .txt file, to which 
		sequences will be saved; default: [name]_sem_ngv.txt .""",default=None)
	parser.add_argument('-nr','--parts_number',metavar='N', nargs=1, help="""Number of parts to divide provided sequences;
		default: 20 """,type=int,default=20)
	parser.add_argument('-k', "--parts_kept",metavar='K', nargs=1, help="""Number of parts to keep unchnged;
		default: 8""",type=int,default=8)
	parser.add_argument('ran',metavar='r', nargs=1,  help="""Input .fasta multisequence format with noncoding sequences""",default=None)


	args = parser.parse_args()

	data_in=None
	if args.ins is None:
		print("!	Provide input .txt file\n")
	elif os.path.isfile(args.ins[0]) or os.path.isfile(os.path.abspath(args.ins[0])):
		data_in = args.ins[0]
	else:
		print("!!!	Provided path to input .txt file and/or file does not exist\n")

	data_ran=None
	if args.ran is None:
		print("!	Provide input .fasta file\n")
	elif os.path.isfile(args.ran[0]) or os.path.isfile(os.path.abspath(args.ran[0])):
		data_ran = args.ran[0]
	else:
		print("!!!	Provided path to input .fasta file and/or file does not exist\n")

	out=None
	if args.out is None:
		if "pos" in data_in:
			data_out=re.sub("pos","sem_ngv",args.ins[0])
		elif data_in[-4:]==".txt":
			data_out=re.sub(".txt","_sem_ngv.txt",args.ins[0])
		else:
			data_out=f'{args.ins[0].split(".")[0]}_sem_ngv.txt'
		out = open(data_out,'w')
	elif os.path.isfile(args.out[0]) or os.path.isfile(os.path.abspath(args.out[0])) :
		print("podany plik out istnieje\n")
		data_out = args.out[0]
		out = open(data_out,'r+')
	elif not re.search("//",args.out[0]):
		data_out = args.out[0]
		out = open(data_out,'w')
	else:
		print("!!!	Provided path to output file is not correct")

	n=20
	if isinstance(args.parts_number, int):
		n=args.parts_number
	else:
		n=args.parts_number[0]

	k=8
	if isinstance(args.parts_kept, int):
		k=args.parts_kept
	else:
		k=args.parts_kept[0]

	if k>=20:
		k=int(20*0.4)
	if data_in and out and data_ran:
		return [data_in, out,n,k,data_ran]
	else:
		return None

num_to_nt = {0:"A",1:"C",2:"G",3:"T"}
def main():
	inputs=parse_args()
	
	if not inputs is None:
		print(f"{' '*13}> Run generate_negative_seq.py < \n\n{'#'*20}START{'#'*20}")
		print(f"\nInput .txt file:\t\t{inputs[0]}\nInput .fasta file:\t\t{inputs[4]}\nOutput file:\t\t\t{inputs[1]}\nDivided to:\t\t\t{inputs[2]} parts\nKeep:\t\t\t\t{inputs[3]} parts")

		out=inputs[1]

		# loading noncoding sequences as one string
		rand_l=100000
		rand_seq=""
		with open(inputs[4]) as f:
			line=f.readline()
			while len(rand_seq)<rand_l and line:
				if line[0]!=">":
					rand_seq+=line.strip().upper()
				line=f.readline()
		rand_seq=rand_seq.strip()
		rand_l=len(rand_seq)

		with open(inputs[0]) as f:
			for ll in f:
				ll=ll.strip().upper()
				n=inputs[2]
				length = len(ll)
				if len(ll)!=300:
					print(f"found irregular line, len() = {len(ll)}")
				part_len = length // inputs[2]
				if part_len * inputs[2] < length:
					n += 1
				iterator = np.arange(n)
				keep_parts = random.sample(list(iterator), k=inputs[3])

				seq=""
				for it in iterator:
					start = it * part_len
					pro_part = ll[start:start + part_len]
					if it in keep_parts:
						seq=f"{seq}{pro_part}"
					else:
						pro_part = random.randint(0,rand_l-part_len)
						seq=f"{seq}{rand_seq[pro_part:pro_part+part_len]}"

				out.write(f"{seq}\n")
	

		out.close()


if __name__ == "__main__":
	main()