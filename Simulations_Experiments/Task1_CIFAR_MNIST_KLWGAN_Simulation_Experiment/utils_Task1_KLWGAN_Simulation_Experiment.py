# Acknowledgement: Thanks to the repository: [KLWGAN](https://github.com/ermongroup/f-wgan/tree/master/image_generation)
# Acknowledgement: Thanks to the repositories: [PyTorch-Template](https://github.com/victoresque/pytorch-template "PyTorch Template"), [Generative Models](https://github.com/shayneobrien/generative-models/blob/master/src/f_gan.py), [f-GAN](https://github.com/nowozin/mlss2018-madrid-gan), and [KLWGAN](https://github.com/ermongroup/f-wgan/tree/master/image_generation)
# Also, thanks to the repositories: [Negative-Data-Augmentation](https://anonymous.4open.science/r/99219ca9-ff6a-49e5-a525-c954080de8a7/), [Negative-Data-Augmentation-Paper](https://openreview.net/forum?id=Ovp8dvB8IBH), and [BigGAN](https://github.com/ajbrock/BigGAN-PyTorch)
from __future__ import print_function
from torch.optim.optimizer import Optimizer
import math
import sys
import os
import numpy as np
import time
import datetime
import json
import pickle
from argparse import ArgumentParser
from tqdm import tqdm, trange
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
import datasets as dset
def prepare_parser():
    usage = 'Parser for all scripts.'
    parser = ArgumentParser(description=usage)
    parser.add_argument('--dataset', type=str, default='I128_hdf5',
        help='Which Dataset to train on, out of I128, I256, C10, C100;'
        'Append "_hdf5" to use the hdf5 version for ISLVRC '
        '(default: %(default)s)')
    parser.add_argument('--augment', action='store_true', default=False,
        help='Augment with random crops and flips (default: %(default)s)')
    parser.add_argument(
        '--num_workers', type=int, default=8,
        help='Number of dataloader workers; consider using less for HDF5'
        '(default: %(default)s)')
    parser.add_argument(
        '--no_pin_memory', action='store_false', dest='pin_memory', default=True,
        help='Pin data into memory through dataloader? (default: %(default)s)')
    parser.add_argument(
        '--shuffle', action='store_true', default=False,
        help='Shuffle the data (strongly recommended)? (default: %(default)s)')
    parser.add_argument(
        '--load_in_mem', action='store_true', default=False,
        help='Load all data into memory? (default: %(default)s)')
    parser.add_argument(
        '--use_multiepoch_sampler', action='store_true', default=False,
        help='Use the multi-epoch sampler for dataloader? (default: %(default)s)')
    parser.add_argument(
        '--loss_type', type=str, default='hinge',
        help='use what type of loss')
    parser.add_argument(
        '--model', type=str, default='BigGAN',
        help='Name of the model module (default: %(default)s)')
    parser.add_argument(
        '--G_param', type=str, default='SN',
        help='Parameterization style to use for G, spectral norm (SN) or SVD (SVD)'
        ' or None (default: %(default)s)')
    parser.add_argument(
        '--D_param', type=str, default='SN',
        help='Parameterization style to use for D, spectral norm (SN) or SVD (SVD)'
        ' or None (default: %(default)s)')
    parser.add_argument(
        '--G_ch', type=int, default=64, help='Channel multiplier for G (default: %(default)s)')
    parser.add_argument(
        '--D_ch', type=int, default=64,
        help='Channel multiplier for D (default: %(default)s)')
    parser.add_argument(
        '--G_depth', type=int, default=1,
        help='Number of resblocks per stage in G? (default: %(default)s)')
    parser.add_argument(
        '--D_depth', type=int, default=1,
        help='Number of resblocks per stage in D? (default: %(default)s)')
    parser.add_argument(
        '--D_thin', action='store_false', dest='D_wide', default=True,
        help='Use the SN-GAN channel pattern for D? (default: %(default)s)')
    parser.add_argument(
        '--G_shared', action='store_true', default=False,
        help='Use shared embeddings in G? (default: %(default)s)')
    parser.add_argument(
        '--shared_dim', type=int, default=0,
        help='G''s shared embedding dimensionality; if 0, will be equal to dim_z. '
        '(default: %(default)s)')
    parser.add_argument(
        '--dim_z', type=int, default=128,
        help='Noise dimensionality: %(default)s)')
    parser.add_argument(
        '--z_var', type=float, default=1.0,
        help='Noise variance: %(default)s)')
    parser.add_argument(
        '--hier', action='store_true', default=False,
        help='Use hierarchical z in G? (default: %(default)s)')
    parser.add_argument(
        '--cross_replica', action='store_true', default=False,
        help='Cross_replica batchnorm in G?(default: %(default)s)')
    parser.add_argument(
        '--mybn', action='store_true', default=False,
        help='Use my batchnorm (which supports standing stats?) %(default)s)')
    parser.add_argument(
        '--G_nl', type=str, default='relu',
        help='Activation function for G (default: %(default)s)')
    parser.add_argument(
        '--D_nl', type=str, default='relu',
        help='Activation function for D (default: %(default)s)')
    parser.add_argument(
        '--G_attn', type=str, default='64',
        help='What resolutions to use attention on for G (underscore separated) '
        '(default: %(default)s)')
    parser.add_argument(
        '--D_attn', type=str, default='64',
        help='What resolutions to use attention on for D (underscore separated) '
        '(default: %(default)s)')
    parser.add_argument(
        '--norm_style', type=str, default='bn',
        help='Normalizer style for G, one of bn [batchnorm], in [instancenorm], '
        'ln [layernorm], gn [groupnorm] (default: %(default)s)')
    parser.add_argument(
        '--seed', type=int, default=0,
        help='Random seed to use; affects both initialization and '
        ' dataloading. (default: %(default)s)')
    parser.add_argument(
        '--G_init', type=str, default='ortho',
        help='Init style to use for G (default: %(default)s)')
    parser.add_argument(
        '--D_init', type=str, default='ortho',
        help='Init style to use for D(default: %(default)s)')
    parser.add_argument(
        '--skip_init', action='store_true', default=False,
        help='Skip initialization, ideal for testing when ortho init was used '
        '(default: %(default)s)')
    parser.add_argument(
        '--conditional', action='store_true', default=False,
        help='run unconditional BigGAN')
    parser.add_argument(
        '--G_lr', type=float, default=5e-5,
        help='Learning rate to use for Generator (default: %(default)s)')
    parser.add_argument(
        '--D_lr', type=float, default=2e-4,
        help='Learning rate to use for Discriminator (default: %(default)s)')
    parser.add_argument(
        '--G_B1', type=float, default=0.0,
        help='Beta1 to use for Generator (default: %(default)s)')
    parser.add_argument(
        '--D_B1', type=float, default=0.0,
        help='Beta1 to use for Discriminator (default: %(default)s)')
    parser.add_argument(
        '--G_B2', type=float, default=0.999,
        help='Beta2 to use for Generator (default: %(default)s)')
    parser.add_argument(
        '--D_B2', type=float, default=0.999,
        help='Beta2 to use for Discriminator (default: %(default)s)')
    parser.add_argument(
        '--batch_size', type=int, default=64,
        help='Default overall batchsize (default: %(default)s)')
    parser.add_argument(
        '--G_batch_size', type=int, default=0,
        help='Batch size to use for G; if 0, same as D (default: %(default)s)')
    parser.add_argument(
        '--num_G_accumulations', type=int, default=1,
        help='Number of passes to accumulate G''s gradients over '
        '(default: %(default)s)')
    parser.add_argument(
        '--num_D_steps', type=int, default=2,
        help='Number of D steps per G step (default: %(default)s)')
    parser.add_argument(
        '--num_D_accumulations', type=int, default=1,
        help='Number of passes to accumulate D''s gradients over '
        '(default: %(default)s)')
    parser.add_argument(
        '--split_D', action='store_true', default=False,
        help='Run D twice rather than concatenating inputs? (default: %(default)s)')
    parser.add_argument(
        '--num_epochs', type=int, default=100,
        help='Number of epochs to train for (default: %(default)s)')
    parser.add_argument(
        '--parallel', action='store_true', default=False,
        help='Train with multiple GPUs (default: %(default)s)')
    parser.add_argument(
        '--G_fp16', action='store_true', default=False,
        help='Train with half-precision in G? (default: %(default)s)')
    parser.add_argument(
        '--D_fp16', action='store_true', default=False,
        help='Train with half-precision in D? (default: %(default)s)')
    parser.add_argument(
        '--D_mixed_precision', action='store_true', default=False,
        help='Train with half-precision activations but fp32 params in D? '
        '(default: %(default)s)')
    parser.add_argument(
        '--G_mixed_precision', action='store_true', default=False,
        help='Train with half-precision activations but fp32 params in G? '
        '(default: %(default)s)')
    parser.add_argument(
        '--accumulate_stats', action='store_true', default=False,
        help='Accumulate "standing" batchnorm stats? (default: %(default)s)')
    parser.add_argument(
        '--num_standing_accumulations', type=int, default=16,
        help='Number of forward passes to use in accumulating standing stats? '
        '(default: %(default)s)')
    parser.add_argument(
        '--G_eval_mode', action='store_true', default=False,
        help='Run G in eval mode (running/standing stats?) at sample/test time? '
        '(default: %(default)s)')
    parser.add_argument(
        '--save_every', type=int, default=2000,
        help='Save every X iterations (default: %(default)s)')
    parser.add_argument(
        '--num_save_copies', type=int, default=2,
        help='How many copies to save (default: %(default)s)')
    parser.add_argument(
        '--num_best_copies', type=int, default=2,
        help='How many previous best checkpoints to save (default: %(default)s)')
    parser.add_argument(
        '--which_best', type=str, default='FID',
        help='Which metric to use to determine when to save new "best"'
        'checkpoints, one of IS or FID (default: %(default)s)')
    parser.add_argument(
        '--no_fid', action='store_true', default=False,
        help='Calculate IS only, not FID? (default: %(default)s)')
    parser.add_argument('--start_eval', type=int, default=50, 
        help='number of epochs after the model begins evaluation.')
    parser.add_argument(
        '--test_every', type=int, default=5000,
        help='Test every X iterations (default: %(default)s)')
    parser.add_argument(
        '--num_inception_images', type=int, default=10000,
        help='Number of samples to compute inception metrics with '
        '(default: %(default)s)')
    parser.add_argument(
        '--hashname', action='store_true', default=False,
        help='Use a hash of the experiment name instead of the full config '
        '(default: %(default)s)')
    parser.add_argument(
        '--base_root', type=str, default='',
        help='Default location to store all weights, samples, data, and logs '
        ' (default: %(default)s)')
    parser.add_argument(
        '--data_root', type=str, default='data',
        help='Default location where data is stored (default: %(default)s)')
    parser.add_argument(
        '--weights_root', type=str, default='weights',
        help='Default location to store weights (default: %(default)s)')
    parser.add_argument(
        '--logs_root', type=str, default='logs',
        help='Default location to store logs (default: %(default)s)')
    parser.add_argument(
        '--samples_root', type=str, default='samples',
        help='Default location to store samples (default: %(default)s)')
    parser.add_argument(
        '--pbar', type=str, default='mine',
        help='Type of progressbar to use; one of "mine" or "tqdm" '
        '(default: %(default)s)')
    parser.add_argument(
        '--name_suffix', type=str, default='',
        help='Suffix for experiment name for loading weights for sampling '
        '(consider "best0") (default: %(default)s)')
    parser.add_argument(
        '--experiment_name', type=str, default='',
        help='Optionally override the automatic experiment naming with this arg. '
        '(default: %(default)s)')
    parser.add_argument(
        '--config_from_name', action='store_true', default=False,
        help='Use a hash of the experiment name instead of the full config '
        '(default: %(default)s)')
    parser.add_argument(
        '--ema', action='store_true', default=False,
        help='Keep an ema of G''s weights? (default: %(default)s)')
    parser.add_argument(
        '--ema_decay', type=float, default=0.9999,
        help='EMA decay rate (default: %(default)s)')
    parser.add_argument(
        '--use_ema', action='store_true', default=False,
        help='Use the EMA parameters of G for evaluation? (default: %(default)s)')
    parser.add_argument(
        '--ema_start', type=int, default=0,
        help='When to start updating the EMA weights (default: %(default)s)')
    parser.add_argument(
        '--adam_eps', type=float, default=1e-8,
        help='epsilon value to use for Adam (default: %(default)s)')
    parser.add_argument(
        '--BN_eps', type=float, default=1e-5,
        help='epsilon value to use for BatchNorm (default: %(default)s)')
    parser.add_argument(
        '--SN_eps', type=float, default=1e-8,
        help='epsilon value to use for Spectral Norm(default: %(default)s)')
    parser.add_argument(
        '--num_G_SVs', type=int, default=1,
        help='Number of SVs to track in G (default: %(default)s)')
    parser.add_argument(
        '--num_D_SVs', type=int, default=1,
        help='Number of SVs to track in D (default: %(default)s)')
    parser.add_argument(
        '--num_G_SV_itrs', type=int, default=1,
        help='Number of SV itrs in G (default: %(default)s)')
    parser.add_argument(
        '--num_D_SV_itrs', type=int, default=1,
        help='Number of SV itrs in D (default: %(default)s)')
    parser.add_argument(
        '--G_ortho', type=float, default=0.0,
        help='Modified ortho reg coefficient in G(default: %(default)s)')
    parser.add_argument(
        '--D_ortho', type=float, default=0.0,
        help='Modified ortho reg coefficient in D (default: %(default)s)')
    parser.add_argument(
        '--toggle_grads', action='store_true', default=True,
        help='Toggle D and G''s "requires_grad" settings when not training them? '
        ' (default: %(default)s)')
    parser.add_argument(
        '--which_train_fn', type=str, default='GAN',
        help='How2trainyourbois (default: %(default)s)')
    parser.add_argument(
        '--load_weights', type=str, default='',
        help='Suffix for which weights to load (e.g. best0, copy0) '
        '(default: %(default)s)')
    parser.add_argument(
        '--resume', action='store_true', default=False,
        help='Resume training? (default: %(default)s)')
    parser.add_argument(
        '--logstyle', type=str, default='%3.3e',
        help='What style to use when logging training metrics?'
        'One of: %#.#f/ %#.#e (float/exp, text),'
        'pickle (python pickle),'
        'npz (numpy zip),'
        'mat (MATLAB .mat file) (default: %(default)s)')
    parser.add_argument(
        '--log_G_spectra', action='store_true', default=False,
        help='Log the top 3 singular values in each SN layer in G? '
        '(default: %(default)s)')
    parser.add_argument(
        '--log_D_spectra', action='store_true', default=False,
        help='Log the top 3 singular values in each SN layer in D? '
        '(default: %(default)s)')
    parser.add_argument(
        '--sv_log_interval', type=int, default=10,
        help='Iteration interval for logging singular values '
        ' (default: %(default)s)')
    return parser
