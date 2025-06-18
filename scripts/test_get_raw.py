import torch
import math
import argparse
from icecream import ic

from modules.deepromoter import DeePromoter
from modules.dataloader import load_data_test

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

"""
Adapted from orginal DeePromoter github code:

https://github.com/egochao/DeePromoter/test.py
"""

###
#backend = torch.backends.quantized.backend
#print(f"Currently using backend: {backend}")
#torch.backends.nnpack.enabled = False
###



def test_get_raw(data_path, pretrain, ker=None):
    if ker is None:
        ker = [27, 14, 7]

    dataloader = load_data_test(data_path, device=device)

    # model define
    net = DeePromoter(ker)
    net.to(device)

    net.load_state_dict(torch.load(pretrain))

    net.eval()
    pred_result = list()
    for load in [dataloader]:
        pred_list = list()
        for data in load:
            inputs = data[0]
            labels = data[1]
            outputs = net(inputs)
            pred_result.append(outputs)
    
    pred_result=torch.cat(pred_result,axis=0)

    return pred_result.detach().numpy()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Get raw results from DeePromoter models on selected dataset (two values corresponding to probablility of each class: 0 - negative, 1 - positive )""")
    parser.add_argument(
        "-d",
        "--data",
        type=str,
        required=True,
        help="path to dataset(txt file)",
    )
    parser.add_argument("-w", "--weight", type=str, help="Path to pre-train")
    args = parser.parse_args()

    output = test_get_raw(args.data, args.weight)

    with open("infer_raw_results.txt", "w") as f:
        ic("Save the results to infer_raw_results.txt")
        for out in output:
            f.write(f"{out[0]},{out[1]}\n")
