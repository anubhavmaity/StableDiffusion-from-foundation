# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/lectures/07_convolutions.ipynb.

# %% auto 0
__all__ = ['ds', 'images', 'labels', 'x_train', 'x_valid', 'y_train', 'y_valid', 'def_device', 'conv', 'to_device',
           'collate_device']

# %% ../nbs/lectures/07_convolutions.ipynb 2
import pickle, gzip, math, os, time, shutil, torch, matplotlib as mpl, numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from torch import nn
import torch.nn.functional as F
from pathlib import Path
from torch import tensor
from fastcore.test import test_close
import deeplake
from sklearn.model_selection import train_test_split

from torch.utils.data import default_collate
from collections import Counter
from typing import Mapping

from .training import *
from .datasets import * 

torch.manual_seed(42)

mpl.rcParams['image.cmap'] = 'gray'
torch.set_printoptions(precision=2, linewidth=125, sci_mode=False)
np.set_printoptions(precision=2, linewidth=125)

ds = deeplake.load('hub://activeloop/not-mnist-small', read_only=True, verbose=False)

images = ds.tensors['images'].numpy().reshape(-1, 784).astype('float32')
labels = ds.tensors['labels'].numpy().squeeze(-1).astype('int')

x_train, x_valid, y_train, y_valid = train_test_split(images, labels, test_size=0.2, random_state=1)
x_train, y_train, x_valid, y_valid = map(tensor, (x_train, y_train, x_valid, y_valid))
x_train, x_valid = x_train/255., x_valid/255.

# %% ../nbs/lectures/07_convolutions.ipynb 61
def conv(ni, nf, ks=3, stride=2, act=True):
    res = nn.Conv2d(ni, nf, stride=stride, kernel_size=ks, padding=ks//2)
    if act: res = nn.Sequential(res, nn.ReLU())
    return res

# %% ../nbs/lectures/07_convolutions.ipynb 69
def_device = 'mps' if torch.backends.mps.is_available() else 'cuda' if torch.cuda.is_available() else 'cpu'

def to_device(x, device=def_device):
    if isinstance(x, Mapping): return {k: v.to(device) for k, v in x.items()}
    return type(x)(o.to(device) for o in x)

def collate_device(b): 
    return to_device(default_collate(b))