# OMASGAN: Out-of-Distribution Minimum Anomaly Score GAN for Sample Generation on the Boundary
Out-of-Distribution Minimum Anomaly Score GAN (OMASGAN)

Code Repository for 'OMASGAN: Out-of-Distribution Minimum Anomaly Score GAN for Sample Generation on the Boundary'

## Abstract of Paper:
Deep generative models trained in an unsupervised manner encounter the serious problem of setting high likelihood, high probability density, and low reconstruction loss to Out-of-Distribution (OoD) samples. This increases the Type II errors (false negatives, misses of anomalies) and decreases the Anomaly Detection (AD) performance. Also, deep generative models for AD suffer from the rarity of anomalies problem. To address these limitations, we propose the new OoD Minimum Anomaly Score GAN (OMASGAN) model. OMASGAN addresses the rarity of anomalies problem by generating strong abnormal samples on the boundary of the support of the data distribution, using data only from the normal class. OMASGAN improves the AD performance by retraining including the abnormal minimum-anomaly-score OoD samples generated by our negative sampling augmentation methodology. OMASGAN uses any f-divergence distribution metric in its variational representation, and explicit likelihood and invertibility are not needed. The proposed model uses a discriminator for inference and the evaluation of OMASGAN on image data using the leave-one-out methodology shows that it achieves an improvement of at least 0.24 and 0.07 points in AUROC on average on MNIST and CIFAR-10 data, respectively, over recently proposed state-of-the-art AD benchmarks.

## Flowchart Diagram:

![plot](./Figures_Images/FlowchartOMASGAN.png)

Figure 1: Flowchart of the OMASGAN model for AD which generates minimum-anomaly-score OoD samples on the boundary of the support of the data distribution and subsequently uses these generated boundary samples to train a discriminative model for detecting abnormal samples.

![plot](./Figures_Images/Flowchart_OMASGAN.png)

Figure 2: Diagram of the training of the OMASGAN model for AD in images using active negative sampling and training by generating strong abnormal OoD samples on the boundary of the data distribution.

## Discussion about the Model:

![plot](./Figures_Images/Illustration_OMASGAN.png)

Figure 3: Illustration of the OMASGAN algorithm for AD where **x**~p<sub>**x**</sub>, G(**z**)~p<sub>g</sub>, and G'(**z**)~p<sub>g'</sub>. The figure shows the OMASGAN Tasks and the data distribution, p<sub>**x**</sub>, the data model distribution, p<sub>g</sub>, the data model distribution after retraining, p<sub>g'</sub>, and the samples from the boundary of the support of the data distribution, B(**z**)~p<sub>b</sub>.

To address the problem of deep generative models knowing what they do not know (Nalisnick et al., 2019), the proposed OMASGAN algorithm performs (iterative) retraining of generative models and GANs for AD and works with anomaly scores rather than with likelihood and probability density. Because it works with anomaly scores instead of probability, the OMASGAN algorithm avoids invertibility and works with GANs, implicit distributions, and f-divergence distribution metrics expressed in their variational representation. The model proposed in (Zaheer et al., 2020) uses old points to perform model retraining for AD, but these old points are chosen in an ad hoc way, do not cover the OoD part of the data space, and are very limited in supply. On the contrary, the proposed OMASGAN model generates any desired number of well scattered OoD points on the boundary of the data distribution for model retraining for AD. OMASGAN first produces minimum anomaly score OoD samples around the data, B(**z**)~p<sub>b</sub>, by using a decreasing function of a distribution metric between the boundary samples and the data and then retrains by including the generated OoD B(**z**) samples. The generated OoD minimum anomaly score B(**z**) samples lead to a generally looser definition of the boundary of the support of the data distribution and form a surface in the high-dimensional space, i.e. manifold. Abnormal OoD samples that lie far from the boundary of the data distribution are also created by the AD models proposed in (Pourreza et al., 2021) and (Bian et al., 2019).