def add_sample_parser(parser):
    parser.add_argument(
        '--sample_npz', action='store_true', default=False,
        help='Sample "sample_num_npz" images and save to npz? '
        '(default: %(default)s)')
    parser.add_argument(
        '--sample_num_npz', type=int, default=10000,
        help='Number of images to sample when sampling NPZs '
        '(default: %(default)s)')
    parser.add_argument(
        '--sample_sheets', action='store_true', default=False,
        help='Produce class-conditional sample sheets and stick them in '
        'the samples root? (default: %(default)s)')
    parser.add_argument(
        '--sample_interps', action='store_true', default=False,
        help='Produce interpolation sheets and stick them in '
        'the samples root? (default: %(default)s)')
    parser.add_argument(
        '--sample_sheet_folder_num', type=int, default=-1,
        help='Number to use for the folder for these sample sheets '
        '(default: %(default)s)')
    parser.add_argument(
        '--sample_random', action='store_true', default=False,
        help='Produce a single random sheet? (default: %(default)s)')
    parser.add_argument(
        '--sample_trunc_curves', type=str, default='',
        help='Get inception metrics with a range of variances?'
        'To use this, specify a startpoint, step, and endpoint, e.g. '
        '--sample_trunc_curves 0.2_0.1_1.0 for a startpoint of 0.2, '
        'endpoint of 1.0, and stepsize of 1.0.  Note that this is '
        'not exactly identical to using tf.truncated_normal, but should '
        'have approximately the same effect. (default: %(default)s)')
    parser.add_argument(
        '--sample_inception_metrics', action='store_true', default=False,
        help='Calculate Inception metrics with sample.py? (default: %(default)s)')
    return parser
