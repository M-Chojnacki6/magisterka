import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import subprocess
import argparse
import re
import os



names=["custom40", "custom41", "alt1", "alt2"]

def parse_args():

	parser = argparse.ArgumentParser(description="""Plot train and validation AUC based on given table""",
		formatter_class=argparse.RawTextHelpFormatter)

	parser.add_argument('ins',metavar='i', nargs=1,  help="""Input [PATH]/[MODELNAME]_train_results.tsv file generated during training.""",default=None)
	parser.add_argument('-o','--out', nargs=1, help="""Name of output directory. Default: images/""",default="images/")

	parser.add_argument('-s','--save_images', help="""Automaticly save output images (both from training data and validation) to .png files in output directory;
name format: [MODELNAME]_AUC.png """,action= 'store_true')


	args = parser.parse_args()

	data_in=None
	if args.ins is None:
		print("!	Provide input file\n")
	elif os.path.isfile(args.ins[0]) or os.path.isfile(os.path.abspath(args.ins[0])):
		data_in = args.ins[0]
		print(data_in[-18:])
		if not re.search("_train_results.tsv$",data_in):
			print(f"Provided input file: {data_in} doesnn't contain recognized suffix: _train_results.tsv\nplotting aborted")
			data_in=None
	else:
		print("!!!	Provided path and/or file does not exist\n")

	out=None
	if isinstance(args.out, list):
		if os.path.isdir(args.out[0]):
			out=os.path.abspath(args.out[0])
		else:
			print("provided path: {args.out[0]} does not exist; changing to current directory")
			out= os.getcwd()
	else:
#		print("data path set to directory ./images")

		out=args.out
		if not os.path.isdir(out):
			os.path.mkdir(out)
	if data_in and out:
		return [data_in, out,args.save_images]
	else:
		return None



def simple_load_AUC(file):
	train_AUC=[]
	valid_AUC=[]
	
	with open(file,"r") as f:
		line0=f.readline()
		categories=[]
		for c in line0.split("\t"):
			if "AUC" in c:
				categories.append(c.split("-")[1].strip())
				train_AUC.append([])
				valid_AUC.append([])
		for line in f:
			line=line.split("\t")

			for l in range(len(categories)):
				AUC=line[l+5].strip().split(",")
				if line[1].strip()=="train":
					train_AUC[l].append(float(AUC[l]))


				elif line[1].strip()=="valid":
					valid_AUC[l].append(float(AUC[l]))
	return [train_AUC,valid_AUC,categories]


def make_simple_plot_AUC(train_data,val_data,categories,output_name,ifsave=False):
	cmap=["b","y","g","r","c"]
	xs = [x for x in range(len(val_data[0]))]
	
	fig,axs = plt.subplots(nrows=len(val_data),ncols=2,figsize=(len(val_data)*2,10),layout='constrained',sharex=True)

	for i in range(len(train_data)):

		axs[i,0].plot(xs, train_data[i], f"{cmap[i]}.",label=categories[i])
		axs[i,0].set_xlim(0,xs[-1]+1)
		axs[i,0].set_ylim(ymin=0,ymax=1)
		axs[i,0].set_ylabel(f"AUC -\n{categories[i]}",size=10)
		axs[i,0].yaxis.label.set_color(cmap[i])
		axs[i,0].grid(visible=True,axis="both")


		axs[i,1].plot(xs, val_data[i], f"{cmap[i]}.")
		axs[i,1].set_xlim(0,xs[-1]+1)
		axs[i,1].set_ylim(ymin=0,ymax=1)
		axs[i,1].set_ylabel(f"AUC -\n{categories[i]}",size=10)
		axs[i,1].yaxis.label.set_color(cmap[i])
	
		axs[i,1].grid(visible=True,axis="both")
		if i==0:
			axs[i,0].set_title("Training",size=20)
			axs[i,1].set_title("Validation",size=20)
		elif i==len(train_data)-1:
			axs[i,1].set_xlabel("Epochs",size=15)
			axs[i,0].set_xlabel("Epochs",size=15)	

	fig.legend(loc='outside lower center',ncol=len(val_data))
	if ifsave:
		plt.savefig(output_name)
	else:
		plt.show()





def main():
	inputs=parse_args()
	
	if inputs:
		print(f"{' '*13}> Run plot_AUC.py < \n\n{'#'*20}START{'#'*20}")
		print(f"\nInput files:\t\t\t{inputs[0]}\nOutput directory:\t\t{inputs[1]}\nSave output:\t\t\t{inputs[2]}")

		train_AUC,valid_AUC,categories = simple_load_AUC(inputs[0])
		output_name=inputs[0].split("/")[-1].replace("train_results.tsv","")
		make_simple_plot_AUC(train_AUC,valid_AUC,categories,os.path.join(inputs[1],f"{output_name}AUC.png"),ifsave=inputs[2])

if __name__ == "__main__":
	main()