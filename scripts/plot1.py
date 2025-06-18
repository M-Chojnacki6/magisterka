import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import subprocess
import argparse
import re
import os
import pathlib


names=["custom40", "custom41", "alt1", "alt2"]

def parse_args():

	parser = argparse.ArgumentParser(description="""Script performing simple analasys of results form
		nets custom[n]/alt[n] and clasyfying these nest according to found categories""",
		formatter_class=argparse.RawTextHelpFormatter)

	parser.add_argument('ins',metavar='i', nargs=1,  help="""Input _out.txt multisequence format after merging""",default=None)
	parser.add_argument('-o','--out', nargs=1, help="""Name of output directory. Default: images/""",default="images/")
	parser.add_argument('--reverse', action='store_true',help="""reverse shortening of the sequence -> when used with ss shorten end,
with se shorten start, with both ss and se -> remove values from middle of the sequence, e.g. for ss = 40 & se = 40:
ACTGATCTCGATCTGACTCTGGCTACATGCTGCTACGTTCGTCGTCACAACTCGCTGCGTCGTGAGACTGCTGAGACTCCGTATCGTGCTCCATGCGTAA

ACTGATCTCGATCTGACTCTGGCTACATGCTGCTACGTTXXXXXXXXXXXXXXXXXXXXXXGTGAGACTGCTGAGACTCCGTATCGTGCTCCATGCGTAA""")
	parser.add_argument('-s','--save_images', help="""Automaticly save output images to .png files in output directory;
name format: plot1_[pattern of input file]_[selected category]_[-rev].png """,action= 'store_true')


	args = parser.parse_args()

	data_in=None
	if args.ins is None:
		print("!	Provide input file\n")
	elif os.path.isfile(args.ins[0]) or os.path.isfile(os.path.abspath(args.ins[0])):
		data_in = args.ins[0]
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
		print("data path set to current directory")
		out=args.out
	if data_in and out:
		return [data_in, out,args.reverse,args.save_images]
	else:
		return None


"""
function fun() loading data from merged output files from nets custom
"""

"""
liczby:
* 0,1,2,3 oznaczają jednoznaczne przyporządkowanie do danego neuronu, tzn: jedna wartość !=0.5 reszta 0.5
	0:  promoter active
	1:  nonpromoter active
	2:  promoter inactive
	3:  nonpromoter inactive
* 4-9 oznaczają dwie możliwośći, analogicznie do:
	4: [1, 1, 0, 0]
	5: [1, 0, 1, 0]
	6: [1, 0, 0, 1]
	7: [0, 1, 1, 0]
	8: [0, 1, 0, 1]
	9:[0, 0, 1, 1]
* 10-13 trzy mnożliwości:
	10:[1, 1, 1, 0]
	11:[1, 1, 0, 1]
	12:[1, 0, 1, 1]
	13:[0, 1, 1, 1]
* 14,15 całkowicie niejasne:
	14:[1, 1, 1, 1]
	15:[0, 0, 0, 0]
"""


def category(vector):
	wp=np.zeros((4))
	for k in range(4):
		if vector[k]!=0.5:
			wp[k]=1
		else:
			wp[k]=0
	if sum(wp)==0:
		return 15
	elif sum(wp)==1:
		if wp[0]:
			return 0
		elif wp[1]:
			return 1
		elif wp[2]:
			return 2
		else:
			return 3
	elif sum(wp)==4:
		return 14
	elif sum(wp)==3:
		if not wp[0]:
			return 13
		elif not wp[1]:
			return 12
		elif not wp[2]:
			return 11
		else:
			return 10
	else:
		if wp[0]:
			if wp[1]:
				return 4
			elif wp[2]:
				return 5
			else:
				return 6
		elif wp[1]:
			if wp[2]:
				return 7
			else:
				return 8
		else:
			return 9


def simple_load(file):
	m=np.zeros((4,len(names)),dtype=int)
	
	with open(file,"r") as f:
		for line in f:
			line=line.split("\t")
			for model in range(len(names)):
				m[int(line[3+model])][model]+=1
	return m


cat=["p.a", "n.a.", "p.i", "n.i"]

