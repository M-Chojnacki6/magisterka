import numpy as np
import argparse
import re
import os
import pathlib
from sklearn.metrics import roc_auc_score


names=["pa", "na", "pi", "ni", "pa_ngv", "na_ngv", "pi_ngv", "ni_ngv","random"]


def parse_args():

	parser = argparse.ArgumentParser(description="""Script performing simple analasys of results form
		nets new RegSeqNet models""",formatter_class=argparse.RawTextHelpFormatter)

	parser.add_argument('ins',metavar='i', nargs="+", 
		help="""Input _out.txt files from all_ins.sh""",default=None,type=pathlib.Path)
	parser.add_argument('-o','--out', nargs=1, help="""Name of output .csv file. Default: results/RegSeqNet_new_count_out.csv""",
		default=pathlib.Path("results/RegSeqNet_new_count_out.csv"),type=pathlib.Path)
	parser.add_argument('-f','--five_output_neurons', help="""Change number of output categories from 4:
* 0 - promoter,
* 1 - nonpromoter active,
* 2 - nonpromoter inactive,
* 3 - random
to 5 categories:
* 0 - promoter active,
* 1 - nonpromoter active,
* 2 - promoter active,
* 3 - nonpromoter inactive,
* 4 - random""",action= 'store_true')


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
		return [data_in, out,args.five_output_neurons]
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

def load_list(line):
	line=line[1:]
	line=line[:-1]
	r=[float(l) for l in line.split(",")]
	return r
"""
function which() finds the most liely output neuron from modle output by the highest values

# line - string, output vector from selected model, e.g.: "[0.5, 0.9894, 0.7521, 0.5]"
"""
def which(line):
	r=load_list(line)
	res=0
	tmp=0
	for y in range(len(r)):
		if tmp<r[y]:
			res=y
			tmp=r[y]
	return res



def simple_load(file,c):
	m=np.zeros((len(c)),dtype=int)
	cat=None
	with open(file,"r") as f:

		for line in f:
			line=line.strip().split("\t")
			cat=which(line[3])
			m[cat]+=1
			cat=int(line[2])
			if cat >3 and len(c)==4:
				cat=3
	return m, cat


def load_AUC(file,c):
	m=[]
	cat=[]
	with open(file,"r") as f:

		for line in f:
			line=line.strip().split("\t")		
			ncat=int(line[2])
			if ncat >3 and len(c)==4:
				ncat=3
			cat.append(ncat)
			r = load_list(line[3])
			# rescale to sum = 1 and prob = 0.5 -> 0
			r=np.array(r)
			r=r-0.5
			if r.sum():
				r=r/r.sum()
			else:
				r=np.array([1/len(c) for x in range(len(c))])
			m.append(r)
	return m, cat


def main():
	inputs=parse_args()
	
	if inputs:
		print(f"{' '*13}> Run script_7.py < \n\n{'#'*20}START{'#'*20}\n\nInput files:")
		for i in inputs[0]:
			print(f"\t\t\t{i}")
		if inputs[2]:
			category=["pa","na","pi","ni","random"]
		else:
			category=["p","na","ni","random"]
		print(f"\nOutput file:\t\t{inputs[1]}\nNumber of categories:\t{len(category)}")
		with open(inputs[1],"w") as out:
			s="Input\ttrue_category"
			for c in category:
				s=f"{s}\t{c}"
			out.write(f"{s}\n")
			m=np.zeros((len(category),len(category)),dtype=int)

			AUC_true=[]
			AUC_res=[]
			for i in range(len(inputs[0])):
				mt,c= simple_load(inputs[0][i],category)

				m[c,:] += mt
				mt=mt/mt.sum(axis=0)*100
				print(mt)
				
				s=f"{inputs[0][i]}\t{c}"
				for t in mt:
					s=f"{s}\t{'{:.2f}'.format(round(t, 2))}"
				out.write(f"{s}\n")

				a,b=load_AUC(inputs[0][i],category)
				AUC_true.extend(b)
				AUC_res.extend(a)

			dm=m.sum(axis=1).reshape((len(category),1))
			for i in range(len(category)):
				if not dm[i,0]:
					dm[i,0]=1
			m=m/dm*100
			print(m)
			for l in range(len(m)):
				s=f"Total\t{category[l]}"
				for t in m[l]:
					s=f"{s}\t{'{:.2f}'.format(round(t, 2))}"
				out.write(f"{s}\n")
			if AUC_true and AUC_res:
				AUC=roc_auc_score(AUC_true,AUC_res,multi_class='ovr')
			else:
				AUC=None
			out.write(f"AUC:\t{AUC}")

if __name__ == "__main__":
	main()