dset_dict = {'I32': dset.ImageFolder, 'I64': dset.ImageFolder,'CAHQ_64': dset.ImageFolder, 'CAHQ_128' :  dset.ImageFolder,
             'I128': dset.ImageFolder, 'I256': dset.ImageFolder,
             'I32_hdf5': dset.ILSVRC_HDF5, 'I64_hdf5': dset.ILSVRC_HDF5,
             'I128_hdf5': dset.ILSVRC_HDF5, 'I256_hdf5': dset.ILSVRC_HDF5,
             'C10': dset.CIFAR10, 'C100': dset.CIFAR100, 'CINIC10': dset.ImageFolder, 'C100U': dset.CIFAR100Unsupervised, 'CINIC10U': dset.CINIC10Unsupervised,
             'STL10': dset.STL10, 'C10U': dset.CIFAR10Unsupervised, 'CelebA': dset.CelebA, 'CA64': dset.CelebA, 'Art': dset.Art}
imsize_dict = {'I32': 32, 'I32_hdf5': 32,'CAHQ_64': 64, 'CAHQ_128' : 128,
               'I64': 64, 'I64_hdf5': 64,
               'I128': 128, 'I128_hdf5': 128,
               'I256': 256, 'I256_hdf5': 256, 'C100U': 32, 'CINIC10U': 32,
               'C10': 32, 'C100': 32, 'CINIC10': 32, 'STL10': 64, 'C10U': 32, 'CelebA': 32, 'CA64': 64, 'Art': 32}