OMASGAN performs automatic negative data augmentation and model retraining for AD by combining negative and positive training and by eliminating the need for feature extraction, human intervention, dataset-dependent heuristic techniques, and ad hoc methods because they do not scale. This strengthens the applicability and generalization of our AD model. The negative data augmentation strategy introduced in (Sinha et al., 2021) does not scale because it relies on feature extraction, feature engineering, rotating features, and human intervention. We note that one of the aims of deep learning is to eliminate feature engineering and feature extraction. The methodology proposed in (Sinha et al., 2021) is dataset-dependent and uses a restrictive and limiting definition of anomaly, creating OoD samples in an ad hoc way and not covering the OoD part of the data space. Starting from the data, D, OMASGAN generates the negative data, D’. As a next step, it learns the data and avoids D’. This is the proposed self-supervised learning methodology to perform retraining by including negative samples. This differs from (i) using single-epoch blurry reconstructions as OoD samples (Zaheer et al., 2020; Pourreza et al., 2021), (ii) rotating features and using Jigsaw images as anomalies (Sinha et al, 2021), and (iii) using a Conditional VAE (CVAE) to move away from the mean in the latent space to produce abnormal points (Bian et al., 2019).

## Usage:

For the evaluation of the proposed OMASGAN model, we use the leave-one-out (LOO) evaluation methodology and the image data sets [MNIST](http://yann.lecun.com/exdb/mnist/) and [CIFAR-10](https://www.cs.toronto.edu/~kriz/cifar.html). We repeat for every abnormal leave-out class and compute the average AD performance of OMASGAN over the abnormal leave-out classes. We also use synthetic data for the evaluation of the OMASGAN model and all the evaluation results can be found in our paper "OMASGAN: Out-of-Distribution Minimum Anomaly Score GAN for Sample Generation on the Boundary" (Author, 2021).

The paper 'OMASGAN: Out-of-Distribution Minimum Anomaly Score GAN for Sample Generation on the Boundary' in Section 5.1 and in Figure 3 presents the evaluation of the proposed OMASGAN model on synthetic data for a multimodal distribution with disconnected components for p<sub>**x**</sub>. Our evaluation results are presented in the folder [OMASGAN-Synthetic-Data](https://github.com/Anonymous-Author-2021/OMASGAN/tree/main/Simulations_Experiments/Toy_Data_Simulation_Experiment). The Toy Data Simulation Experiment folder, which is within the Simulations Experiments folder, includes figures and simulation results for OMASGAN evaluated on synthetic data. For multimodal distributions with disjoint/disconnected components for p<sub>**x**</sub>, for two-dimensional synthetic data, the OMASGAN model successfully forms and generates the boundary of the support of the data distribution in [OMASGAN-Task2](https://github.com/Anonymous-Author-2021/OMASGAN/blob/main/Simulations_Experiments/Toy_Data_Simulation_Experiment/Toy_Data_Image1_Task2.pdf), [Task2-Boundary](https://github.com/Anonymous-Author-2021/OMASGAN/blob/main/Simulations_Experiments/Toy_Data_Simulation_Experiment/Toy_Data_Image11_Task2.pdf), [Boundary-Formation](https://github.com/Anonymous-Author-2021/OMASGAN/blob/main/Simulations_Experiments/Toy_Data_Simulation_Experiment/Toy_Data_Image14_Task2.pdf), [Support-Boundary](https://github.com/Anonymous-Author-2021/OMASGAN/blob/main/Simulations_Experiments/Toy_Data_Simulation_Experiment/Toy_Data_Image28_Boundary.pdf), and [OMASGAN-AUROC](https://github.com/Anonymous-Author-2021/OMASGAN/blob/main/Simulations_Experiments/Toy_Data_Simulation_Experiment/Toy_Data_Image19_AUROC.pdf).

Simulations Experiments folder: The Optimization Tasks of OMASGAN, including the Boundary Task and the Retraining Task, are in the Simulations Experiments folder. In the boundary algorithm (Task 2), the boundary model is trained to perform sample generation on the boundary of the data distribution by starting from within the data distribution (Task 1). In the retraining function (Task 3), as shown in the flowchart diagram in Figure 1, OMASGAN performs model retraining for AD by including negative samples, where the negative OoD samples are generated by the proposed negative data augmentation methodology. Regarding our negative data augmentation methodology, OMASGAN generates minimum anomaly score OoD samples around the data using a strictly decreasing function of a distribution metric between the boundary samples and the data. For the Boundary and Retraining Tasks, according to Table 4 of the f-GAN paper, we use the Pearson Chi-Squared f-divergence distribution metric and we note that after Pearson Chi-Squared, the next best metrics are KL and Jensen-Shannon (Nowozin et al., 2016).

For synthetic data, example usage:
```
cd ./Simulations_Experiments/Toy_Data_Simulation_Experiment/
python train_Toy_Data_fGAN_Simulation_Experiment.py
```

## MNIST and CIFAR-10 Usage:

For the evaluation of the proposed OMASGAN model, we use synthetic data, [MNIST](http://yann.lecun.com/exdb/mnist/), [CIFAR-10](https://www.cs.toronto.edu/~kriz/cifar.html), [Fashion-MNIST](https://www.kaggle.com/zalando-research/fashionmnist), [KMNIST](https://github.com/rois-codh/kmnist), and [SVHN](http://ufldl.stanford.edu/housenumbers/). The paper 'OMASGAN: Out-of-Distribution Minimum Anomaly Score GAN for Sample Generation on the Boundary' in Sections 5.2-5.5 and in Figures 4-11 presents the evaluation of OMASGAN on image data from the MNIST and CIFAR-10 datasets. For the evaluation of OMASGAN on MNIST image data, we obtain [MNIST-Task3](https://github.com/Anonymous-Author-2021/OMASGAN/blob/main/Simulations_Experiments/Images_Generated_MNIST_Task3_fGAN.pdf) and for the evaluation of the OMASGAN model on CIFAR-10 data, we obtain [CIFAR10-Task3](https://github.com/Anonymous-Author-2021/OMASGAN/blob/main/Simulations_Experiments/Images_Generated_CIFAR-10_Task3_KLWGAN.pdf). Our evaluation results are presented in [OMASGAN-AUROC](https://github.com/Anonymous-Author-2021/OMASGAN/blob/main/Simulations_Experiments/OMASGAN_KLWGAN_CIFAR-10_LOO0_AUROC.pdf) and in the file [OMASGAN-Results](https://github.com/Anonymous-Author-2021/OMASGAN/blob/main/Simulations_Experiments/test_Evaluation_Metrics_Simulation_Experiment.py).

To run the f-GAN-based OMASGAN model using the LOO methodology on MNIST data, for the abnormal class "abnormal_class_LOO" (train_Task1_fGAN_Simulation_Experiment.py), run the bash script:
```
cd ./Experiments/
sh run_OMASGAN_fGAN_MNIST.sh
```

Example usage:
```
cd ./Simulations_Experiments/
python train_Task1_fGAN_Simulation_Experiment.py
#python -m train_Task1_fGAN_Simulation_Experiment
python Task1_MNIST_fGAN_Simulation_Experiment.py
python Task1_MNIST2_fGAN_Simulation_Experiment.py
```

Also, example usage:
```
cd ./Simulations_Experiments/Task1_CIFAR10_MNIST_KLWGAN_Simulation_Experiment/
python train_Task1_KLWGAN_Simulation_Experiment.py --select_dataset cifar10 --abnormal_class 0 --shuffle --batch_size 64 --parallel --num_G_accumulations 1 --num_D_accumulations 1 --num_epochs 500 --num_D_steps 4 --G_lr 2e-4 --D_lr 2e-4 --dataset C10 --data_root ./data/ --G_ortho 0.0 --G_attn 0 --D_attn 0 --G_init N02 --D_init N02 --ema --use_ema --ema_start 1000 --start_eval 50 --test_every 5000 --save_every 2000 --num_best_copies 5 --num_save_copies 2 --loss_type kl_5 --seed 2 --which_best FID --model BigGAN --experiment_name C10Ukl5
#python train_Task1_KLWGAN_Simulation_Experiment.py --select_dataset mnist --abnormal_class 0 --shuffle --batch_size 64 --parallel --num_G_accumulations 1 --num_D_accumulations 1 --num_epochs 500 --num_D_steps 4 --G_lr 2e-4 --D_lr 2e-4 --dataset C10 --data_root ./data/ --G_ortho 0.0 --G_attn 0 --D_attn 0 --G_init N02 --D_init N02 --ema --use_ema --ema_start 1000 --start_eval 50 --test_every 5000 --save_every 2000 --num_best_copies 5 --num_save_copies 2 --loss_type kl_5 --seed 2 --which_best FID --model BigGAN --experiment_name C10Ukl5
```

The use of torch.nn.DataParallel(model) is recommended along with the use of torch.save(model.module.state_dict(), "./.pt") instead of torch.save(model.state_dict(), "./.pt"). Also, saving the best model is recommended by using "best_loss = float('inf')" and "if loss.item()<best_loss: best_loss=loss.item(); torch.save(model.module.state_dict(), "./.pt")". Downloading the image dataset one time is also recommended, e.g. "--data_root ../&lt;path-to-folder-of-dataset&gt;/data/".

After saving the trained model from Task 1: Example usage:
```
cd ./Simulations_Experiments/
python train_Task2_fGAN_Simulation_Experiment.py
```

Also, example usage:
```
cd ./Simulations_Experiments/Task2_CIFAR_MNIST_KLWGAN_Simulation_Experiment/
python train.py --select_dataset cifar10 --abnormal_class 0 --shuffle --batch_size 64 --parallel --num_G_accumulations 1 --num_D_accumulations 1 --num_epochs 500 --num_D_steps 4 --G_lr 2e-4 --D_lr 2e-4 --dataset C10 --data_root ./data/ --G_ortho 0.0 --G_attn 0 --D_attn 0 --G_init N02 --D_init N02 --ema --use_ema --ema_start 1000 --start_eval 50 --test_every 5000 --save_every 2000 --num_best_copies 5 --num_save_copies 2 --loss_type kl_5 --seed 2 --which_best FID --model BigGAN --experiment_name C10Ukl5
#python train.py --select_dataset mnist --abnormal_class 0 --shuffle --batch_size 64 --parallel --num_G_accumulations 1 --num_D_accumulations 1 --num_epochs 500 --num_D_steps 4 --G_lr 2e-4 --D_lr 2e-4 --dataset C10 --data_root ./data/ --G_ortho 0.0 --G_attn 0 --D_attn 0 --G_init N02 --D_init N02 --ema --use_ema --ema_start 1000 --start_eval 50 --test_every 5000 --save_every 2000 --num_best_copies 5 --num_save_copies 2 --loss_type kl_5 --seed 2 --which_best FID --model BigGAN --experiment_name C10Ukl5
```

Then, after saving the trained models from Tasks 1 and 2: Example usage:
```
cd ./Simulations_Experiments/
python train_Task3_fGAN_Simulation_Experiment.py
```

Example usage:
```
cd ./Simulations_Experiments/Task3_CIFAR_MNIST_KLWGAN_Simulation_Experiment/
python train.py --select_dataset cifar10 --abnormal_class 0 --shuffle --batch_size 64 --parallel --num_G_accumulations 1 --num_D_accumulations 1 --num_epochs 500 --num_D_steps 4 --G_lr 2e-4 --D_lr 2e-4 --dataset C10 --data_root ./data/ --G_ortho 0.0 --G_attn 0 --D_attn 0 --G_init N02 --D_init N02 --ema --use_ema --ema_start 1000 --start_eval 50 --test_every 5000 --save_every 2000 --num_best_copies 5 --num_save_copies 2 --loss_type kl_5 --seed 2 --which_best FID --model BigGAN --experiment_name C10Ukl5
#python train.py --select_dataset mnist --abnormal_class 0 --shuffle --batch_size 64 --parallel --num_G_accumulations 1 --num_D_accumulations 1 --num_epochs 500 --num_D_steps 4 --G_lr 2e-4 --D_lr 2e-4 --dataset C10 --data_root ./data/ --G_ortho 0.0 --G_attn 0 --D_attn 0 --G_init N02 --D_init N02 --ema --use_ema --ema_start 1000 --start_eval 50 --test_every 5000 --save_every 2000 --num_best_copies 5 --num_save_copies 2 --loss_type kl_5 --seed 2 --which_best FID --model BigGAN --experiment_name C10Ukl5
```

Next, after saving the trained models from Tasks 1, 2, and 3: Example usage:
```
cd ./Simulations_Experiments/
python train_Task3_J_fGAN_Simulation_Experiment.py
```

Also, example usage:
```
cd ./Simulations_Experiments/Task3_J_CIFAR_MNIST_KLWGAN_Simulation_Experiment/
python train.py --select_dataset cifar10 --abnormal_class 0 --shuffle --batch_size 64 --parallel --num_G_accumulations 1 --num_D_accumulations 1 --num_epochs 500 --num_D_steps 4 --G_lr 2e-4 --D_lr 2e-4 --dataset C10 --data_root ./data/ --G_ortho 0.0 --G_attn 0 --D_attn 0 --G_init N02 --D_init N02 --ema --use_ema --ema_start 1000 --start_eval 50 --test_every 5000 --save_every 2000 --num_best_copies 5 --num_save_copies 2 --loss_type kl_5 --seed 2 --which_best FID --model BigGAN --experiment_name C10Ukl5
#python train.py --select_dataset mnist --abnormal_class 0 --shuffle --batch_size 64 --parallel --num_G_accumulations 1 --num_D_accumulations 1 --num_epochs 500 --num_D_steps 4 --G_lr 2e-4 --D_lr 2e-4 --dataset C10 --data_root ./data/ --G_ortho 0.0 --G_attn 0 --D_attn 0 --G_init N02 --D_init N02 --ema --use_ema --ema_start 1000 --start_eval 50 --test_every 5000 --save_every 2000 --num_best_copies 5 --num_save_copies 2 --loss_type kl_5 --seed 2 --which_best FID --model BigGAN --experiment_name C10Ukl5
```

To run the KLWGAN-based OMASGAN model using the LOO methodology on CIFAR-10 data, run the bash script:
```
cd ./Experiments/
sh run_OMASGAN_KLWGAN_CIFAR.sh
```

Also, to run the KLWGAN-based OMASGAN using the LOO methodology on MNIST image data, run the bash script:
```
cd ./Experiments/
sh run_OMASGAN_KLWGAN_MNIST.sh
```

## Further Usage Information:

To run the code, we use a virtual environment and conda. For the versions of the libraries we use, see the requirements.txt file which has been created by using "pip freeze > requirements.txt". For installing the versions of the Python libraries we use, run "pip install -r requirements.txt".

To clone the Code Repository, run:
```
git clone https://github.com/Anonymous-Author-2021/OMASGAN.git
conda create -n OMASGAN python=3.7
conda info --envs
conda activate OMASGAN
pip install --user --requirement requirements.txt
```

This Code Repository contains a PyTorch implementation for the OMASGAN model.

Environments - Requirements: Python 3.7 and PyTorch 1.2 (requirements.txt)

Future Date: Saturday 8 May 2021: Author Notification: Release the source code, make the source code public, and make the Code Repository non-anonymous.

Future Date: Thursday 11 February 2021: Supplementary Materials Submission Deadline: This anonymous GitHub Repository will not be modified until Saturday 8 May 2021, Author Notification.

Project Website: [OMASGAN Project](https://anonymous.4open.science/r/5ccfd7f1-3316-4eeb-af38-cc4abd4843c6/).

This website is best viewed in Chrome or Firefox.

## Acknowledgements:

Thanks to the repositories: [PyTorch-Template](https://github.com/victoresque/pytorch-template "PyTorch Template"), [Generative Models](https://github.com/shayneobrien/generative-models/blob/master/src/f_gan.py), [f-GAN](https://github.com/nowozin/mlss2018-madrid-gan), and [KLWGAN](https://github.com/ermongroup/f-wgan/tree/master/image_generation).

Acknowledgement: Thanks to the repositories: [f-GAN](https://github.com/nowozin/mlss2018-madrid-gan/blob/master/GAN%20-%20CIFAR.ipynb), [GANs](https://github.com/shayneobrien/generative-models), [Boundary-GAN](https://github.com/wiseodd/generative-models/blob/master/GAN/boundary_seeking_gan/bgan_pytorch.py), [fGAN](https://github.com/wiseodd/generative-models/blob/master/GAN/f_gan/f_gan_pytorch.py), and [Rumi-GAN](https://github.com/DarthSid95/RumiGANs).

Also, thanks to the repositories: [Negative-Data-Augmentation](https://anonymous.4open.science/r/99219ca9-ff6a-49e5-a525-c954080de8a7/), [Negative-Data-Augmentation-Paper](https://openreview.net/forum?id=Ovp8dvB8IBH), and [BigGAN](https://github.com/ajbrock/BigGAN-PyTorch).

Additional acknowledgement: Thanks to the repositories: [Pearson-Chi-Squared](https://anonymous.4open.science/repository/99219ca9-ff6a-49e5-a525-c954080de8a7/losses.py), [DeepSAD](https://github.com/lukasruff/Deep-SAD-PyTorch), and [GANomaly](https://github.com/samet-akcay/ganomaly).

All the acknowledgements, references, and citations can be found in the paper "OMASGAN: Out-of-Distribution Minimum Anomaly Score GAN for Sample Generation on the Boundary".

## References:
Asokan, S. and Seelamantula, C., “Teaching a GAN What Not to Learn,” in Proceedings 34th Conference on Neural Information Processing Systems (NeurIPS 2020), Larochelle, H., Ranzato, M., Hadsell, R., Balcan, M., and Lin, H. (eds), Vancouver, Canada, December 2020.

Author, “OMASGAN: Out-of-Distribution Minimum Anomaly Score GAN for Sample Generation on the Boundary,” Submitted to International Conference on Machine Learning (ICML), 2021.

Bian, J., Hui, X., Sun, S., Zhao, X., and Tan, M., “A Novel and Efficient CVAE-GAN-Based Approach With Informative Manifold for Semi-Supervised Anomaly Detection,” in IEEE Access, vol. 7, pp. 88903-88916, June 2019. DOI: 10.1109/ACCESS.2019.2920251

Brock, A., Donahue, J., and Simonyan, K., “Large Scale GAN Training for High Fidelity Natural Image Synthesis,” in Proceedings Seventh International Conference on Learning Representations (ICLR), New Orleans, Louisiana, USA, May 2019.

Goodfellow, I., Pouget-Abadie, J., Mirza, M., Xu, B., Warde-Farley, D., Ozair, S., Courville, A., and Bengio, Y., “Generative Adversarial Nets,” in Proceedings Advances in Neural Information Processing Systems (NIPS), pp. 2672–2680, Montréal, Canada, December 2014.

Nalisnick, E.,  Matsukawa, A., Teh, Y., Gorur, D., and Lakshminarayanan, B., “Do Deep Generative Models Know What They Don’t Know?,” in Proceedings International Conference on Learning Representations (ICLR), New Orleans, USA, May 2019.

Nowozin, S., Cseke, B., and Tomioka, R., “f-GAN: Training Generative Neural Samplers using Variational Divergence Minimization,” in Proceedings Thirtieth Conference on Neural Information Processing Systems (NIPS), Barcelona, Spain, December 2016.

Pourreza, M., Mohammadi, B., Khaki, M., Bouindour, S., Snoussi, H., and Sabokrou, M., “G2D: Generate to Detect Anomaly,” in Proceedings IEEE/CVF Winter Conference on Applications of Computer Vision (WACV), pp. 2003-2012, January 2021.

Sabokrou, M., Khalooei, M., Fathy, M., and Adeli, E., “Adversarially Learned One-Class Classifier for Novelty Detection,” in Proceedings IEEE/CVF Conference Computer Vision and Pattern Recognition (CVPR), pp. 3379-3388, Salt Lake City, UT, USA, June 2018. DOI: 10.1109/CVPR.2018.00356

Sinha, A., Ayush, K., Song, J., Uzkent, B., Jin, H., and Ermon, S., “Negative Data Augmentation,” in Proceedings International Conference on Learning Representations (ICLR), May 2021.

Song, J. and Ermon, S., “Bridging the Gap Between f-GANs and Wasserstein GANs,” in Proceedings International Conference on Machine Learning (ICML), pp. 9078-9087, vol. 119, Daumé III, H. and Singh, A. (eds), July 2020.

Zaheer, M., Lee, J., Astrid, M., and Lee, S., “Old is Gold: Redefining the Adversarially Learned One-Class Classifier Training Paradigm,” in Proceedings IEEE/CVF Conference Computer Vision and Pattern Recognition (CVPR), pp. 14171-14181, Seattle, Washington, USA, June 2020. DOI: 10.1109/CVPR42600.2020.01419
