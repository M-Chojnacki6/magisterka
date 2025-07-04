from scipy.stats import fisher_exact
import re
import os
import argparse
import numpy as np
import pandas as pd
import pathlib

L_DEEP=["human_TATA", "human_nonTATA" ,"mouse_TATA" ,"mouse_nonTATA"] 

def parse_args():
	parser = argparse.ArgumentParser(description="Script 2a adding information about presense of TATA motif in sequence to output files from script_1a.py, based on selected .fps file",
		formatter_class=argparse.RawTextHelpFormatter)

	parser.add_argument('fps',metavar='fps', nargs=1,  help="""Path to .fps file containg informations about presence of TATA motif in sequences from selected;
order of results from DeePromoter have to be the same as oreder of corresponding sequences in dataset""",
		type=pathlib.Path)

	parser.add_argument('ins',metavar='inputs', nargs="+",  help="""List of .txt files containing results from four DeePromoter models, generated by script_1a.py;
all files should be generated based on the same input dataset, corresponding to provided .fps file;
end result is the same set of files with additiona column containing 0 / 1:
> 0 - sequences without TATA motif
> 1 - sequences with TATA motif""",
		type=pathlib.Path)



	args = parser.parse_args()

	data_in=[]
	if isinstance(args.ins, list):
		data_tmp=args.ins
	else:
		data_tmp=args.ins[0]
	for file in data_tmp:
		if os.path.isfile(file) or os.path.isfile(os.path.abspath(file)):
			data_in.append(file)
		else:
			print(f"!!!	Provided path to input file {file} is incorrect\n")

	# fps check:
	if isinstance(args.fps, pathlib.Path):
		fps=args.fps
	else:
		fps=args.fps[0]
	if not ( os.path.isfile(fps) or os.path.isfile(os.path.abspath(fps))):
		print(f"Input file not found, check if path is correct:\n{data}")
		fps=None


	if data_in and fps:
		return [data_in, fps]
	else:
		return None




def main():
	inputs=parse_args()
	
	if not inputs is None:
		print(f"{' '*13}> Run script_2a.py < \n\n{'#'*20}START{'#'*20}\nfps file:\t\t{inputs[1]}\ninput files:")
		fps_list=[]
		with open(inputs[1],"r") as fps:
			for row in fps:
				if row[:2]=="FP":
					row = row.strip().split("_")[1].split(" ")[0]
					fps_list.append(int(row)-1)

		for i in range(len(inputs[0])):
			print(f"\t\t\t{inputs[0][i]}")
			file=pd.read_csv(inputs[0][i],sep="\t",header=None)
			file.iloc[:,len(L_DEEP)]=0
			file.iloc[fps_list,len(L_DEEP)]=1
			file = file.astype(int)
			file.to_csv(inputs[0][i],sep="\t",header=False,index=False)

if __name__ == "__main__":
	main()