root_dict = {'I32': 'ImageNet', 'I32_hdf5': 'ILSVRC32.hdf5', 'CAHQ_64': 'train', 'CAHQ_128' :  'train',
             'I64': 'ImageNet', 'I64_hdf5': 'ILSVRC64.hdf5',
             'I128': 'ImageNet', 'I128_hdf5': 'ILSVRC128.hdf5',
             'I256': 'ImageNet', 'I256_hdf5': 'ILSVRC256.hdf5', 'C100U': 'cifar', 'CINIC10U': 'cinic10/train', 
             'C10': 'cifar', 'C100': 'cifar', 'CINIC10': 'cinic10/train', 'STL10': 'stl10', 'C10U': 'cifar', 'CelebA': 'celeba', 'CA64': 'celeba', 'Art': 'devi_art'}
nclass_dict = {'I32': 1000, 'I32_hdf5': 1000, 'CAHQ_64': 1, 'CAHQ_128' :  1,
               'I64': 1000, 'I64_hdf5': 1000,
               'I128': 1000, 'I128_hdf5': 1000,
               'I256': 1000, 'I256_hdf5': 1000, 'C100U': 1, 'CINIC10U': 1,
               'C10': 10, 'C100': 100, 'CINIC10': 10, 'STL10': 1, 'C10U': 1, 'CelebA': 1, 'CA64': 1, 'Art': 34}
classes_per_sheet_dict = {'I32': 50, 'I32_hdf5': 50,'CAHQ_64': 1, 'CAHQ_128' : 1,
                          'I64': 50, 'I64_hdf5': 50,
                          'I128': 20, 'I128_hdf5': 20,
                          'I256': 20, 'I256_hdf5': 20, 'C100U': 1, 'CINIC10U': 1,
                          'C10': 10, 'C100': 100, 'CINIC10': 10, 'STL10': 1, 'C10U': 1, 'CelebA': 1, 'CA64': 1, 'Art': 34}
activation_dict = {'inplace_relu': nn.ReLU(inplace=True),
                   'relu': nn.ReLU(inplace=False),
                   'ir': nn.ReLU(inplace=True), }
class CenterCropLongEdge(object):
    def __call__(self, img):
        return transforms.functional.center_crop(img, min(img.size))
    def __repr__(self):
        return self.__class__.__name__
class RandomCropLongEdge(object):
    def __call__(self, img):
        size = (min(img.size), min(img.size))
        i = (0 if size[0] == img.size[0]
             else np.random.randint(low=0, high=img.size[0] - size[0]))
        j = (0 if size[1] == img.size[1]
             else np.random.randint(low=0, high=img.size[1] - size[1]))
        return transforms.functional.crop(img, i, j, size[0], size[1])
    def __repr__(self):
        return self.__class__.__name__
class MultiEpochSampler(torch.utils.data.Sampler):
    def __init__(self, data_source, num_epochs, start_itr=0, batch_size=128):
        self.data_source = data_source
        self.num_samples = len(self.data_source)
        self.num_epochs = num_epochs
        self.start_itr = start_itr
        self.batch_size = batch_size
        if not isinstance(self.num_samples, int) or self.num_samples <= 0:
            raise ValueError("num_samples should be a positive integeral "
                             "value, but got num_samples={}".format(self.num_samples))
    def __iter__(self):
        n = len(self.data_source)
        num_epochs = int(np.ceil((n * self.num_epochs - (self.start_itr * self.batch_size)) / float(n)))
        out = [torch.randperm(n)
               for epoch in range(self.num_epochs)][-num_epochs:]
        out[0] = out[0][(self.start_itr * self.batch_size % n):]
        output = torch.cat(out).tolist()
        print('Length dataset output is %d' % len(output))
        return iter(output)
    def __len__(self):
        return len(self.data_source) * self.num_epochs - self.start_itr * self.batch_size
def get_data_loaders(dataset, data_root=None, augment=False, batch_size=64,
                     num_workers=8, shuffle=True, load_in_mem=False, hdf5=False,
                     pin_memory=True, drop_last=True, start_itr=0,
                     num_epochs=500, use_multiepoch_sampler=False, **kwargs):
    data_root += '/%s' % root_dict[dataset]
    print('Using dataset root location %s' % data_root)
    which_dataset = dset_dict[dataset]
    norm_mean = [0.5, 0.5, 0.5]
    norm_std = [0.5, 0.5, 0.5]
    image_size = imsize_dict[dataset]
    dataset_kwargs = {'index_filename': '%s_imgs.npz' % dataset}
    if 'hdf5' in dataset:
        train_transform = None
    else:
        if augment:
            print('Data will be augmented...')
            if dataset in ['C10', 'C100', 'CINIC10', 'STL10', 'C10U']:
                train_transform = [transforms.RandomHorizontalFlip()]
            elif dataset in ['CelebA']:
                train_transform = [transforms.CenterCrop(140),
                                   transforms.Resize(image_size),
                                   transforms.RandomHorizontalFlip()]
            else:
                train_transform = [RandomCropLongEdge(),
                                   transforms.Resize(image_size),
                                   transforms.RandomHorizontalFlip()]
        else:
            print('Data will not be augmented...')
            if dataset in ['C10', 'C100', 'CINIC10', 'STL10', 'C10U']:
                train_transform = [transforms.Resize(image_size)]
            elif dataset in ['CelebA']:
                train_transform = [transforms.CenterCrop(140),
                                   transforms.Resize(image_size)]
            elif dataset in ['CA64']:
                train_transform = [transforms.CenterCrop(140),
                                   transforms.Resize(image_size)]
            elif dataset in ['CAHQ_64', 'CAHQ_128'] :
                train_transform = [transforms.Resize(image_size)]
            else:
                train_transform = [CenterCropLongEdge(), transforms.Resize(image_size)]
        train_transform = transforms.Compose(train_transform + [transforms.ToTensor(), transforms.Normalize(norm_mean, norm_std)])
    train_set = which_dataset(root=data_root, transform=train_transform, load_in_mem=load_in_mem, **dataset_kwargs)
    from torch.utils.data import Subset
    def get_target_label_idx(labels, targets):
        return np.argwhere(np.isin(labels, targets)).flatten().tolist()
    train_idx_normal = get_target_label_idx(train_set.labels, [1, 2, 3, 4, 5, 6, 7, 8, 9])
    train_set = Subset(train_set, train_idx_normal)
    print(len(train_set))
    from train_Task1_KLWGAN_Proof_of_Concept import select_dataset
    print(select_dataset)
    if select_dataset == "mnist":
        train_transform = transforms.Compose([transforms.Grayscale(3), train_transform])
        train_set = torchvision.datasets.MNIST(root=data_root, transform=train_transform, download=True)
        from torch.utils.data import Subset
        def get_target_label_idx(labels, targets):
            return np.argwhere(np.isin(labels, targets)).flatten().tolist()
        train_idx_normal = get_target_label_idx(train_set.targets, [1, 2, 3, 4, 5, 6, 7, 8, 9])
        train_set = Subset(train_set, train_idx_normal)
        print(len(train_set))
    loaders = []
    if use_multiepoch_sampler:
        print('Using multiepoch sampler from start_itr %d...' % start_itr)
        loader_kwargs = {'num_workers': num_workers, 'pin_memory': pin_memory}
        sampler = MultiEpochSampler(train_set, num_epochs, start_itr, batch_size)
        train_loader = DataLoader(train_set, batch_size=batch_size, sampler=sampler, **loader_kwargs)
    else:
        print('shuffle ', shuffle, ' batch_size ', batch_size, ' num_workers ', num_workers, ' pin_memory ', pin_memory)
        loader_kwargs = {'num_workers': num_workers, 'pin_memory': pin_memory, 'drop_last': drop_last}
        train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=shuffle, **loader_kwargs)
    loaders.append(train_loader)
    return loaders
