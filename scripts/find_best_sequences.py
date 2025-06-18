from sklearn.preprocessing import OneHotEncoder as Encoder
import argparse
import numpy as np
import torch
import re
import os
import random
import torch.nn as nn
import torch.nn.functional as F
import math

"""

Parts of the code adapted from github repository belonging to M. Osipowicz
	https://github.com/marnifora/magisterka

class OHEncoder() - adapted version of preprocessing input sequences - the main change: 
	handling unknown symbols (X) as vector of 0s;

class CustomNetwork() - informations about RegSeqNet architecture
"""

from seq_in import OHEncoder, CustomNetwork

NET_TYPES = {'custom': CustomNetwork}  
nucleotides = ['A', 'T', 'C', 'G']

def parse_args():

	parser = argparse.ArgumentParser(description='Script finding example of the nucleotid sequence providing best score for given output neuron',
		formatter_class=argparse.RawTextHelpFormatter)

	parser.add_argument('model',metavar='m', nargs=1, 
		help="""Model, which will be used to comute final vector of probabilities.
Provide file with extension: .model
File [model name]_params.txt should be in the same directory""", default=None)
	parser.add_argument('-c', '--category', nargs=1, type=int,help="""Index of neuron (class of sequence), for which optimal sequence will be found
0 - promoter active
1 - nonpromoter active
2 - promoter inactive
3 - nonpromoter inactive
4 - random (only for bigger networks)
defualt: 0""",default=0)
	parser.add_argument('-ins',metavar='i', nargs=1,  help="""Fasta file with sequences of length: 2000, from which we take first sequence as the
starting nucleotid sequence; if none provided, random sequence will be generated""",default=None)
	parser.add_argument('-n','--sequence_number', action='store', metavar='INT', type=int, default=1,
	help='number of optimal sequences to find, found by muteiting input sequence with different random seeds; default: 1')
	parser.add_argument('--seed', action='store', metavar='NUMBER', type=int, default='0',help='Set random seed, default: 0')
	parser.add_argument('-o','--out', nargs=1, help="""Name of output .fasta file, where optimal sequence will be saved; 
default: optimum_[class_index].fasta""",default=None)
	parser.add_argument('-min', '--optimum_lower_bound',metavar='u',nargs=1, type=float,
		help="""Minimal value of optimizing neuron, for which script recognise sequence as  good enough and ends.
This value should be from range [0.6 - 1.0]
Default: 0.95""", default=0.95)
	parser.add_argument('-max', '--non_optimum_higher_bound',metavar='d',nargs=1, type=float,
		help="""Maximal value of NOT optimized neurons, for which script recognise sequence as  good enough and ends.
This value should be from range [0.5 - 0.75]
Default: 0.55""", default=0.55)
	parser.add_argument('--num_neurons', action='store', metavar='INT', type=int, default=4,
	help='number of output neurons/class; default: 4')
	parser.add_argument('--cpu', action='store_true',	help='force script to use cpu instead of cuda.')
	args = parser.parse_args()

	model_param=None
	name=None
	modelfile=None
	if args.model is None:
		print("!!!	Please give a model\n")

	elif os.path.isfile(args.model[0]):
#		print(">> model loaded\n")
		modelfile = args.model[0]
		if '/' in modelfile:
			model_param=modelfile.split("/")[-1]
			name=model_param
	else:
		print("!!!	Given model path does not exist\n")

	if isinstance(args.category, int):
		c=args.category
	else:
		c=args.category[0]
	if isinstance(args.sequence_number, int):
		n=args.sequence_number
	else:
		n=args.sequence_number[0]
	if isinstance(args.seed, int):
		seed=args.seed
	else:
		seed=args.seed[0]
	seq=""
	torch.manual_seed(seed)
	np.random.seed(seed)
	if args.ins is None:

		seq=''.join(np.random.choice(nucleotides) for _ in range(2000))
	elif os.path.isfile(args.ins[0]) or os.path.isfile(os.path.abspath(args.ins[0])):
