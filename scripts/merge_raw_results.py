import argparse
import subprocess
import numpy as np
import os
import re


names=["custom40", "custom41", "alt1", "alt2"]

def parse_args():

	parser = argparse.ArgumentParser(description="""Auxiliary script which merge results from all four RegSeqNet models:
(custom40, custom41, alt1, alt2) for one dataset. Data will be saved in exact order by models""",formatter_class=argparse.RawTextHelpFormatter)

	parser.add_argument('-p','--path', nargs=1, help="""Path to directotry with files to merge; default: ./""",default=os.getcwd())

	parser.add_argument('i', nargs=len(names), help=f"""List of filenames to merge;
each filename should contains name of the model in format [...]_[model]_[...];""",default=None)

	parser.add_argument('-o','--out', nargs=1, help="""Name of output file with merged data; 
format:
id;\tstrand;\ttrue cat.;\tcustom40 cat.;\tcustom41 cat.;\talt1 cat.;\talt2 cat.;\tcustom40 
 vec.;\tcustom41 vec;\talt1 vec;\talt2 vec;""",default=None)

	parser.add_argument('-l','--lines', nargs=1,type=int, help="""Expected number of lines to merge; 
default: number of line in []_custom41_[] output file""",default=None)


	args = parser.parse_args()

	path=None
	if isinstance(args.path, list):
		if os.path.isdir(args.path[0]):
			path=os.path.abspath(args.path[0])
		else:
			print("provided path: {args.path[0]} does not exist; changing to current directory")
			path = os.getcwd()
	else:
		print("data path set to current directory")
		path=args.path

	file_names=[]
	ff=True

	if args.i is None:
		print("pleas provide names of input files")
	else:
		for pattern in names:
			f=True
			for ins in args.i:
				if pattern in ins:
					if os.path.isfile(os.path.join(path,ins)):
						f=False
#						print(f"output file from model:\t{pattern}\tfound")
						file_names.append(ins)
			if f:
				print(f"output file from model:\t{pattern}\tMISSING!")
				ff=False


	l=0
	if args.lines is None:
		if ff:
			res=subprocess.run([f"wc", "-l" , f"{os.path.join(path,file_names[0])}"], # 
			stdout=subprocess.PIPE)
			if res.returncode==0:
				l=int(res.stdout.decode("utf-8").strip().split()[0])
	elif isinstance(args.lines, int):
		if args.lines>0:
			l=args.lines

	out=None
	if args.out is None:
		if ff:
			out=re.sub(f"{names[0]}_","",file_names[0])

	elif os.path.isdir(os.path.dirname(args.out[0])):
		out=args.out[0]

	if path and ff and l and out:
		return [path,file_names,l,out]
	else:
		return None

"""
function which() finds the most liely output neuron from modle output by the highest values

# line - string, output vector from selected model, e.g.: "[0.5, 0.9894, 0.7521, 0.5]"
"""
def which(line):
	line=line[3][1:]
	line=line[:-2]
	r=[float(l) for l in line.split(",")]
	res=0
	tmp=0
	for y in range(4):
		if tmp<r[y]:
			res=y
			tmp=r[y]
	return res

def main():
	inputs=parse_args()
	
	if inputs:
		print(f"{' '*13}> Run merge raw results.py < \n\n{'#'*20}START{'#'*20}")
		print(f"\nPath to files:\t\t\t{inputs[0]}\nInput files:\t\t\t{inputs[1]}\nOutput file:\t\t\t{inputs[3]}\nNumber of lines to merge:\t{inputs[2]}")
		f_c40=open(f"{os.path.join(inputs[0],inputs[1][0])}")
		f_c41=open(f"{os.path.join(inputs[0],inputs[1][1])}")
		f_a1=open(f"{os.path.join(inputs[0],inputs[1][2])}")
		f_a2=open(f"{os.path.join(inputs[0],inputs[1][3])}")
		
		f_out=open(f"{os.path.join(inputs[0],inputs[3])}","w")
		f_list=[f_c40,f_c41,f_a1,f_a2]
		data=["" for x in range(len(names))]
		for ind in range(inputs[2]):
			c40=f_c40.readline().split("\t")
			data[0]=c40[3][:-1]
			f_out.write(f"{c40[0]}\t{c40[1]}\t{c40[2]}\t{which(c40)}\t")
			for x in range(1,len(names)):
				d=f_list[x].readline().split("\t")
				f_out.write(f"{which(d)}\t")
				data[x]=d[3][:-1]
			for x in range(len(names)-1):
				f_out.write(f"{data[x]}\t")
			f_out.write(f"{data[len(names)-1]}\n")	



		f_c40.close()
		f_c41.close()
		f_a1.close()
		f_a2.close()			
		f_out.close()

if __name__ == "__main__":
	main()
