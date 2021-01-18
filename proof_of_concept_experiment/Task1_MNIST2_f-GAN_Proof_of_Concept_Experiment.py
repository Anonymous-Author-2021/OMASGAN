# According to Table 4 of the f-GAN paper, we use Pearson Chi-Squared.
# After Pearson Chi-Squared, the next best are KL and then Jensen-Shannon.
import os
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import math
import numpy as np
import matplotlib.pyplot as plt
import torch
import random
seed_value = 2
random.seed(seed_value)
torch.manual_seed(seed_value)
torch.cuda.manual_seed_all(seed_value)
np.random.seed(seed_value)
torch.backends.cudnn.deterministic = True
from tensorboardX import SummaryWriter
import torchvision
import torchvision.transforms as transforms
import torchvision.utils as vutils
transform = transforms.Compose([transforms.Grayscale(3), transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))])
MNIST = torchvision.datasets.MNIST('data-mnist', train=True, download=True, transform=transform)
from torch.utils.data import Subset
def get_target_label_idx(labels, targets):
  return np.argwhere(np.isin(labels, targets)).flatten().tolist()
train_idx_normal = get_target_label_idx(MNIST.targets, [1, 2, 3, 4, 5, 6, 7, 8, 9])
MNIST = Subset(MNIST, train_idx_normal)
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.nn.init as init
from torch.autograd import Variable
class ConjugateDualFunction:
   def __init__(self, divergence_name):
       self.divergence_name = divergence_name
   def T(self, v):
       if self.divergence_name == "kl":
           return v
       elif self.divergence_name == "klrev":
           return -F.exp(v)
       # According to Table 4 of the f-GAN paper, we use Pearson Chi-Squared.
       # After Pearson Chi-Squared, the next best are KL and then Jensen-Shannon.
       elif self.divergence_name == "pearson":
           return v
       elif self.divergence_name == "neyman":
           return 1.0 - F.exp(v)
       elif self.divergence_name == "hellinger":
           return 1.0 - F.exp(v)
       elif self.divergence_name == "jensen":
           return math.log(2.0) - F.softplus(-v)
       elif self.divergence_name == "gan":
           return -F.softplus(-v)
       else:
           raise ValueError("Unknown f-divergence.")
   def fstarT(self, v):
       if self.divergence_name == "kl":
           return torch.exp(v - 1.0)
       elif self.divergence_name == "klrev":
           return -1.0 - v
       # According to Table 4 of the f-GAN paper, we use Pearson Chi-Squared.
       # After Pearson Chi-Squared, the next best are KL and then Jensen-Shannon.
       elif self.divergence_name == "pearson":
           return 0.25*v*v + v
       elif self.divergence_name == "neyman":
           return 2.0 - 2.0*F.exp(0.5*v)
       elif self.divergence_name == "hellinger":
           return F.exp(-v) - 1.0
       elif self.divergence_name == "jensen":
           return F.softplus(v) - math.log(2.0)
       elif self.divergence_name == "gan":
           return F.softplus(v)
       else:
           raise ValueError("This is an unknown f-divergence.")
class DCGANGenerator(nn.Module):
   def __init__(self, nrand):
       super(DCGANGenerator, self).__init__()
       self.lin1 = nn.Linear(nrand, 4*4*512)
       init.xavier_uniform_(self.lin1.weight, gain=0.1)
       self.lin1bn = nn.BatchNorm1d(4*4*512)
       self.dc1 = nn.ConvTranspose2d(512, 256, 4, stride=2, padding=1)
       self.dc1bn = nn.BatchNorm2d(256)
       self.dc2 = nn.ConvTranspose2d(256, 128, 4, stride=2, padding=1)
       self.dc2bn = nn.BatchNorm2d(128)
       self.dc3a = nn.ConvTranspose2d(128, 64, 4, stride=2, padding=1)
       self.dc3abn = nn.BatchNorm2d(64)
       self.dc3b = nn.Conv2d(64, 3, 3, stride=1, padding=1)
   def forward(self, z):
       h = F.relu(self.lin1bn(self.lin1(z)))
       h = torch.reshape(h, (-1, 512, 4, 4))
       h = F.relu(self.dc1bn(self.dc1(h)))
       h = F.relu(self.dc2bn(self.dc2(h)))
       h = F.relu(self.dc3abn(self.dc3a(h)))
       x = self.dc3b(h)
       return x