def one_heatmap(data,pattern,ss,se,ds,rev,out):
	minmin=data.min()
	maxmax=data.max()
	if True:
		minmin=0
		maxmax=100
	fig, axs = plt.subplots(2,2,figsize=(10,10))
	im=[[0,0],[0,0]]
	for (i,j) in [(0,0),(0,1),(1,0),(1,1)]:
		im[i][j] = axs[i,j].imshow(data[j+2*i],vmin=minmin, vmax=maxmax,
			cmap=mpl.colormaps["coolwarm"])

		axs[i,j].set_xticks(np.arange(len(se)), labels=se)
		axs[i,j].set_yticks(np.arange(len(ss)), labels=ss)
		for h in range(len(ss)):
			for l in range(len(se)):
				text = axs[i,j].text(l, h, f"{data[i*2+j,h, l]}",
							   ha="center", va="center", color="k")
		axs[i,j].set_xlabel("shortened end",size=14)
		axs[i,j].set_ylabel("shortened start",size=14)
		axs[i,j].set_title(names[j+2*i])
		axs[i,j].invert_yaxis()
	fig.tight_layout()
	if out:
		fig.savefig(os.path.join(out, f"plot1_{pattern}_{ds}{rev}.png"))
	else:
		if rev:
			fig.suptitle(f"zeroed middle of input, {ds}",size=20)
		else:
			fig.suptitle(f"shortened input, {ds}",size=20)
		plt.show()


def make_heatmap(pattern,ss,se,ds="",rev=False,out=None):
	res=np.zeros((4,len(ss),len(se)),dtype=int)
	res_join=None
	tata=False
	### heatmap form reverse zeroed
	if ds=="pa":
		c=0
		res_join=np.zeros((4,len(ss),len(se)),dtype=int)
	elif ds=="na":
		c=1
	elif ds=="pi":
		c=2
		res_join=np.zeros((4,len(ss),len(se)),dtype=int)
	elif ds=="na":
		c=3
	elif "TATA" in ds:
		c=0
		tata=True
		res_join=np.zeros((4,len(ss),len(se)),dtype=int)
	r = ""
	if rev:
		r="-rev"
	for i in range(len(ss)):
		for j in range(len(se)):
			
			m = simple_load(f"{pattern}-s{ss[i]}-e{se[j]}{r}.txt")
			m = m*100/np.sum(m,axis=0)
			for k in range(4):
				res[k,i,j]=m[c,k] #+m[2,k]
				if not res_join is None:
					res_join[k,i,j]=m[0,k]+m[2,k]

#	prepare four heatmap on one plot
	pattern=pattern.split("/")[-1]
	if not tata:
		one_heatmap(res,pattern,ss,se,ds,r,out)	
	if not res_join is None:
		one_heatmap(res_join,pattern,ss,se,"p",r,out)	



def main():
	inputs=parse_args()
	
	if inputs:
		print(f"{' '*13}> Run plot1.py < \n\n{'#'*20}START{'#'*20}")
		print(f"\nInput files:\t\t\t{inputs[0]}\nOutput directory:\t\t{inputs[1]}\nreverse:\t\t\t{inputs[2]}\nSave output:\t\t\t{inputs[3]}")

		####
		ss = [50, 150, 250, 350, 450, 550, 650, 750, 850 ,950]
		se = [50, 150, 250, 350, 450, 550, 650 ,750, 850, 950]
		categories=["pa","na","pi","ni"]

		pattern=inputs[0].split(".")[0]
		if "TATA" in pattern:
			t="TATA"
			if "nonTATA" in pattern:
				t="nonTATA"
			if inputs[3]:
				make_heatmap(pattern,ss,se,t,inputs[2],inputs[1])
			else:
				make_heatmap(pattern,ss,se,t,inputs[2])
		for c in range(len(categories)):
			if categories[c] in pattern:
				if inputs[3]:
					make_heatmap(pattern,ss,se,categories[c],inputs[2],inputs[1])
				else:
					make_heatmap(pattern,ss,se,categories[c],inputs[2])


if __name__ == "__main__":
	main()
