# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/lectures/14_augment.ipynb.

# %% auto 0
__all__ = ['act_gr', 'summary']

# %% ../nbs/lectures/14_augment.ipynb 2
import fastcore.all as fc
from functools import partial

from datasets import load_dataset

from torch import nn
from torch import optim
import torch.nn.functional as F
import torchvision.transforms.functional as TF
from torch.optim import lr_scheduler
from torcheval.metrics import MulticlassAccuracy

from .conv import def_device
from .datasets import inplace
from .learner import MetricsCB, DeviceCB, ProgressCB, DataLoaders, Learner, TrainLearner, SingleBatchCB, MomentumLearner, lr_find
from .activations import Hooks
from .init import conv, GeneralRelu, init_weights, ActivationStats, set_seed
from .sgd import BatchSchedCB
from .resnet import ResBlock

# %% ../nbs/lectures/14_augment.ipynb 6
act_gr = partial(GeneralRelu, leak=0.1, sub=0.4)

# %% ../nbs/lectures/14_augment.ipynb 16
def _flops(x, h, w):
    if x.dim() < 3: return x.numel()
    if x.dim() == 4: return x.numel()*h*w
    raise Exception()

@fc.patch
def summary(self:Learner):
    res = '|Module|Input|Output|Num params|MFlops|\n|--|--|--|--|--|\n'
    totp, totf = 0, 0
    def _f(hook, mod, inp, outp):
        nonlocal res,totp,totf
        nparams = sum(o.numel() for o in mod.parameters())
        totp += nparams
        *_,h,w = outp.shape
        flops = sum(_flops(o, h, w) for o in mod.parameters())/1e6
        totf += flops
        res += f'{type(mod).__name__}|{tuple(inp[0].shape)}|{tuple(outp.shape)}|{nparams}|{flops:.1f}|\n'
    with Hooks(self.model, _f) as hooks: self.fit(1, lr=1, train=False, cbs=SingleBatchCB())
    print(f"Tot params: {totp}; MLFLOPS: {totf:.1f}")
    if fc.IN_NOTEBOOK:
        from IPython.display import Markdown
        return Markdown(res)
    else: print(res)