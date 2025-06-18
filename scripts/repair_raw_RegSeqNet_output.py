import argparse
import pandas as pd
import os
import pathlib


def parse_args():

	parser = argparse.ArgumentParser(description="""Script changing true category in singular RegSeqNet 
output fle to selected class""",formatter_class=argparse.RawTextHelpFormatter)

	parser.add_argument('ins',metavar='i', nargs=1, 
		help="""Input _out.txt files from all_ins.sh""",default=None,type=pathlib.Path)
	parser.add_argument('c',metavar='INT', nargs=1, 
		help="""True category, to which column 3 in input file will be changed""",choices=[0,1,2,3,4,5],type=int)

	args = parser.parse_args()

	data_in=[]
	if isinstance(args.ins, list):
		data_in=args.ins[0]
	else:
		data_in=args.ins

	if isinstance(args.c, list):
		c=int(args.c[0])
	else:
		c=int(args.c)

	if data_in:
		return [data_in, c]
	else:
		return None

def main():
	inputs=parse_args()

	if inputs:
		print(f"{' '*13}> Run repair_raw_RegSeqNet_output.py < \n\n{'#'*20}START{'#'*20}\n\nInput file:\t\t{inputs[0]}\nnew true category:\t{inputs[1]}")
		data=pd.read_csv(inputs[0],sep="\t",usecols=[0, 1,2,3],header=None)
		data.iloc[:,2]=inputs[1]
		data.to_csv(inputs[0],sep="\t",header=False,index=False)

if __name__ == "__main__":
	main()
