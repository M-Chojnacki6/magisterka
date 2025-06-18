import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import subprocess
import argparse
import re
import os
import pathlib


names=["custom40", "custom41", "alt1", "alt2"]

def parse_args():

	parser = argparse.ArgumentParser(description="""Plot train and validation losses based on given table""",
		formatter_class=argparse.RawTextHelpFormatter)

	parser.add_argument('ins',metavar='i', nargs=1,  help="""Input [PATH]/[MODELNAME]_train_results.tsv file generated during training.""",default=None)
	parser.add_argument('-o','--out', nargs=1, help="""Name of output directory. Default: images/""",default="images/")

	parser.add_argument('-s','--save_images', help="""Automaticly save output images (both from training data and validation) to .png files in output directory;
name format: [MODELNAME]_loss.png """,action= 'store_true')


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
		print("data path set to directory ./images")

		out=args.out
		if not os.path.isdir(out):
			os.path.mkdir(out)
	if data_in and out:
		return [data_in, out,args.save_images]
	else:
		return None



def simple_load(file):
	train_loss=[]
	valid_loss=[]
	
	with open(file,"r") as f:
		line0=f.readline()
		categories=[]
		for c in line0.split("\t"):
			if "AUC" in c:
				categories.append(c.split("-")[1].strip())
				train_loss.append([])
				valid_loss.append([])
		for line in f:
			line=line.split("\t")
			loss=line[2].strip()
			if line[1].strip()=="train":
				loss=loss.split(",")
				for l in range(len(loss)):
					train_loss[l].append(float(loss[l]))


			elif line[1].strip()=="valid":
				loss=loss.split(",")
				for l in range(len(loss)):
					valid_loss[l].append(float(loss[l]))
	return [train_loss,valid_loss,categories]


def make_simple_plot(train_data,val_data,categories,output_name,ifsave=False):
	cmap=["b","y","g","r","c"]
	xs = [x for x in range(len(val_data[0]))]
	
	fig,axs = plt.subplots(nrows=1,ncols=2,figsize=(10,10),layout='constrained')
	
#	sns.set_theme(style="darkgrid")
	ymax=max(max([max(x) for x in train_data]),max([max(x) for x in val_data]))
	ymin=min(min([min(x) for x in train_data]),min([min(x) for x in val_data]))
	for i,s in enumerate(train_data):

		axs[0].plot(xs, train_data[i], f"{cmap[i]}.",label=categories[i])
		axs[0].set_xlim(0,xs[-1]+1)
		axs[0].set_ylim(ymin*0.95,ymax*1.05)
		axs[0].set_ylabel("Loss",size=15)
		axs[0].set_xlabel("Epochs",size=15)
		axs[0].set_title("Training",size=20)
		axs[0].grid(visible=True,axis="both")


		axs[1].plot(xs, val_data[i], f"{cmap[i]}.")
		axs[1].set_xlim(0,xs[-1]+1)
		axs[1].set_ylim(ymin*0.95,ymax*1.05)
		axs[1].set_ylabel("Loss",size=15)
		axs[1].set_xlabel("Epochs",size=15)
		axs[1].set_title("Validation",size=20)
		axs[1].grid(visible=True,axis="both")

	fig.legend(loc='outside lower center',ncol=len(val_data))
	if ifsave:
		plt.savefig(output_name)
	else:
		plt.show()





def main():
	inputs=parse_args()
	
	if inputs:
		print(f"{' '*13}> Run plot_losses.py < \n\n{'#'*20}START{'#'*20}")
		print(f"\nInput files:\t\t\t{inputs[0]}\nOutput directory:\t\t{inputs[1]}\nSave output:\t\t\t{inputs[2]}")

		train_loss,valid_loss,categories = simple_load(inputs[0])
		output_name=inputs[0].split("/")[-1].replace("train_results.tsv","")
		make_simple_plot(train_loss,valid_loss,categories,os.path.join(inputs[1],f"{output_name}loss.png"),ifsave=inputs[2])

if __name__ == "__main__":
	main()