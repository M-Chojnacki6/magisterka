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

Fragmenty kodu zapożyczone z repozytorium na github'ie, z pracy M. Osipowicz
	https://github.com/marnifora/magisterka

class OHEncoder - kodowanie sewkwencji zgodnie z przyjętymi przez sieci wymaganiami;
				zawiera drobne uproszczenia względem pierwotnej wersji;

"""


class OHEncoder:

	def __init__(self, categories=np.array(['A', 'C', 'G', 'T'])):
		self.encoder = Encoder(sparse_output=False, categories=[categories],handle_unknown="ignore")
		self.dictionary = categories
		self.encoder.fit(categories.reshape(-1, 1))
	def __call__(self,seq):
		seq = list(seq)
		info = 1
		if 'N' in seq:
			pos = [i for i, el in enumerate(seq) if el == 'N']
			if len(pos) <= 0.05*len(seq):
				info=0
				print('{} unknown position(s) in given sequence - changed to random one(s)'.format(len(pos)))
				for p in pos:
					seq[p] = random.choice(self.dictionary)
			else:
				return None
		s = np.array(seq).reshape(-1, 1)
		return self.encoder.transform(s).T, info

"""
class CustomNetwork() - inforamcje o architekturze sieci typu Custom 

"""

class CustomNetwork(torch.nn.Module):

	def __init__(self, seq_len, num_channels=[300, 200, 200], kernel_widths=[19, 11, 7], pooling_widths=[3, 4, 4],
				 num_units=[2000, 4], dropout=0.5):
		super(CustomNetwork, self).__init__()
		paddings = [int((w-1)/2) for w in kernel_widths]
		self.seq_len = seq_len
		self.dropout = dropout
		self.params = {
			'input sequence length': seq_len,
			'convolutional layers': len(num_channels),
			'fully connected': len(num_units),
			'number of channels': num_channels,
			'kernels widths': kernel_widths,
			'pooling widths': pooling_widths,
			'units in fc': num_units,
			'dropout': dropout

		}

		conv_modules = []
		num_channels = [1] + num_channels
		for num, (input_channels, output_channels, kernel, padding, pooling) in \
				enumerate(zip(num_channels[:-1], num_channels[1:], kernel_widths, paddings, pooling_widths)):
			k = 4 if num == 0 else 1
			conv_modules += [
				nn.Conv2d(input_channels, output_channels, kernel_size=(k, kernel), padding=(0, padding)),
				nn.BatchNorm2d(output_channels),
				nn.ReLU(),
				nn.MaxPool2d(kernel_size=(1, pooling), ceil_mode=True)
			]
			seq_len = math.ceil(seq_len / pooling)
		self.conv_layers = nn.Sequential(*conv_modules)

		fc_modules = []
		self.fc_input = 1 * seq_len * num_channels[-1]
		num_units = [self.fc_input] + num_units
		for input_units, output_units in zip(num_units[:-1], num_units[1:]):
			fc_modules += [
				nn.Linear(in_features=input_units, out_features=output_units),
				nn.ReLU(),
				nn.Dropout(p=self.dropout)
			]
		self.fc_layers = nn.Sequential(*fc_modules)

	def forward(self, x):
		x = self.conv_layers(x)
		x = x.view(-1, self.fc_input)  # reshape
		x = self.fc_layers(x)
		return torch.sigmoid(x)
	  
		
		
NET_TYPES = {'custom': CustomNetwork}       
"""

Część własna, parsowanie argumentów

""" 

def parse_args():

	parser = argparse.ArgumentParser(description='Auxality script computing results for RegSeqNet models on selected dataset',
		formatter_class=argparse.RawTextHelpFormatter)

	parser.add_argument('model',metavar='m', nargs=1, 
		help="""Finished model, which will be used to compute final vector of probabilities.
Provide file with extension: .model
File [model name]_params.txt should be in the same directory""", default=None)
	parser.add_argument('ins',metavar='i', nargs=1,  help="""Fasta file with sequences of length: 2000.""",default=None)
	parser.add_argument('k',metavar='k', nargs=1,  help="""True category of data;
0 - paromoto active
1 - enhancer active
2 - promotor inactive
3 - enhancer inactive
4 - TATA motif
5 - lack of TATA motif
6 - TATA motif - negative 
7 - lack of TATA motif - negative
8 - random
9 - negative
		""",choices=[0,1,2,3,4,5,6,7,8,9],type= int,default=None)
	parser.add_argument('-o','--out', nargs=1, help="""Name of output .txt file, where results from model and
provided true category will be saved;""",default=None)

	parser.add_argument('-ss', '--shorten_from_start',metavar='p',nargs=1, type=int,
		help="""Shorten start of the sequence by chosen number of nucleotides, e.g. for ss = 40:
ACTGATCTCGATCTGACTCTGGCTACATGCTGCTACGTTCGTCGTCACAACTCGCTGCGTCGTGAGACTGCTGAGACTCCGTATCGTGCTCCATGCGTAA
 
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXCGTCGTCACAACTCGCTGCGTCGTGAGACTGCTGAGACTCCGTATCGTGCTCCATGCGTAA
0 by default""",choices= [x for x in range(0,951)], default=0)
	parser.add_argument('-se', '--shorten_from_end',metavar='e',nargs=1, type=int,
		help="""Shorten start of the sequence by chosen number of nucleotides, e.g. for se = 40:
ACTGATCTCGATCTGACTCTGGCTACATGCTGCTACGTTCGTCGTCACAACTCGCTGCGTCGTGAGACTGCTGAGACTCCGTATCGTGCTCCATGCGTAA
 
