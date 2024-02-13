import numpy as np
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.datasets import USPS
from torch.utils.data import DataLoader


# define residual unet
class UNet(nn.Module):
  def __init__(self, in_channels=1, out_channels=1, compact=4, residual=True, circular_padding=True, cat=True):
    super(UNet, self).__init__()
    self.name = 'unet'
    self.residual = residual
    self.cat = cat

    self.Maxpool = nn.MaxPool2d(kernel_size=2, stride=2)

    self.Conv1 = conv_block(ch_in=in_channels, ch_out=64, circular_padding=circular_padding)
    self.Conv2 = conv_block(ch_in=64, ch_out=128)
    self.Conv3 = conv_block(ch_in=128, ch_out=256)
    self.Conv4 = conv_block(ch_in=256, ch_out=512)

    self.Up4 = up_conv(ch_in=512, ch_out=256)
    self.Up_conv4 = conv_block(ch_in=512, ch_out=256)

    self.Up3 = up_conv(ch_in=256, ch_out=128)
    self.Up_conv3 = conv_block(ch_in=256, ch_out=128)

    self.Up2 = up_conv(ch_in=128, ch_out=64)
    self.Up_conv2 = conv_block(ch_in=128, ch_out=64)

    self.Conv_1x1 = nn.Conv2d(in_channels=64, out_channels=out_channels, kernel_size=1, stride=1, padding=0)
  
  def forward(self, x):
    # encoding path
    cat_dim = 1
    input = x
    x1 = self.Conv1(input)

    x2 = self.Maxpool(x1)
    x2 = self.Conv2(x2)

    x3 = self.Maxpool(x2)
    x3 = self.Conv3(x3)

    d3 = self.Up3(x3)
    if self.cat:
        d3 = torch.cat((x2, d3), dim=cat_dim)
        d3 = self.Up_conv3(d3)

    d2 = self.Up2(d3)
    if self.cat:
        d2 = torch.cat((x1, d2), dim=cat_dim)
        d2 = self.Up_conv2(d2)

    d1 = self.Conv_1x1(d2)

    out = d1+x if self.residual else d1
    return out

class conv_block(nn.Module):
  def __init__(self, ch_in, ch_out, circular_padding=False):
    super(conv_block, self).__init__()
    self.conv = nn.Sequential(
        nn.Conv2d(ch_in, ch_out, kernel_size=3, stride=1, padding=1, bias=True,
                  padding_mode='circular' if circular_padding else 'zeros'),
        nn.BatchNorm2d(ch_out),
        nn.ReLU(inplace=True),
        nn.Conv2d(ch_out, ch_out, kernel_size=3, stride=1, padding=1, bias=True),
        nn.BatchNorm2d(ch_out),
        nn.ReLU(inplace=True)
    )
  def forward(self, x):
    x = self.conv(x)
    return x

class up_conv(nn.Module):
  def __init__(self, ch_in, ch_out):
    super(up_conv, self).__init__()
    self.up = nn.Sequential(
        nn.Upsample(scale_factor=2),
        nn.Conv2d(ch_in, ch_out, kernel_size=3, stride=1, padding=1, bias=True),
        nn.BatchNorm2d(ch_out),
        nn.ReLU(inplace=True)
    )

  def forward(self, x):
    x = self.up(x)
    return x