def seed_rng(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    np.random.seed(seed)
def update_config_roots(config):
    if config['base_root']:
        print('Pegging all root folders to base root %s' % config['base_root'])
        for key in ['data', 'weights', 'logs', 'samples']:
            config['%s_root' % key] = '%s/%s' % (config['base_root'], key)
    return config
def prepare_root(config):
    for key in ['weights_root', 'logs_root', 'samples_root']:
        if not os.path.exists(config[key]):
            print('Making directory %s for %s...' % (config[key], key))
            os.mkdir(config[key])
class ema(object):
    def __init__(self, source, target, decay=0.9999, start_itr=0):
        self.source = source
        self.target = target
        self.decay = decay
        self.start_itr = start_itr
        self.source_dict = self.source.state_dict()
        self.target_dict = self.target.state_dict()
        with torch.no_grad():
            for key in self.source_dict:
                self.target_dict[key].data.copy_(self.source_dict[key].data)
    def update(self, itr=None):
        if itr and itr < self.start_itr:
            decay = 0.0
        else:
            decay = self.decay
        with torch.no_grad():
            for key in self.source_dict:
                self.target_dict[key].data.copy_(self.target_dict[key].data * decay + self.source_dict[key].data * (1 - decay))
def ortho(model, strength=1e-4, blacklist=[]):
    with torch.no_grad():
        for param in model.parameters():
            if len(param.shape) < 2 or any([param is item for item in blacklist]):
                continue
            w = param.view(param.shape[0], -1)
            grad = (2 * torch.mm(torch.mm(w, w.t())
                                 * (1. - torch.eye(w.shape[0], device=w.device)), w))
            param.grad.data += strength * grad.view(param.shape)
def default_ortho(model, strength=1e-4, blacklist=[]):
    with torch.no_grad():
        for param in model.parameters():
            if len(param.shape) < 2 or param in blacklist:
                continue
            w = param.view(param.shape[0], -1)
            grad = (2 * torch.mm(torch.mm(w, w.t())
                                 - torch.eye(w.shape[0], device=w.device), w))
            param.grad.data += strength * grad.view(param.shape)
def toggle_grad(model, on_or_off):
    for param in model.parameters():
        param.requires_grad = on_or_off
def join_strings(base_string, strings):
    return base_string.join([item for item in strings if item])
def save_weights(G, D, state_dict, weights_root, experiment_name,
                 name_suffix=None, G_ema=None):
    root = '/'.join([weights_root, experiment_name])
    if not os.path.exists(root):
        os.mkdir(root)
    if name_suffix:
        print('Saving weights to %s/%s...' % (root, name_suffix))
    else:
        print('Saving weights to %s...' % root)
    torch.save(G.state_dict(),
               '%s/%s.pth' % (root, join_strings('_', ['G', name_suffix])))
    torch.save(G.optim.state_dict(),
               '%s/%s.pth' % (root, join_strings('_', ['G_optim', name_suffix])))
    torch.save(D.state_dict(),
               '%s/%s.pth' % (root, join_strings('_', ['D', name_suffix])))
    torch.save(D.optim.state_dict(),
               '%s/%s.pth' % (root, join_strings('_', ['D_optim', name_suffix])))
    torch.save(state_dict,
               '%s/%s.pth' % (root, join_strings('_', ['state_dict', name_suffix])))
    if G_ema is not None:
        torch.save(G_ema.state_dict(),
                   '%s/%s.pth' % (root, join_strings('_', ['G_ema', name_suffix])))
def load_weights(G, D, state_dict, weights_root, experiment_name,
                 name_suffix=None, G_ema=None, strict=True, load_optim=True):
    root = '/'.join([weights_root, experiment_name])
    if name_suffix:
        print('Loading %s weights from %s...' % (name_suffix, root))
    else:
        print('Loading weights from %s...' % root)
    if G is not None:
        G.load_state_dict(
            torch.load('%s/%s.pth' %
                       (root, join_strings('_', ['G', name_suffix]))),
            strict=strict)
        if load_optim:
            G.optim.load_state_dict(
                torch.load('%s/%s.pth' % (root, join_strings('_', ['G_optim', name_suffix]))))
    if D is not None:
        D.load_state_dict(
            torch.load('%s/%s.pth' %
                       (root, join_strings('_', ['D', name_suffix]))),
            strict=strict)
        if load_optim:
            D.optim.load_state_dict(
                torch.load('%s/%s.pth' % (root, join_strings('_', ['D_optim', name_suffix]))))
    for item in state_dict:
        state_dict[item] = torch.load(
            '%s/%s.pth' % (root, join_strings('_', ['state_dict', name_suffix])))[item]
    if G_ema is not None:
        G_ema.load_state_dict(
            torch.load('%s/%s.pth' %
                       (root, join_strings('_', ['G_ema', name_suffix]))),
            strict=strict)
class MetricsLogger(object):
    def __init__(self, fname, reinitialize=False):
        self.fname = fname
        self.reinitialize = reinitialize
        if os.path.exists(self.fname):
            if self.reinitialize:
                print('{} exists, deleting...'.format(self.fname))
                os.remove(self.fname)

    def log(self, record=None, **kwargs):
        if record is None:
            record = {}
        record.update(kwargs)
        record['_stamp'] = time.time()
        with open(self.fname, 'a') as f:
            f.write(json.dumps(record, ensure_ascii=True) + '\n')
class MyLogger(object):
    def __init__(self, fname, reinitialize=False, logstyle='%3.3f'):
        self.root = fname
        if not os.path.exists(self.root):
            os.mkdir(self.root)
        self.reinitialize = reinitialize
        self.metrics = []
        self.logstyle = logstyle
    def reinit(self, item):
        if os.path.exists('%s/%s.log' % (self.root, item)):
            if self.reinitialize:
                if 'sv' in item:
                    if not any('sv' in item for item in self.metrics):
                        print('Deleting singular value logs...')
                else:
                    print('{} exists, deleting...'.format(
                        '%s_%s.log' % (self.root, item)))
                os.remove('%s/%s.log' % (self.root, item))
    def log(self, itr, **kwargs):
        for arg in kwargs:
            if arg not in self.metrics:
                if self.reinitialize:
                    self.reinit(arg)
                self.metrics += [arg]
            if self.logstyle == 'pickle':
                print('Pickle not currently supported...')
            elif self.logstyle == 'mat':
                print('.mat logstyle not currently supported...')
            else:
                with open('%s/%s.log' % (self.root, arg), 'a') as f:
                    f.write('%d: %s\n' % (itr, self.logstyle % kwargs[arg]))
def write_metadata(logs_root, experiment_name, config, state_dict):
    with open(('%s/%s/metalog.txt' %
               (logs_root, experiment_name)), 'w') as writefile:
        writefile.write('datetime: %s\n' % str(datetime.datetime.now()))
        writefile.write('config: %s\n' % str(config))
        writefile.write('state: %s\n' % str(state_dict))
def progress(items, desc='', total=None, min_delay=0.1, displaytype='s1k'):
    total = total or len(items)
    t_start = time.time()
    t_last = 0
    for n, item in enumerate(items):
        t_now = time.time()
        if t_now - t_last > min_delay:
            print("\r%s%d/%d (%6.2f%%)" % (
                desc, n+1, total, n / float(total) * 100), end=" ")
            if n > 0:
                if displaytype == 's1k':
                    next_1000 = n + (1000 - n % 1000)
                    t_done = t_now - t_start
                    t_1k = t_done / n * next_1000
                    outlist = list(divmod(t_done, 60)) + \
                        list(divmod(t_1k - t_done, 60))
                    print("(TE/ET1k: %d:%02d / %d:%02d)" %
                          tuple(outlist), end=" ")
                else:
                    t_done = t_now - t_start
                    t_total = t_done / n * total
                    outlist = list(divmod(t_done, 60)) + \
                        list(divmod(t_total - t_done, 60))
                    print("(TE/ETA: %d:%02d / %d:%02d)" %
                          tuple(outlist), end=" ")

            sys.stdout.flush()
            t_last = t_now
        yield item
    t_total = time.time() - t_start
    print("\r%s%d/%d (100.00%%) (took %d:%02d)" % ((desc, total, total) + divmod(t_total, 60)))
def sample(G, z_, y_, config):
    with torch.no_grad():
        z_.sample_()
        y_.sample_()
        if config['parallel']:
            G_z = nn.parallel.data_parallel(G, (z_, G.shared(y_)))
        else:
            G_z = G(z_, G.shared(y_))
        return G_z, y_
def sample_inception(G_ema, config, folder_number):
    if config['dataset'] in ['CAHQ_64', 'CAHQ_128'] :
        config['sample_num_npz'] = 3000
    else : 
        config['sample_num_npz'] = 10000
    experiment_name = (config['experiment_name'] if config['experiment_name']
                       else name_from_config(config))
    if not os.path.isdir('%s/%s/%s' % (config['samples_root'], experiment_name, folder_number)):
        os.mkdir('%s/%s/%s' %
                 (config['samples_root'], experiment_name, folder_number))
    import functools
    device = 'cuda'
    G_batch_size = max(config['G_batch_size'], config['batch_size'])
    z_, y_ = prepare_z_y(G_batch_size, G_ema.dim_z, config['n_classes'],
                         device=device, fp16=config['G_fp16'],
                         z_var=config['z_var'])
    sample_ = functools.partial(sample, G=G_ema, z_=z_, y_=y_, config=config)
    x, y = [], []
    print('Sampling %d images and saving them to npz...' %
          config['sample_num_npz'])
    for i in trange(int(np.ceil(config['sample_num_npz'] / float(G_batch_size)))):
        with torch.no_grad():
            images, labels = sample_()
        x += [np.uint8(255 * (images.cpu().numpy() + 1) / 2.)]
        y += [labels.cpu().numpy()]
    x = np.concatenate(x, 0)[:config['sample_num_npz']]
    y = np.concatenate(y, 0)[:config['sample_num_npz']]
    print('Images shape: %s, Labels shape: %s' % (x.shape, y.shape))
    npz_filename = '%s/%s/%s/samples.npz' % (
        config['samples_root'], experiment_name, folder_number)
    print('Saving npz to %s...' % npz_filename)
    np.savez(npz_filename, **{'x': x, 'y': y})
def sample_sheet(G, classes_per_sheet, num_classes, samples_per_class, parallel,
                 samples_root, experiment_name, folder_number, z_=None):
    if not os.path.isdir('%s/%s' % (samples_root, experiment_name)):
        os.mkdir('%s/%s' % (samples_root, experiment_name))
    if not os.path.isdir('%s/%s/%d' % (samples_root, experiment_name, folder_number)):
        os.mkdir('%s/%s/%d' % (samples_root, experiment_name, folder_number))
    for i in range(num_classes // classes_per_sheet):
        ims = []
        y = torch.arange(i * classes_per_sheet, (i + 1) * classes_per_sheet, device='cuda')
        for j in range(samples_per_class):
            if (z_ is not None) and hasattr(z_, 'sample_') and classes_per_sheet <= z_.size(0):
                z_.sample_()
            else:
                z_ = torch.randn(classes_per_sheet, G.dim_z, device='cuda')
            with torch.no_grad():
                if parallel:
                    o = nn.parallel.data_parallel(
                        G, (z_[:classes_per_sheet], G.shared(y)))
                else:
                    o = G(z_[:classes_per_sheet], G.shared(y))
            ims += [o.data.cpu()]
        out_ims = torch.stack(ims, 1).view(-1, ims[0].shape[1], ims[0].shape[2],
                                           ims[0].shape[3]).data.float().cpu()
        image_filename = '%s/%s/%d/samples%d.jpg' % (samples_root, experiment_name,
                                                     folder_number, i)
        torchvision.utils.save_image(out_ims, image_filename,
                                     nrow=samples_per_class, normalize=True)
def interp(x0, x1, num_midpoints):
    lerp = torch.linspace(0, 1.0, num_midpoints + 2,
                          device='cuda').to(x0.dtype)
    return ((x0 * (1 - lerp.view(1, -1, 1))) + (x1 * lerp.view(1, -1, 1)))
def interp_sheet(G, num_per_sheet, num_midpoints, num_classes, parallel,
                 samples_root, experiment_name, folder_number, sheet_number=0,
                 fix_z=False, fix_y=False, device='cuda'):
    if fix_z:
        zs = torch.randn(num_per_sheet, 1, G.dim_z, device=device)
        zs = zs.repeat(1, num_midpoints + 2, 1).view(-1, G.dim_z)
    else:
        zs = interp(torch.randn(num_per_sheet, 1, G.dim_z, device=device),
                    torch.randn(num_per_sheet, 1, G.dim_z, device=device),
                    num_midpoints).view(-1, G.dim_z)
    if fix_y:
        ys = sample_1hot(num_per_sheet, num_classes)
        ys = G.shared(ys).view(num_per_sheet, 1, -1)
        ys = ys.repeat(1, num_midpoints + 2,
                       1).view(num_per_sheet * (num_midpoints + 2), -1)
    else:
        ys = interp(G.shared(sample_1hot(num_per_sheet, num_classes)).view(num_per_sheet, 1, -1),
                    G.shared(sample_1hot(num_per_sheet, num_classes)).view(
                        num_per_sheet, 1, -1),
                    num_midpoints).view(num_per_sheet * (num_midpoints + 2), -1)
    if G.fp16:
        zs = zs.half()
    with torch.no_grad():
        if parallel:
            out_ims = nn.parallel.data_parallel(G, (zs, ys)).data.cpu()
        else:
            out_ims = G(zs, ys).data.cpu()
    interp_style = '' + ('Z' if not fix_z else '') + ('Y' if not fix_y else '')
    image_filename = '%s/%s/%d/interp%s%d.jpg' % (samples_root, experiment_name,
                                                  folder_number, interp_style,
                                                  sheet_number)
    torchvision.utils.save_image(out_ims, image_filename,
                                 nrow=num_midpoints + 2, normalize=True)
def print_grad_norms(net):
    gradsums = [[float(torch.norm(param.grad).item()),
                 float(torch.norm(param).item()), param.shape]
                for param in net.parameters()]
    order = np.argsort([item[0] for item in gradsums])
    print(['%3.3e,%3.3e, %s' % (gradsums[item_index][0],
                                gradsums[item_index][1],
                                str(gradsums[item_index][2]))
           for item_index in order])
def get_SVs(net, prefix):
    d = net.state_dict()
    return {('%s_%s' % (prefix, key)).replace('.', '_'):
            float(d[key].item())
            for key in d if 'sv' in key}
def name_from_config(config):
    name = '_'.join([
        item for item in [
            'Big%s' % config['which_train_fn'],
            config['dataset'],
            config['loss_type'],
            config['model'] if config['model'] != 'BigGAN' else None,
            'seed%d' % config['seed'],
            'Gch%d' % config['G_ch'],
            'Dch%d' % config['D_ch'],
            'Gd%d' % config['G_depth'] if config['G_depth'] > 1 else None,
            'Dd%d' % config['D_depth'] if config['D_depth'] > 1 else None,
            'bs%d' % config['batch_size'],
            'Gfp16' if config['G_fp16'] else None,
            'Dfp16' if config['D_fp16'] else None,
            'nDs%d' % config['num_D_steps'] if config['num_D_steps'] > 1 else None,
            'nDa%d' % config['num_D_accumulations'] if config['num_D_accumulations'] > 1 else None,
            'nGa%d' % config['num_G_accumulations'] if config['num_G_accumulations'] > 1 else None,
            'Glr%2.1e' % config['G_lr'],
            'Dlr%2.1e' % config['D_lr'],
            'GB%3.3f' % config['G_B1'] if config['G_B1'] != 0.0 else None,
            'GBB%3.3f' % config['G_B2'] if config[
              'G_B2'] != 0.999 else None,
            'DB%3.3f' % config['D_B1'] if config['D_B1'] != 0.0 else None,
            'DBB%3.3f' % config['D_B2'] if config['D_B2'] != 0.999 else None,
            'Gnl%s' % config['G_nl'],
            'Dnl%s' % config['D_nl'],
            'Ginit%s' % config['G_init'],
            'Dinit%s' % config['D_init'],
            'G%s' % config['G_param'] if config['G_param'] != 'SN' else None,
            'D%s' % config['D_param'] if config['D_param'] != 'SN' else None,
            'Gattn%s' % config['G_attn'] if config['G_attn'] != '0' else None,
            'Dattn%s' % config['D_attn'] if config['D_attn'] != '0' else None,
            'Gortho%2.1e' % config['G_ortho'] if config['G_ortho'] > 0.0 else None,
            'Dortho%2.1e' % config['D_ortho'] if config['D_ortho'] > 0.0 else None,
            config['norm_style'] if config['norm_style'] != 'bn' else None,
            'cr' if config['cross_replica'] else None,
            'Gshared' if config['G_shared'] else None,
            'hier' if config['hier'] else None,
            'ema' if config['ema'] else None,
            config['name_suffix'] if config['name_suffix'] else None,]
        if item is not None])
def query_gpu(indices):
    os.system('nvidia-smi -i 0 --query-gpu=memory.free --format=csv')
def count_parameters(module):
    print('Number of parameters: {}'.format(
        sum([p.data.nelement() for p in module.parameters()])))
def sample_1hot(batch_size, num_classes, device='cuda'):
    return torch.randint(low=0, high=num_classes, size=(batch_size,), device=device, dtype=torch.int64, requires_grad=False)
class Distribution(torch.Tensor):
    def init_distribution(self, dist_type, **kwargs):
        self.dist_type = dist_type
        self.dist_kwargs = kwargs
        if self.dist_type == 'normal':
            self.mean, self.var = kwargs['mean'], kwargs['var']
        elif self.dist_type == 'categorical':
            self.num_categories = kwargs['num_categories']
    def sample_(self):
        if self.dist_type == 'normal':
            self.normal_(self.mean, self.var)
        elif self.dist_type == 'categorical':
            self.random_(0, self.num_categories)
    def to(self, *args, **kwargs):
        new_obj = Distribution(self)
        new_obj.init_distribution(self.dist_type, **self.dist_kwargs)
        new_obj.data = super().to(*args, **kwargs)
        return new_obj
def prepare_z_y(G_batch_size, dim_z, nclasses, device='cuda', fp16=False, z_var=1.0):
    z_ = Distribution(torch.randn(G_batch_size, dim_z, requires_grad=False))
    z_.init_distribution('normal', mean=0, var=z_var)
    z_ = z_.to(device, torch.float16 if fp16 else torch.float32)
    if fp16:
        z_ = z_.half()
    y_ = Distribution(torch.zeros(G_batch_size, requires_grad=False))
    y_.init_distribution('categorical', num_categories=nclasses)
    y_ = y_.to(device, torch.int64)
    return z_, y_
def initiate_standing_stats(net):
    for module in net.modules():
        if hasattr(module, 'accumulate_standing'):
            module.reset_stats()
            module.accumulate_standing = True
def accumulate_standing_stats(net, z, y, nclasses, num_accumulations=16):
    initiate_standing_stats(net)
    net.train()
    for i in range(num_accumulations):
        with torch.no_grad():
            z.normal_()
            y.random_(0, nclasses)
            x = net(z, net.shared(y))
    net.eval()
def fairness_discrepancy(data, n_classes):
    if n_classes == 2:
        props = data.sum() / 10000
        fair_d = abs(.5 - props)
    else: 
        unique, freq = np.unique(data, return_counts=True)
        props = freq / 10000
        fair_d = np.sqrt((abs(props - 0.25)**2).sum())
    return fair_d
class Adam16(Optimizer):
    def __init__(self, params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8, weight_decay=0):
        defaults = dict(lr=lr, betas=betas, eps=eps, weight_decay=weight_decay)
        params = list(params)
        super(Adam16, self).__init__(params, defaults)
    def load_state_dict(self, state_dict):
        super(Adam16, self).load_state_dict(state_dict)
        for group in self.param_groups:
            for p in group['params']:
                self.state[p]['exp_avg'] = self.state[p]['exp_avg'].float()
                self.state[p]['exp_avg_sq'] = self.state[p]['exp_avg_sq'].float()
                self.state[p]['fp32_p'] = self.state[p]['fp32_p'].float()
    def step(self, closure=None):
        loss = None
        if closure is not None:
            loss = closure()
        for group in self.param_groups:
            for p in group['params']:
                if p.grad is None:
                    continue
                grad = p.grad.data.float()
                state = self.state[p]
                if len(state) == 0:
                    state['step'] = 0
                    state['exp_avg'] = grad.new().resize_as_(grad).zero_()
                    state['exp_avg_sq'] = grad.new().resize_as_(grad).zero_()
                    state['fp32_p'] = p.data.float()
                exp_avg, exp_avg_sq = state['exp_avg'], state['exp_avg_sq']
                beta1, beta2 = group['betas']
                state['step'] += 1
                if group['weight_decay'] != 0:
                    grad = grad.add(group['weight_decay'], state['fp32_p'])
                exp_avg.mul_(beta1).add_(1 - beta1, grad)
                exp_avg_sq.mul_(beta2).addcmul_(1 - beta2, grad, grad)
                denom = exp_avg_sq.sqrt().add_(group['eps'])
                bias_correction1 = 1 - beta1 ** state['step']
                bias_correction2 = 1 - beta2 ** state['step']
                step_size = group['lr'] * math.sqrt(bias_correction2) / bias_correction1
                state['fp32_p'].addcdiv_(-step_size, exp_avg, denom)
                p.data = state['fp32_p'].half()
        return loss
# Acknowledgement: Thanks to the repository: [KLWGAN](https://github.com/ermongroup/f-wgan/tree/master/image_generation)
# Acknowledgement: Thanks to the repositories: [PyTorch-Template](https://github.com/victoresque/pytorch-template "PyTorch Template"), [Generative Models](https://github.com/shayneobrien/generative-models/blob/master/src/f_gan.py), [f-GAN](https://github.com/nowozin/mlss2018-madrid-gan), and [KLWGAN](https://github.com/ermongroup/f-wgan/tree/master/image_generation)
# Also, thanks to the repositories: [Negative-Data-Augmentation](https://anonymous.4open.science/r/99219ca9-ff6a-49e5-a525-c954080de8a7/), [Negative-Data-Augmentation-Paper](https://openreview.net/forum?id=Ovp8dvB8IBH), and [BigGAN](https://github.com/ajbrock/BigGAN-PyTorch)