#		print(args.ins[0])
		data_in = args.ins[0]
		with open(data_in,"r") as f:
			line=f.readline()
			line=f.readline()
			while line[0]!=">":
				seq = f"{seq}{line.strip().upper()}"
				line=f.readline()
				if line.strip()=="":
					break

	else:
		print("!!!	Provided input path to input file is incorrect\n")


	out=None
	if args.out is None:
		out=f'optimum_{c}.fasta'
	elif os.path.isfile(args.out[0]) or os.path.isfile(os.path.abspath(args.out[0])) :
		out = args.out[0]
	elif not re.search("//",args.out[0]):
		out = args.out[0]
	else:
		print("!!!!!!	Provided path to output file is incorrect\n")

	if isinstance(args.optimum_lower_bound, float):
		u=args.optimum_lower_bound
	else:
		u=args.optimum_lower_bound[0]
	if u<0.6 or u >1.0:
		print("min value {u} out of bound [0.6 - 1.0]; changing to default value: 0.95")
		u=0.95
	if isinstance(args.non_optimum_higher_bound, float):
		d=args.non_optimum_higher_bound
	else:
		d=args.non_optimum_higher_bound[0]
	if d<0.5 or d >0.75:
		print("max value {d} out of bound [0.5 - 0.75]; changing to default value: 0.55")
		d=0.55
	if isinstance(args.num_neurons, int):
		num=args.num_neurons
	else:
		num=args.num_neurons[0]

	if num!= 4 or num!=5:
		num=4

	if seq and out and modelfile and model_param:
		return [modelfile, model_param, seq, out,c, u ,d,num,seed,n,args.cpu]
	else:
		return None


def main():
	inputs=parse_args()
	
	if not inputs is None:
		print(f"{' '*17}> Run find_best_sequence.py < \n\n{'#'*20}START{'#'*20}")
		print(f"\nInput model file:\t\t{inputs[0]}\nModel parameters:\t\t{inputs[1]}\nstarting sequence:\t\t{inputs[2]}\nOutput file:\t\t\t{inputs[3]}\nProvided category:\t\t{inputs[4]}\nNumber of sequences:\t\t{inputs[9]}\nMin optimum:\t\t\t{inputs[5]}\nMax non-optimum:\t\t{inputs[6]}\nNumber of output neurons:\t{inputs[7]}\nSeed:\t\t\t\t{inputs[8]}")
		if inputs[10]:
			device = torch.device('cpu')
		else:
			device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
		"""
		Loading model
		"""

		model_param=inputs[1][::-1].split("_",1)[1]
		model_param=model_param[::-1]
		#print(model_param)
		md=inputs[0][::-1].split("/",1)[1]
		md=md[::-1]
		#print(md)
		model_param=f"{md}/{model_param}_params.txt"
		#print(model_param)


		par=open(os.path.normpath(model_param))
		for line in par:
			if line.startswith('Network type'):
				network = NET_TYPES[line.split(':')[-1].strip().lower()]
		par.close()

		model = network(2000,num_units=[2000,inputs[7]])
		model.load_state_dict(torch.load(inputs[0], map_location=device))
		model.eval()

		typ=inputs[4]
		
		"""
		prepare encoder
		"""
		OHE=OHEncoder()

		# prepare list of non-optimized neurons
		non_opt=[]
		for  x in range(inputs[7]):
			if x!=typ:
				non_opt.append(x)
#		print(non_opt)
		"""
		Main loop: checking results and changing sequence
		"""
		for k in range(inputs[9]):
			end = True
			i=0
			seq=inputs[2]
			old_opt=0.5
			old_seq=seq
			while end:
				check_min=True
				check_max=True
				# encoding sequence and obtaining results neurons
				encoded_seq=OHE(seq)
				X = torch.tensor(encoded_seq[0])
				X = X.reshape(1,1, *X.size())
				X=X.float()
				y=model(X)
				y=y[0].detach().numpy().tolist()
	#			print(y)
				rest=[]
				for r in non_opt:

					rest.append(y[r])
					if y[r]>inputs[6]:
						check_max=False
				if y[typ]<inputs[5]:
					check_min=False
#				print(f">>> step: {i}\nsequence: {seq}\noptimized value: {y[typ]}\nrest: {rest}\n")
				if check_min and check_max:
					end=False
#					print("optimal sequence found!")
				else:
					if old_opt>y[typ]:
						seq=old_seq
					elif old_opt<y[typ]:
						old_opt=y[typ]
						old_seq=seq
					position=np.random.randint(0,2000)
					new=np.random.choice(nucleotides)
					while new==seq[position]:
						new=np.random.choice(nucleotides)
					if position==0:
						seq=f"{new}{seq[1:]}"
					elif position==1999:
						seq=f"{seq[:1999]}{new}"
					else:
						seq=f"{seq[:position]}{new}{seq[position+1:]}"
				i+=1
			if k%10==0:
				print(f"progres: {k}/{inputs[9]}")
			out=open(inputs[3],"a+")				
			out.write(f"> {k}_optimal_for_category: {typ}\tmodel: {model_param}\tresults: {y}\tinitial seed: {inputs[8]}\tmin: {inputs[5]}\tmax: {inputs[6]}\tnumber of steps\t{i}\n{seq}\n")
			out.close()


if __name__ == "__main__":
	main()
