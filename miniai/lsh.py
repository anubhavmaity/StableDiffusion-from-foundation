# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_locality_sensitive_hashing_lsh.ipynb.

# %% auto 0
__all__ = ['LSH']

# %% ../nbs/02_locality_sensitive_hashing_lsh.ipynb 3
import matplotlib.pyplot as plt
import torch
from fastcore.all import patch

# %% ../nbs/02_locality_sensitive_hashing_lsh.ipynb 4
torch.manual_seed(42)
torch.set_printoptions(precision=3, linewidth=140, sci_mode=False)

# %% ../nbs/02_locality_sensitive_hashing_lsh.ipynb 6
class LSH:
    def __init__(self, dim, nht, hl):
        self.dimensions = dim # dimensions of the data
        self.num_hash_tables = nht # number of hash tables
        self.hash_length = hl # hash length
        self.hash_table = torch.randn(self.num_hash_tables, self.hash_length, self.dimensions) # the hashtable

# %% ../nbs/02_locality_sensitive_hashing_lsh.ipynb 11
@patch
def hashing(self:LSH, query): 
    return (((query[:, None, None]) * self.hash_table).sum(-1) >= 0).long()

# %% ../nbs/02_locality_sensitive_hashing_lsh.ipynb 29
@patch
def query_neigbours(self:LSH, query, data, data_hash, neighbours=10):
    query_hash = self.hashing(query)
    result = ( (query_hash * data_hash).sum(-1) / data_hash.sum(-1) ) == 1
    result_indices = torch.nonzero(torch.any(result, dim=1)).flatten()
    
    dist = ((query - data[result_indices]) ** 2).sum(-1).sqrt()
    sorted_dist, idx = torch.sort(dist)
    
    
    return sorted_dist[:neighbours], result_indices[idx[:neighbours]]