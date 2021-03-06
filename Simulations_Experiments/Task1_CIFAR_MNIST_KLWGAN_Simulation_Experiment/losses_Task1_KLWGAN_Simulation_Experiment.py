# Acknowledgement: Thanks to the repository: [KLWGAN](https://github.com/ermongroup/f-wgan/tree/master/image_generation)
# Acknowledgement: Thanks to the repositories: [PyTorch-Template](https://github.com/victoresque/pytorch-template "PyTorch Template"), [Generative Models](https://github.com/shayneobrien/generative-models/blob/master/src/f_gan.py), [f-GAN](https://github.com/nowozin/mlss2018-madrid-gan), and [KLWGAN](https://github.com/ermongroup/f-wgan/tree/master/image_generation)
# Also, thanks to the repositories: [Negative-Data-Augmentation](https://anonymous.4open.science/r/99219ca9-ff6a-49e5-a525-c954080de8a7/), [Negative-Data-Augmentation-Paper](https://openreview.net/forum?id=Ovp8dvB8IBH), and [BigGAN](https://github.com/ajbrock/BigGAN-PyTorch)
import torch
import torch.nn.functional as F
def loss_dcgan_dis(dis_fake, dis_real):
    L1 = torch.mean(F.softplus(-dis_real))
    L2 = torch.mean(F.softplus(dis_fake))
    return L1, L2
def loss_dcgan_gen(dis_fake):
    loss = torch.mean(F.softplus(-dis_fake))
    return loss
def loss_dcgan_dis_new(dis_fake, dis_real, dis_real_fake):
    L1 = torch.mean(F.softplus(-dis_real))
    L2 = torch.mean(F.softplus(dis_fake))
    L_real_fake = torch.mean(F.softplus(dis_real_fake))
    return L1, L2, L_real_fake
def loss_hinge_dis(dis_fake, dis_real):
    weighted = F.relu(1. - dis_real)
    loss_real = torch.mean(weighted)
    loss_fake = torch.mean(F.relu(1. + dis_fake))
    return loss_real, loss_fake
def loss_hinge_gen(dis_fake):
    loss = -torch.mean(dis_fake)
    return loss
def get_kl_ratio(v):
    v_norm = torch.logsumexp(v[:, 0], dim=0) - torch.log(torch.tensor(v.size(0)).float())
    return torch.exp(v - v_norm)
def loss_kl_dis(dis_fake, dis_real, temp=1.0):
    dis_fake_m = dis_fake / temp
    dis_fake_ratio = get_kl_ratio(dis_fake_m)
    dis_fake = dis_fake * dis_fake_ratio
    loss_real = torch.mean(F.relu(1. - dis_real))
    loss_fake = torch.mean(F.relu(1. + dis_fake))
    return loss_real, loss_fake
def loss_kl_gen(dis_fake, temp=1.0):
    dis_fake_m = dis_fake / temp
    dis_fake_ratio = get_kl_ratio(dis_fake_m)
    dis_fake = dis_fake * dis_fake_ratio
    loss = -torch.mean(dis_fake)
    return loss
def loss_chi_dis(dis_fake, dis_real):
    dis_fake = torch.clamp(dis_fake, -1.0, 1.0)
    dis_real = torch.clamp(dis_real, -1.0, 1.0)
    loss_real = torch.mean(- dis_real)
    dis_fake_mean = torch.mean(dis_fake)
    loss_fake = torch.mean(dis_fake * (dis_fake - dis_fake_mean + 2)) / 2.0
    return loss_real, loss_fake
def loss_chi_gen(dis_fake):
    dis_fake = torch.clamp(dis_fake, -1.0, 1.0)
    dis_fake_mean = torch.mean(dis_fake)
    loss_fake = -torch.mean(dis_fake * (dis_fake - dis_fake_mean + 2)) / 2.0
    return loss_fake
# Pearson Chi-Squared: According to Table 4 of the f-GAN paper, we use the
# Pearson Chi-Squared f-divergence distribution metric and we note that after Pearson
# Chi-Squared, the next best are KL and then Jensen-Shannon (Nowozin et al., 2016).
def loss_dv_dis(dis_fake, dis_real):
    loss_real = torch.mean(F.relu(1. - dis_real))
    dis_fake_norm = torch.exp(dis_fake).mean() + 1e-8
    dis_fake_ratio = (torch.exp(dis_fake) + 1e-8) / dis_fake_norm
    dis_fake = dis_fake * dis_fake_ratio
    loss_fake = torch.mean(F.relu(1. + dis_fake)) + torch.mean(dis_fake_ratio * torch.log(dis_fake_ratio))
    return loss_real, loss_fake
def loss_dv_gen(dis_fake):
    dis_fake_norm = torch.exp(dis_fake).mean() + 1e-8
    dis_fake_ratio = (torch.exp(dis_fake) + 1e-8) / dis_fake_norm
    dis_fake = dis_fake * dis_fake_ratio
    loss = -torch.mean(dis_fake) - torch.mean(dis_fake_ratio * torch.log(dis_fake_ratio))
    return loss
generator_loss = loss_hinge_gen
discriminator_loss = loss_hinge_dis
# Acknowledgement: Thanks to the repository: [KLWGAN](https://github.com/ermongroup/f-wgan/tree/master/image_generation)
# Acknowledgement: Thanks to the repositories: [PyTorch-Template](https://github.com/victoresque/pytorch-template "PyTorch Template"), [Generative Models](https://github.com/shayneobrien/generative-models/blob/master/src/f_gan.py), [f-GAN](https://github.com/nowozin/mlss2018-madrid-gan), and [KLWGAN](https://github.com/ermongroup/f-wgan/tree/master/image_generation)
# Also, thanks to the repositories: [Negative-Data-Augmentation](https://anonymous.4open.science/r/99219ca9-ff6a-49e5-a525-c954080de8a7/), [Negative-Data-Augmentation-Paper](https://openreview.net/forum?id=Ovp8dvB8IBH), and [BigGAN](https://github.com/ajbrock/BigGAN-PyTorch)
