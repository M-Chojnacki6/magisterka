import numpy as np
import argparse
import re
import os
import pathlib


names=["custom40", "custom41", "alt1", "alt2"]

def parse_args():

	parser = argparse.ArgumentParser(description="""Script performing simple analasys of results form
		nets custom[n]/alt[n] and clasyfying these nest according to found categories""")

	parser.add_argument('ins',metavar='i', nargs="+", 
		help="""Input _out.txt multisequence format after merging""",default=None,type=pathlib.Path)
	parser.add_argument('-o','--out', nargs=1, help="""Name of output .csv file. Default: results/RegSeqNet_count_out.csv""",
		default=pathlib.Path("results/RegSeqNet_count_out.csv"),type=pathlib.Path)


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
	out=None
	if isinstance(args.out, list):
		out=args.out[0]
	else:
		out= args.out
	if not (os.path.isdir(pathlib.Path(out).parent) or os.path.isdir(os.path.abspath(pathlib.Path(out)).parent) ) :
		out=None

	if data_in and out:
		return [data_in, out]
	else:
		return None


"""
function fun() loading data from merged output files from RegSeqNet models
"""

"""
liczby:
* 0,1,2,3 - labels for sequences classified unambigous: with only one output neuron !=0.5 and rest =  0.5
	0:  promoter active
	1:  nonpromoter active
	2:  promoter inactive
	3:  nonpromoter inactive
* 4-9 labels for sequences recognized to two categories (!= 0.5)
	4: [1, 1, 0, 0]
	5: [1, 0, 1, 0]
	6: [1, 0, 0, 1]
	7: [0, 1, 1, 0]
	8: [0, 1, 0, 1]
	9:[0, 0, 1, 1]
* 10-13 labels for sequences recognized to three categories (!= 0.5)
	10:[1, 1, 1, 0]
	11:[1, 1, 0, 1]
	12:[1, 0, 1, 1]
	13:[0, 1, 1, 1]
* 14,15 ambigous - classified to ether all or none categories
	14:[1, 1, 1, 1]
	15:[0, 0, 0, 0]
"""


def simple_load(file):
	m=np.zeros((4,len(names)),dtype=int)
	x=0
		
	with open(file,"r") as f:
		for line in f:
			line=line.split("\t")
			for model in range(len(names)):
				m[int(line[3+model])][model]+=1
			x+=1
	return m


category=["pa","na","pi","ni"]
def main():
	inputs=parse_args()
	
	if inputs:
		print(f"{' '*13}> Run analyses1.py < \n\n{'#'*20}START{'#'*20}\n\nInput files:")
		for i in inputs[0]:
			print(f"\t\t\t{i}")
		print(f"\nOutput file:\t\t{inputs[1]}\n")
		with open(inputs[1],"w") as out:
			s="Input\tcategory"
			for c in names:
				s=f"{s}\t{c}"
			for i in range(len(inputs[0])):
				m = simple_load(inputs[0][i])
				m=m/m.sum(axis=0)*100

				out.write(f"{s}\n")
				for l in range(len(m)):
					s=f"{inputs[0][i]}\t{category[l]}"
					for c in m[l]:
						s=f"{s}\t{'{:.2f}'.format(round(c, 2))}"
					out.write(f"{s}\n")


if __name__ == "__main__":
	main()