ACTGATCTCGATCTGACTCTGGCTACATGCTGCTACGTTCGTCGTCACAACTCGCTGCGTCXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
0 by default""",choices= [x for x in range(0,951)], default=0)
	parser.add_argument('--reverse', action='store_true',help="""reverse shortening of the sequence -> when used with ss shorten end,
with se shorten start, with both ss and se -> remove values from middle of the sequence, e.g. for ss = 40 & se = 40:
ACTGATCTCGATCTGACTCTGGCTACATGCTGCTACGTTCGTCGTCACAACTCGCTGCGTCGTGAGACTGCTGAGACTCCGTATCGTGCTCCATGCGTAA

ACTGATCTCGATCTGACTCTGGCTACATGCTGCTACGTTXXXXXXXXXXXXXXXXXXXXXXGTGAGACTGCTGAGACTCCGTATCGTGCTCCATGCGTAA""")

	args = parser.parse_args()
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
		print("!!!	Given path or file does not exist\n")



	data_in=None
	if args.ins is None:
		print("!	Provide input file\n")
	elif os.path.isfile(args.ins[0]) or os.path.isfile(os.path.abspath(args.ins[0])):
		print(args.ins[0])
		data_in = args.ins[0]
	else:
		print("!!!	Provided input path to input file is incorrect\n")


	"""
	if not ( os.path.exists(args.path[0]) and os.path.abspath(args.path[0]) ):
		print("!!!	Podana ścieżka katalogu z sekwencjami nie istnieje.\n")
	else:
		path=args.path[0]
	"""


	if args.out is None and data_in:
		data_out=f'{args.ins[0].split(".")[0]}_out.txt'
		out = open(data_out,'w')
	elif os.path.isfile(args.out[0]) or os.path.isfile(os.path.abspath(args.out[0])) :
		print("provided output file exists; overwritting...\n")
		data_out = args.out[0]
		out = open(data_out,'r+')
	elif not re.search("//",args.out[0]):
		data_out = args.out[0]
		out = open(data_out,'w')
	else:
		print("!!!!!!	Provided input path to output file is incorrect\n")

	if isinstance(args.k, int):
		k=args.k
	else:
		k=args.k[0]

	if isinstance(args.shorten_from_start, int):
		ss=args.shorten_from_start
	else:
		ss=args.shorten_from_start[0]
	if isinstance(args.shorten_from_end, int):
		se=args.shorten_from_end
	else:
		se=args.shorten_from_end[0]

	if data_in and out and modelfile and model_param:
		return [modelfile, model_param, data_in, out,k,ss,se, args.reverse]
	else:
		return None


def main():
	inputs=parse_args()
	
	if not inputs is None:
		print(f"{' '*13}> Run seq_in.py < \n\n{'#'*20}START{'#'*20}")
		print(f"\nInput model file:\t\t{inputs[0]}\nModel parameters:\t\t{inputs[1]}\nInput file name:\t\t{inputs[2]}\nOutput file:\t\t\t{inputs[3]}\nProvided category:\t\t{inputs[4]}\nShorten start by:\t\t{inputs[5]}\nShorten end by:\t\t\t{inputs[6]}\nReverse shortening:\t\t{inputs[7]}")
		
		"""
		Loading model
		"""

		model_param=inputs[1][::-1].split("_",1)[1]
#		print(model_param)

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

		if "_5_" in model_param:
			model = network(2000,num_units=[2000,5])
			m=5
		else:
			model = network(2000)
			m=4
		
		model.load_state_dict(torch.load(inputs[0], map_location=torch.device('cpu')))
		model.eval()

		out=inputs[3]
		typ=inputs[4]

		"""
		prepare encoder
		"""
		OHE=OHEncoder()

		"""
		uruchamianie modelu dla podanej listy sewkencji
		"""

		with open(inputs[2]) as f:
			for ll in f:
				if ll[0]==">":
					name=ll.strip().split()
					seq=""
					if name[1][:3]=="chr":
						name[0]=f"{name[1][3:]}:{name[2]}"
					elif name[0]==">" and len(name)>=1:
						name[0]=name[1]
					strand="+"
					

					if len(name)>3:
						if name[3] in ["+","-"]:
							strand=name[3]

				else:
					seq=f"{seq}{ll.strip().upper()}"
		#			print(seq)
				
				
				if len(seq)==2000:
					if inputs[6]:
						if inputs[7]:
							seq=f"{seq[:inputs[5]]}{'X'*(2000-inputs[5]-inputs[6])}{seq[-inputs[6]:]}"
						else:
							seq=f"{'X'*inputs[5]}{seq[inputs[5]:-inputs[6]]}{'X'*inputs[6]}"
					else:
						if inputs[7]:
							seq=f"{seq[:inputs[5]]}{'X'*(2000-inputs[5])}"
						else:
							seq=f"{'X'*inputs[5]}{seq[inputs[5]:]}"
					out.write(f"{name[0]}\t+\t{typ}\t")
								
					encoded_seq=OHE(seq)
					if encoded_seq is None:
						if m==4:
							out.write(f"[0.5, 0.5, 0.5, 0.5]\n")	
						else:
							out.write(f"[0.5, 0.5, 0.5, 0.5, 0.5]\n")							
					else:
						X = torch.tensor(encoded_seq[0])
						X = X.reshape(1,1, *X.size())
						X=X.float()
						y=model(X)
						y=y[0].detach().numpy().tolist()
						y=str(y)
						if encoded_seq[1]:
							out.write(f"{y}\n")
						else:
							out.write(f"{y}\tcontains_N\n")
					seq=""
							

		out.close()


if __name__ == "__main__":
	main()