class DCGANDiscriminator(nn.Module):
   def __init__(self):
       super(DCGANDiscriminator, self).__init__()
       self.conv1 = nn.Conv2d(3, 64, 4, stride=2, padding=1)
       self.conv1bn = nn.BatchNorm2d(64)
       self.conv2 = nn.Conv2d(64, 128, 4, stride=2, padding=1)
       self.conv2bn = nn.BatchNorm2d(128)
       self.conv3 = nn.Conv2d(128, 256, 4, stride=2, padding=1)
       self.conv3bn = nn.BatchNorm2d(256)
       self.lin1 = nn.Linear(4*4*256, 512)
       self.lin1bn = nn.BatchNorm1d(512)
       self.lin2 = nn.Linear(512, 1)
   def forward(self, x):
       h = F.elu(self.conv1bn(self.conv1(x)))
       h = F.elu(self.conv2bn(self.conv2(h)))
       h = F.elu(self.conv3bn(self.conv3(h)))
       h = torch.reshape(h, (-1, 4*4*256))
       h = F.elu(self.lin1bn(self.lin1(h)))
       v = self.lin2(h)
       return v
class FGANLearningObjective(nn.Module):
   def __init__(self, gen, disc, divergence_name="gan", gamma=0.01):
       super(FGANLearningObjective, self).__init__()
       self.gen = gen
       self.disc = disc
       self.conj = ConjugateDualFunction(divergence_name)
       self.gammahalf = 0.5*gamma
   def forward(self, xreal, zmodel):
       vreal = self.disc(xreal)
       Treal = self.conj.T(vreal)
       xmodel = self.gen(zmodel)
       vmodel = self.disc(xmodel)
       fstar_Tmodel = self.conj.fstarT(vmodel)
       loss_gen = -fstar_Tmodel.mean()
       loss_disc = fstar_Tmodel.mean() - Treal.mean()
       # Gradient penalty
       if self.gammahalf > 0.0:
           batchsize = xreal.size(0)
           grad_pd = torch.autograd.grad(Treal.sum(), xreal,
               create_graph=True, only_inputs=True)[0]
           grad_pd_norm2 = grad_pd.pow(2)
           grad_pd_norm2 = grad_pd_norm2.view(batchsize, -1).sum(1)
           gradient_penalty = self.gammahalf * grad_pd_norm2.mean()
           loss_disc += gradient_penalty
       return loss_gen, loss_disc
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
nrand = 100
gen = DCGANGenerator(nrand)
disc = DCGANDiscriminator()
# According to Table 4 of the f-GAN paper, we use Pearson Chi-Squared.
# After Pearson Chi-Squared, the next best are KL and then Jensen-Shannon.
fgan = FGANLearningObjective(gen, disc, "pearson", gamma=10.0)
fgan = fgan.to(device)
batchsize = 64
optimizer_gen = optim.Adam(fgan.gen.parameters(), lr=1.0e-3)
optimizer_disc = optim.Adam(fgan.disc.parameters(), lr=1.0e-3)
trainloader = torch.utils.data.DataLoader(MNIST, batch_size=batchsize, shuffle=True, num_workers=8, drop_last=True)
writer = SummaryWriter(log_dir="runs/MNIST", comment="f-GAN-Pearson")
nepochs = 500
niter = 0
for epoch in range(nepochs):
   zmodel = Variable(torch.rand((batchsize,nrand), device=device))
   xmodel = fgan.gen(zmodel)
   xmodelimg = vutils.make_grid(xmodel, normalize=True, scale_each=True)
   writer.add_image('Generated', xmodelimg, global_step=niter)
   for i, data in enumerate(trainloader, 0):
       niter += 1
       imgs, labels = data
       fgan.zero_grad()
       xreal = Variable(imgs.to(device), requires_grad=True)
       zmodel = Variable(torch.rand((batchsize,nrand), device=device))
       loss_gen, loss_disc = fgan(xreal, zmodel)
       writer.add_scalar('obj/disc', loss_disc, niter)
       writer.add_scalar('obj/gen', loss_gen, niter)
       if i == 0:
           print("epoch %d  iter %d  obj(D) %.4f  obj(G) %.4f"%(epoch, niter, loss_disc, loss_gen))
       fgan.gen.zero_grad()
       loss_gen.backward(retain_graph=True)
       optimizer_gen.step()
       fgan.disc.zero_grad()
       loss_disc.backward()
       optimizer_disc.step()
writer.export_scalars_to_json("./all_scalars.json")
writer.close()