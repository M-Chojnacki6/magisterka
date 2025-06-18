import os 
from statistics import  mean
import argparse
import pathlib
optim_A="A"*2000
optim_C="C"*2000
optim_G="C"*2000
optim_T="C"*2000

def parse_args():
	parser = argparse.ArgumentParser(description="""Script 6 computing Hamming distance between results of sequence optimalisations;
format of the files NAME should be: 
optim_[custom<n>/alt<n>]_[A/C/G/T]_[0/1/2/3]
corresponding to model, on which sequences were optimalised,
starting seqeunce (all A/C/G/T)
category, which was optimised""",
		formatter_class=argparse.RawTextHelpFormatter)

	parser.add_argument('-d',metavar='d', nargs=1, 
		help="""Directory containing input files; Default: results/""",default=None)
	args = parser.parse_args()

	data_dir=None
	if args.d is None:
		data_dir=pathlib.Path("results/")
	elif os.path.isdir(args.d[0]) or os.path.isdir(os.path.abspath(args.d[0])):
		data_dir= pathlib.Path(args.d[0])
	else:
		print("!!!	Provided path and/or file does not exist\nchanging to default: results/")
		data_dir=pathlib.Path("results/")
	files=[]

	for m in ["custom40","custom41", "alt1","alt2"]:
		for n in ["A","C","G","T"]:
			for i in range(4):
				if os.path.isfile(os.path.join(str(data_dir),f"optim_{m}_{n}_{i}.fasta")):
					files.append(os.path.join(str(data_dir),f"optim_{m}_{n}_{i}.fasta"))

	if files:
		return files
	else:
		return None

def main():
	inputs=parse_args()
	
	if inputs:
		print(f"{' '*13}> Run script_6.py < \n\n{'#'*20}START{'#'*20}\n\nInput files:")
		for file in inputs:
			print(f"\t\t\t{file}")

			Hamming_A=[]
			Hamming_C=[]
			Hamming_G=[]
			Hamming_T=[]
			print(f"\n{'-'*50}\nfile: {file}\n")
			with open(file,"r") as f:
				for line in f:
					if line[0]!=">":
						line=line.strip()
						Hamming_A.append(2000-line.count("A"))
						Hamming_C.append(2000-line.count("C"))
						Hamming_G.append(2000-line.count("G"))
						Hamming_T.append(2000-line.count("T"))
			print(f"mean Hamming distance to:\nall A:\t{mean(Hamming_A)}\nall C:\t{mean(Hamming_C)}\nall G:\t{mean(Hamming_G)}\nall T:\t{mean(Hamming_T)}")


if __name__ == "__main__":
	main()