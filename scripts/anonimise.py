import argparse
import re
import os
import pathlib


code = ["HG","GB","NA","PA","DA"]

def parse_args():

	parser = argparse.ArgumentParser(description="""Script to remove patient codes from fasta files""",
		formatter_class=argparse.RawTextHelpFormatter)

	parser.add_argument('ins',metavar='i', nargs=1,  help="""Input .fasta multisequence format - one line, onse sequence""",default=None)
	parser.add_argument('-o','--out',metavar='i', nargs=1,  help="""Name of the output file, if not selected, input file eill be overwrited""",default=None)


	args = parser.parse_args()

	data_in=None
	if args.ins is None:
		print("!	Provide input file\n")
	elif os.path.isfile(args.ins[0]) or os.path.isfile(os.path.abspath(args.ins[0])):
		data_in = args.ins[0]
	else:
		print("!!!	Provided path and/or file does not exist\n")

	out=None
	if isinstance(args.out, list):
		if os.path.isfile(args.out[0]):
			out=os.path.abspath(args.out[0])
		elif not "/" in args.out[0]:
			out=os.path.abspath(args.out[0])
	else:
		print("Overwriting input file")
		out=args.out

	if out is None:
		out =  data_in
	if data_in and out:
		return [data_in, out]
	else:
		return None


def main():
	inputs=parse_args()
	
	if inputs:
		print(f"{' '*13}> Run anonimise.py < \n\n{'#'*20}START{'#'*20}")
		print(f"\nInput files:\t\t\t{inputs[0]}\nOutput file:\t\t\t{inputs[1]}")
		if inputs[0]==inputs[1]:
			out=open("tmp.fasta","w")
		else:
			out=open(inputs[1],"w")
		with open(inputs[0],"r") as f:
			for line in f:
				if line[0]==">":
					for c in code:
						if c in line:
							header=""
							line=line.strip().split()
							for l in line:
								if not re.findall(f"^{c}[0-9]+",l):
									header=f"{header} {l}"
							line=header

				out.write(f"{line.strip()}\n")

		out.close()

		if inputs[0]==inputs[1]:
			os.system(f"mv tmp.fasta {inputs[1]}")
			if os.path.isfile("tmp.fasta"):
				os.system(f"rm tmp.fasta")


if __name__ == "__main__":
	main()