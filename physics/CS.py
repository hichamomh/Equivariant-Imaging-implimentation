import torch
import os
import numpy as np



class CS():
  def __init__(self, d, D, img_shape, dtype=torch.float, device='cuda:0'):
    self.img_shape = img_shape
    fname = './dataset/forw_cs_{}x{}.pt'.format(d, D)
    if os.path.exists(fname):
      A, A_dagger = torch.load(fname)
    else:
      A = np.random.randn(d, D) / np.sqrt(d)
      A_dagger = np.linalg.pinv(A)
      torch.save([A, A_dagger], fname)
      print('CS matrix has been created and saved at {}'.format(fname))
    self._A = torch.from_numpy(A).type(dtype).to(device)
    self._A_dagger = torch.from_numpy(A_dagger).type(dtype).to(device)

  def A(self, x):
    y = torch.einsum('in, mn->im', x.reshape(x.shape[0], -1), self._A)
    return y

  def A_dagger(self, y):
    N, C, H, W = y.shape[0], self.img_shape[0], self.img_shape[1], self.img_shape[2]
    x = torch.einsum('im, nm->in', y, self._A_dagger)
    x = x.reshape(N, C, H, W)
    return x