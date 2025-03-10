﻿# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 10:39:25 2021

@author: admin
"""
from sklearn.manifold import TSNE
import os
import torch
import torchvision
import torch.nn as nn
import torchvision.transforms as transforms
import torch.optim as optim
import torch.nn.functional as F
import matplotlib.pyplot as plt
from torchvision import datasets
from torch.utils.data import DataLoader
from torchvision.utils import save_image
# from Tools import filters, JSMA
from torchvision import utils as vutils
import numpy as np
from collections import OrderedDict
import random
# from frank_wolfe import FrankWolfe
# from autoattack import AutoAttack
import advertorch
from advertorch.attacks import LinfPGDAttack, CarliniWagnerL2Attack, DDNL2Attack, SinglePixelAttack, LocalSearchAttack, SpatialTransformAttack,L1PGDAttack
from autoattack import AutoAttack
from models.LeNet import LeNet5_autoencoder, LeNet5_encoder, Decoder, Classifier_head, LeNet5, LeNet5_STA, LeNet5_tsne, LeNet5_dnet
from models.ResNet import ResNet18_MNIST, ResidualBlock, ResNet50_MNIST, ResNet101_MNIST
import torchvision.transforms as transforms

# basic settings
seed = 0
torch.manual_seed(seed)  # 为CPU设置随机种子
torch.cuda.manual_seed(seed)  # 为当前GPU设置随机种子
torch.cuda.manual_seed_all(seed)  # 为所有GPU设置随机种子
random.seed(seed)
np.random.seed(seed)
os.environ['PYTHONHASHSEED'] = str(seed)  # 为了禁止hash随机化，使得实验可复现。
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
NUM_EPOCHS = 200
LEARNING_RATE = 1e-3
BATCH_SIZE = 256


# def save_decoded_image(img, name):
#     img = img.view(img.size(0), 3, 32, 32)
#     save_image(img, name)
#

###preprocess###
transform = transforms.Compose(
    [transforms.ToTensor()
     ]
)

trainset = datasets.MNIST(
    root='./MNIST_data',
    train=True,
    download=False,
    transform=transform
)
testset = datasets.MNIST(
    root='./MNIST_data',
    train=False,
    download=False,
    transform=transform
)

trainloader = DataLoader(
    trainset,
    batch_size=BATCH_SIZE,
    shuffle=False
)
testloader = DataLoader(
    testset,
    batch_size=BATCH_SIZE,
    shuffle=True
)


#
# # pixel constrain
# FGSM_N = advertorch.attacks.GradientSignAttack(predict=model, loss_fn=nn.CrossEntropyLoss(reduction="sum"))
#
# FGSM_T = advertorch.attacks.GradientSignAttack(predict=model, loss_fn=nn.CrossEntropyLoss(reduction="sum"),
# targeted=True)
#
# MMT_N = advertorch.attacks.MomentumIterativeAttack(predict=model, loss_fn=nn.CrossEntropyLoss(), eps=0.3, nb_iter=40,
#                                                    decay_factor=1.0, eps_iter=0.01,
#                                                    clip_min=0.0, clip_max=1.0, targeted=False)
# MMT_T = advertorch.attacks.MomentumIterativeAttack(predict=model, loss_fn=nn.CrossEntropyLoss(), eps=0.3, nb_iter=40,
#                                                    decay_factor=1.0, eps_iter=0.01,
#                                                    clip_min=0.0, clip_max=1.0, targeted=True)
# BIM_N = advertorch.attacks.LinfBasicIterativeAttack(predict=model, loss_fn=nn.CrossEntropyLoss(), eps=0.3, nb_iter=40,
#                                                     eps_iter=0.05,
#                                                     clip_min=0.0, clip_max=1.0, targeted=False)
# BIM_T = advertorch.attacks.LinfBasicIterativeAttack(predict=model, loss_fn=nn.CrossEntropyLoss(), eps=0.5, nb_iter=40,
#                                                     eps_iter=0.05,
#                                                     clip_min=0.0, clip_max=1.0, targeted=True)
#
# PGD_N = LinfPGDAttack(
#             model, loss_fn=nn.CrossEntropyLoss(reduction="sum"), eps=0.30,
#             nb_iter=40, eps_iter=0.01, rand_init=True, clip_min=0.0, clip_max=1.0, targeted=False)
#
# PGD_T = LinfPGDAttack(
#             model, loss_fn=nn.CrossEntropyLoss(reduction="sum"), eps=0.50,
#             nb_iter=40, eps_iter=0.01, rand_init=True, clip_min=0.0, clip_max=1.0, targeted=True)
#
#
# CW_N = CarliniWagnerL2Attack(
#     model, 10, clip_min=0.0, clip_max=1.0, max_iterations=500, confidence=1, initial_const=1, learning_rate=1e-2,
#     binary_search_steps=4, targeted=False)
#
# CW_T = CarliniWagnerL2Attack(
#     model, 10, clip_min=0.0, clip_max=1.0, max_iterations=500, confidence=1, initial_const=1, learning_rate=1e-2,
#     binary_search_steps=4, targeted=True)
#
# DDN = DDNL2Attack(model, nb_iter=100, gamma=0.05, init_norm=1.0, quantize=True, levels=256, clip_min=0.0,
#                         clip_max=1.0, targeted=False, loss_fn=None)
#
# STA = SpatialTransformAttack(
#     model, 10, clip_min=0.0, clip_max=1.0, max_iterations=5000, search_steps=20, targeted=False)
#
# AA_N = AutoAttack(model, norm='Linf', eps=0.3, version='standard')
#
# JSMA_T = advertorch.attacks.JacobianSaliencyMapAttack(predict=model, num_classes=10, clip_min=0.0, clip_max=1.0,
#                                                     loss_fn=None, theta=1.0, gamma=1.0,
#                                                     comply_cleverhans=False)
#
# # spatial constrain
# # DDN
# DDN_N = DDNL2Attack(model, nb_iter=100, gamma=0.05, init_norm=1.0, quantize=True, levels=256, clip_min=0.0,
#                         clip_max=1.0, targeted=False, loss_fn=None)
#
#
# # STA
# STA_N = SpatialTransformAttack(
#     model, 10, clip_min=0.0, clip_max=1.0, max_iterations=5000, search_steps=20, targeted=False)



'''
训练目标模型
'''

# model = LeNet5().cuda().train()
# targetlabel = torch.zeros(BATCH_SIZE).cuda()
# targetlabel = targetlabel.to('cuda', dtype=torch.int64)
# optimizer = torch.optim.Adam(model.parameters(), lr=0.001, betas=(0.9, 0.99))
# criterion_cls = nn.CrossEntropyLoss()
# train_loss = []
# for epoch in range(NUM_EPOCHS):
#     running_loss = 0.0
#     for img, label in trainloader:
#         targetlabel_temp = targetlabel[0:img.shape[0]]
#         img, label = img.cuda(), label.cuda()
#         optimizer.zero_grad()
#         predict = model(img)
#         loss = criterion_cls(predict, label)
#         loss.backward()
#         optimizer.step()
#         running_loss += loss.item()
#     loss = running_loss / len(trainloader)
#     train_loss.append(loss)
#     print('Epoch {} of {}, Train Loss: {:.6f}, '.format(epoch + 1, NUM_EPOCHS, loss))
# torch.save(model, './saving_models/Revision/MNIST_LeNet5.pkl')


'''
训练教师模型
'''
# lenet_mnist_aotoencoder = LeNet5_autoencoder().cuda()
# lenet_mnist_aotoencoder.train()
# optimizer = torch.optim.Adam(lenet_mnist_aotoencoder.parameters(), lr=0.0001, betas=(0.9, 0.99))
# criterion_cls = nn.CrossEntropyLoss()
# criterion_rec = nn.MSELoss()
# train_loss = []
# for epoch in range(200):
#     running_loss = 0.0
#     for img, label in trainloader:
#         img, label = img.cuda(), label.cuda()
#         optimizer.zero_grad()
#         predict, img_rec = lenet_mnist_aotoencoder(img)
#
#         cls_loss, rec_loss = criterion_cls(predict, label), criterion_rec(img_rec, img)
#         loss = cls_loss + rec_loss
#         loss.backward()
#         optimizer.step()
#         running_loss += loss.item()
#     loss = running_loss / len(trainloader)
#     train_loss.append(loss)
#     print('Epoch {} of {}, Train Loss: {:.6f}, Cls Loss: {}, Rec_loss: {}'.format(epoch + 1, NUM_EPOCHS, loss, cls_loss, rec_loss ))
#
# torch.save(lenet_mnist_aotoencoder, './saving_models/LeNet5_MNIST_AE.pkl')





# test
total = 0
correct = 0
temp = 0
model = torch.load('./saving_models/LeNet5_MNIST_AE.pkl')
targetlabel = torch.zeros(BATCH_SIZE).cuda()
targetlabel = targetlabel.to('cuda', dtype=torch.int64)
for img, label in testloader:
    length = img.shape[0]
    targetlabel_temp = targetlabel[0:length]
    img, label = img.cuda(), label.cuda()

    # img_adv = BIM_N.perturb(img)
    # img_adv = BIM_T.perturb(img, targetlabel_temp)
    # img_adv = AA_N.run_standard_evaluation(img, label, bs=BATCH_SIZE)

    # teacher network
    _, x = model(img)
    _, prediction = torch.max(_, 1)

    # student network
    # x = model(img)
    # _, prediction = torch.max(x, 1)
    total += label.size(0)
    correct += (prediction == label).sum()
    # vutils.save_image(img_adv, './saving_samples/AA_N/img_adv_{}.jpg'.format(temp))
    print('当前temp:', temp, '当前batch正确的个数:', (prediction == label).sum())
    temp += 1
print('mnist teacher network')
print('There are ' + str(correct.item()) + ' correct pictures.')
print('Accuracy=%.2f' % (100.00 * correct.item() / total))
























