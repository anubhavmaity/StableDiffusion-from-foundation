# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/lectures/11_initializing.ipynb.

# %% auto 0
__all__ = ['clean_ipython_hist', 'clean_tb', 'clean_mem', 'BatchTransformCB', 'GeneralRelu', 'plot_func', 'init_weights',
           'lsuv_init', 'conv', 'get_model']

# %% ../nbs/lectures/11_initializing.ipynb 2
import pickle,gzip,math,os,time,shutil,torch,matplotlib as mpl,numpy as np,matplotlib.pyplot as plt
import sys,gc,traceback
import fastcore.all as fc
from collections.abc import Mapping
from pathlib import Path
from operator import attrgetter, itemgetter
from functools import partial
from copy import deepcopy
from contextlib import contextmanager

import torchvision.transforms.functional as TF, torch.nn.functional as F
from torch import tensor,nn,optim
from torch.utils.data import DataLoader,default_collate
from torch.nn import init
from torcheval.metrics import MulticlassAccuracy
from datasets import load_dataset,load_dataset_builder

from .datasets import *
from .conv import *
from .learner import *
from .activations import *

# %% ../nbs/lectures/11_initializing.ipynb 15
def clean_ipython_hist():
    if not 'get_ipython' in globals(): return
    ip = get_ipython()
    user_ns = ip.user_ns
    ip.displayhook.flush()
    pc = ip.displayhook.prompt_count + 1
    for n in range(1, pc): user_ns.pop('_i' + repr(n), None)
    user_ns.update(dict(_i='', _ii='', _iii=''))
    hm = ip.history_manager
    hm.input_hist_parsed[:] = [''] * pc
    hm.input_hist_raw[:] = [''] * pc
    hm._i = hm._ii = hm._iii = hm._iOO = ''

# %% ../nbs/lectures/11_initializing.ipynb 16
def clean_tb():
    # h/t Piotr Czapla
    if hasattr(sys, 'last_traceback'):
        traceback.clear_frames(sys.last_traceback)
        delattr(sys, 'last_traceback')
    if hasattr(sys, 'last_type'): delattr(sys, 'last_type')
    if hasattr(sys, 'last_value'): delattr(sys, 'last_value')

# %% ../nbs/lectures/11_initializing.ipynb 17
def clean_mem():
    clean_tb()
    clean_ipython_hist()
    gc.collect()
    torch.cuda.empty_cache()

# %% ../nbs/lectures/11_initializing.ipynb 88
class BatchTransformCB(Callback):
    def __init__(self, tfm): self.tfm = tfm
    def before_batch(self, learn): learn.batch = self.tfm(learn.batch)

# %% ../nbs/lectures/11_initializing.ipynb 97
class GeneralRelu(nn.Module):
    def __init__(self, leak=None, sub=None, maxv=None):
        super().__init__()
        self.leak,self.sub,self.maxv = leak,sub,maxv
    
    def forward(self, x):
        x = F.leaky_relu(x, self.leak) if self.leak is not None else F.relu(x)
        if self.sub is not None: x.sub_(self.sub)
        if self.maxv is not None: x.clamp_max(self.maxv)
        return x

# %% ../nbs/lectures/11_initializing.ipynb 98
def plot_func(f, start=-5., end=5., steps=100):
    x = torch.linspace(start, end, steps)
    plt.plot(x, f(x))
    plt.grid(True, which='both', ls='--')
    plt.axhline(y=0, color='k', linewidth=0.7)
    plt.axvline(x=0, color='k', linewidth=0.7)

# %% ../nbs/lectures/11_initializing.ipynb 102
def init_weights(m, leaky=0.):
    if isinstance(m, (nn.Conv1d, nn.Conv2d, nn.Conv3d, nn.Linear)): init.kaiming_normal_(m.weight, a=leaky)

# %% ../nbs/lectures/11_initializing.ipynb 111
def _lsuv_stats(hook, mod, inp, outp):
    acts = to_cpu(outp)
    hook.mean = acts.mean()
    hook.std = acts.std()

def lsuv_init(m, m_in, xb):
    h = Hook(m, _lsuv_stats)
    with torch.no_grad():
        
        while model(xb) is not None and (abs(h.std - 1) > 1e-3 or abs(h.mean) > 1e-3):
            m_in.bias -= h.mean
            m_in.weight.data /= h.std
    h.remove()

# %% ../nbs/lectures/11_initializing.ipynb 126
def conv(ni, nf, ks=3, stride=2, act=nn.ReLU, norm=None, bias=True):
    layers = [nn.Conv2d(ni, nf, stride=stride, kernel_size=ks, padding=ks//2, bias=bias)]
    if norm: layers.append(norm(nf))
    if act: layers.append(act())
    return nn.Sequential(*layers)

# %% ../nbs/lectures/11_initializing.ipynb 127
def get_model(act=nn.ReLU, nfs=None, norm=None, bias=True):
    if norm in (nn.BatchNorm1d, nn.BatchNorm2d, nn.BatchNorm3d): bias=False
    if nfs is None: nfs = [1, 8, 16, 32, 64]
    layers = [conv(nfs[i], nfs[i+1], act=act, norm=norm, bias=bias) for i in range(len(nfs) - 1)]
    return nn.Sequential(*layers, conv(nfs[-1], 10, act=None, norm=None), nn.Flatten()).to(def_device)
