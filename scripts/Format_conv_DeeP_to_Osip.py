import argparse
import re
import os

def parse_args():

	parser = argparse.ArgumentParser(description="""Script coverting data format usied by DeePromotor 
		(one sequence per row, 300 nt, witjout headers)
		  to data format used by nets CustomNets (multifasta with 2000 nt sequences each)""")

	parser.add_argument('ins',metavar='i', nargs=1,  help="""Input .txt multisequence format""",default=None)
	parser.add_argument('-o','--out', nargs=1, help="""Name of output .fasta file, to which 
		sequences will be saved; defoult: [name].fasta .""",default=None)
	parser.add_argument('-s','--start', nargs=1, help="""Index number from which shorter sequence will start in longer;
	default: 749 """,type=int,default=749)
	parser.add_argument('p', nargs=1, help="""Pattern to the prefix of headers of new sequences;
	default: [Patter]_[index] """,type=str,default="DeeP")


	args = parser.parse_args()

	data_in=None
	if args.ins is None:
		print("!	Provide input fasta file\n")
	elif os.path.isfile(args.ins[0]) or os.path.isfile(os.path.abspath(args.ins[0])):
		print(args.ins[0])
		data_in = args.ins[0]
	else:
		print("!!!	Provided path and/or file does not exist\n")

	out=None
	if args.out is None:
		if data_in:
			if data_in[-4:]==".txt":
				data_out=re.sub(".txt",".fasta",args.ins[0])
			else:
				data_out=f'{args.ins[0].split(".")[0]}.fasta'
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

	if isinstance(args.start, int):
		s=args.start

	else:
		s=args.start[0]

	if s>=1699:
		print(f"starting index selected too big: {s}, changing to default 749")
		s=749
	pattern= "DeeP"
	if isinstance(args.p, str):
		pattern=args.p
	else:
		pattern=args.p[0]

	if data_in and out:
		return [data_in, out,s,pattern]
	else:
		return None


def main():
	inputs=parse_args()
	
	if not inputs is None:
		print(f"{' '*13}> Run Format_conv_Osip_to_DeeP.py < \n\n{'#'*20}START{'#'*20}")
		print(f"\nInput file:\t\t\t{inputs[0]}\nOutput file:\t\t\t{inputs[1]}\nStarting index:\t\t\t{inputs[2]}\nPattern prefix:\t\t\t{inputs[3]}")
		
		out=inputs[1]
		x=0
		with open(inputs[0]) as f:
			for ll in f:
				ll=ll.strip().upper()
				if len(ll)!=300:
					print(f"found irregular line, len() = {len(ll)}")
				out.write(f"> {inputs[3]}_{x} converted from DeePromotor\n")
				out.write(f"{(inputs[2]-1)*'X'}{ll}{(2001-len(ll)-inputs[2])*'X'}\n")
				x+=1
							

		out.close()


if __name__ == "__main__":
	main()