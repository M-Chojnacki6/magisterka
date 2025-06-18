import argparse
import numpy as np
import torch
import re
import os
from modules.dataloader import load_data_test
from modules.deepromoter import DeePromoter



L_model=["best_mcc" ,"best_precision" ,"best_recall"]
L_DEEP=["human_TATA", "human_nonTATA" ,"mouse_TATA" ,"mouse_nonTATA"] 

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')



def parse_args():

	parser = argparse.ArgumentParser(description='Script 1a test selected model DeePromoter on selected dataset',
		formatter_class=argparse.RawTextHelpFormatter)

	parser.add_argument('path_to_models',metavar='PATH', nargs=1, 
		help="""Path to results directory containing pre-trained models on data: 
human_TATA, "human_nonTATA, mouse_TATA nad mouse_nonTATA,
Provided models should habve extension: .pth""", default=None)
	parser.add_argument('ins',metavar='i', nargs=1,  help="""Txt file with sequences of length: 300.""",default=None)
	parser.add_argument('-o','--out', nargs=1, help="""Name of output .txt file, where results from model will be saved""",default=None)
	parser.add_argument('-t','--type', nargs=1, help="""Select category of the best model:
* 0 - best_mcc (default)
* 1 - best_precision
* 2 - best_recail""",default=0,choices = [0,1,2],type=int)
	parser.add_argument('-p','--save_score',  help="""Save value of the selected output neuron instead of category""",action= 'store_true')

	args = parser.parse_args()

	if args.path_to_models is None:
		print("!!!	Please give a path\n")

	elif os.path.isdir(args.path_to_models[0]): 
		PATH_TO_MODELS = os.path.normpath(args.path_to_models[0])
		for m in L_DEEP:
			if not os.path.isdir(os.path.join(PATH_TO_MODELS,m)):
				PATH_TO_MODELS=None
	else:
		print("!!!	Given path or file does not exist\n")

	if isinstance(args.type, int):
		t=args.type
	else:
		t=args.type[0]

	data_in=None
	if args.ins is None:
		print("!	Provide input file\n")
	elif os.path.isfile(args.ins[0]) or os.path.isfile(os.path.abspath(args.ins[0])):
		data_in = args.ins[0]
	else:
		print("!!!	Provided path to input file is incorrect\n")

	out=None
	if args.out is None:
		if not os.path.isdir("results"):
			os.mkdir("results")
		out=args.ins[0].split("/")[-1]
		out=f'results/{out.split(".")[0]}_{L_model[t]}_out.txt'
		if args.save_score:
			out=out.replace(".txt","_score.txt")
	elif os.path.isfile(args.out[0]) or os.path.isfile(os.path.abspath(args.out[0])) :
		print("provided output file exists; overwritting...\n")
		out = args.out[0]
	elif not re.search("//",args.out[0]):
		out = args.out[0]
	else:
		print("!!!!!!	Provided input path to output file is incorrect\n")



	if PATH_TO_MODELS and data_in:
		return [PATH_TO_MODELS, data_in, out,t,args.save_score]
	else:
		return None




def main():
	inputs=parse_args()
	
	if not inputs is None:
		print(f"{' '*13}> Run script_1a.py < \n\n{'#'*20}START{'#'*20}")
		print(f"\nDeePromoter models directory:\t{inputs[0]}\nInput file name:\t\t{inputs[1]}\nOutput file:\t\t\t{inputs[2]}\nModel type:\t\t\t{inputs[3]}\nSave score:\t\t\t{inputs[4]}")
		results=[[] for x in range(len(L_DEEP))]
		load = load_data_test(inputs[1],device=device)
		for m in range(len(L_DEEP)):
			# prepare model

			net = DeePromoter([27, 14, 7])
			net.to(device)
			net.load_state_dict(torch.load(os.path.join(inputs[0],L_DEEP[m],f"{L_model[inputs[3]]}.pth")))
			net.eval()

			

			for data in load:

				outputs = net(data[0])
				_, predicted = torch.max(outputs.data, 1)
				if inputs[4]:
					results[m].extend(outputs.detach().cpu().numpy())
				else:
					results[m].extend(predicted.cpu().numpy())
		with open(inputs[2],"w") as out:
			if inputs[4]:
				for y in range(len(L_DEEP)):
					out.write(f"{L_DEEP[y]}_0\t{L_DEEP[y]}_1\t")
				out.write("\n")
			for x in range(len(results[0])):


				for y in range(len(L_DEEP)):
					if inputs[4]:
						out.write(f"{results[y][x][0]}\t{results[y][x][1]}\t")
					else:
						out.write(f"{results[y][x]}\t")
				out.write("\n")
 


if __name__ == "__main__":
	main()