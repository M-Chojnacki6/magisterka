import itertools
import random
import numpy as np
import argparse
import re
import os


def parse_args():

	parser = argparse.ArgumentParser(description="""Script creating negative data as described in DeePromotor 
		publication, by substituting n-k from n patritions with random nucleotides""")

	parser.add_argument('ins',metavar='i', nargs=1,  help="""Input .txt/.fasta multisequence format""",default=None)
	parser.add_argument('-o','--out', nargs=1, help="""Name of output .txt/.fasta file, to which 
		sequences will be saved; default: [name]_ngv.txt .""",default=None)
	parser.add_argument('-nr','--parts_number', nargs=1, help="""Number of parts to divide provided sequences;
		default: 20 """,type=int,default=20)
	parser.add_argument('-k', "--parts_kept", nargs=1, help="""Number of parts to keep unchnged;
		default: 8""",type=int,default=8)


	args = parser.parse_args()
	IS_FASTA=False
	data_in=None
	if args.ins is None:
		print("!	Provide input fasta file\n")
	elif os.path.isfile(args.ins[0]) or os.path.isfile(os.path.abspath(args.ins[0])):
		data_in = args.ins[0]
		if data_in[-6:]==".fasta":
			IS_FASTA=True
	else:
		print("!!!	Provided path and/or file does not exist\n")


	out=None
	if args.out is None and data_in:
		if IS_FASTA:
			data_out=re.sub(".fasta","_ngv.fasta",data_in)
		else:
			if "pos" in data_in:
				data_out=re.sub("pos","ngv",args.ins[0])
			elif data_in[-4:]==".txt":
				data_out=re.sub(".txt","_ngv.txt",args.ins[0])
			else:
				data_out=f'{args.ins[0].split(".")[0]}_ngv.txt'
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

	if k>=n:
		k=int(n*0.4)
	if data_in and out:
		return [data_in, out,n,k,IS_FASTA]
	else:
		return None

num_to_nt = {0:"A",1:"C",2:"G",3:"T"}

def generate_ngv(seq,n,k):
	length=len(seq)
	part_len = length // n
	if part_len * n < length:
		n += 1
	iterator = np.arange(n)
	keep_parts = random.sample(list(iterator), k=k)
	res=""
	for it in iterator:
		start = it * part_len
		pro_part = seq[start:start + part_len]
		if it in keep_parts:
			res=f"{res}{pro_part}"
		else:
			pro_part = random.choices(np.arange(4), k=len(pro_part))
			for i in pro_part:
				res=f"{res}{num_to_nt[i]}"
	return res


def main():
	inputs=parse_args()
	
	if not inputs is None:
		print(f"{' '*13}> Run generate_negative_seq.py < \n\n{'#'*20}START{'#'*20}")
		print(f"\nInput file:\t\t\t{inputs[0]}\nOutput file:\t\t\t{inputs[1]}\nDivided to:\t\t\t{inputs[2]} parts\nKeep:\t\t\t\t{inputs[3]} parts")

		out=inputs[1]
		with open(inputs[0]) as f:
			if inputs[4]:
				seq=""
				for ll in f:
					if ll[0]==">" and seq:
						seq=generate_ngv(seq,inputs[2],inputs[3])
						out.write(f"{seq}\n{ll.strip()} ngv\n")
						seq=""
					elif ll[0]==">":
						out.write(f"{ll.strip()} ngv\n")
					else:
						ll=ll.strip().upper()
						seq=f"{seq}{ll}"

			else:

				for ll in f:
					ll=ll.strip().upper()
					n=inputs[2]
					length = len(ll)
					if len(ll)!=300:
						print(f"found irregular line, len() = {len(ll)}")

					seq=generate_ngv(ll,inputs[2],inputs[3])

					out.write(f"{seq}\n")
	
		if inputs[4]:
			out.write(f"{seq}")
		out.close()


if __name__ == "__main__":
	main()
