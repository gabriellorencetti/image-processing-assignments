# -----------------------------------------------------------
# Assignment 4: recovery and fourier
# SCC0251 — Image Processing
# 
# Prof. Lizeth Andrea Castellanos Beltran **********
# Aluna PAE: Leo Sampaio Ferraz Ribeiro
# Monitor: Flavio Salles
#
# 2021.1
# 
# Trabalho feito por:
# Caio Augusto Duarte Basso - NUSP 10801173
# Gabriel Garcia Lorencetti - NUSP 10691891
# -----------------------------------------------------------


import numpy as np
import imageio
import scipy
import math


####### functions definitions ######

# Function for method 1
def Adaptive_denoising(gamma, img, filter_size, mode, row):

    #new_img = np.zeros(img.shape)
    #print(row)
    crop_img = img[ row[0]:row[1],row[2]:row[3] ] #crops image based on coordenates from input

    pad_size = (filter_size - 1) // 2 # calculating padding size for each side of image
    img = np.pad(img, (pad_size, pad_size), 'symmetric') # adds padding to image

    #print(crop_img)

    new_img = img
    imgSizeX,imgSizeY = img.shape

    if (mode == "average"): # if mode is average
        dispn = np.std(crop_img) # standard deviation from cropped image
        if dispn == 0:
            dispn = 1
        for i in range (pad_size, imgSizeX - pad_size):
            for j in range (pad_size, imgSizeY - pad_size):
                a = 0
                displ = np.std(img[i-pad_size:i+pad_size, j-pad_size:j+pad_size]) # standard deviation from image area --fixthis
                centerl = np.mean(img[i-pad_size:i+pad_size, j-pad_size:j+pad_size]) # average from image area --fixthis
                
                if displ == 0:
                    displ = dispn

                new_img[i, j] = img[i, j] - gamma * (dispn/displ) * (img[i, j] - centerl) # that one formula pdf

   
    else: # if mode is robust
        q75, q25 = np.percentile(crop_img, [75, 25]) # gets iqr from cropped image
        dispn = q75 - q25
        if dispn == 0:
            dispn = 1
        for i in range (pad_size, imgSizeX - pad_size):
            for j in range (pad_size, imgSizeY - pad_size):

                q75, q25 = np.percentile(img[i-pad_size:i+pad_size, j-pad_size:j+pad_size], [75, 25]) # gets iqr from image area --fixthis
                displ = q75 - q25
                centerl = np.median(img[i-pad_size:i+pad_size, j-pad_size:j+pad_size]) # median from image area --fixthis
                
                if displ == 0:
                    displ = dispn
                
                new_img[i, j] = img[i, j] - gamma * (dispn/displ) * (img[i, j] - centerl) # that one formula pdf

    new_img = new_img[pad_size:imgSizeX-pad_size,pad_size:imgSizeY-pad_size]

    # clip image between [0,255]
    new_img = np.clip(new_img, 0, 255)
    
    return new_img

# Function for method 2
def Constrained_least_square(gamma, img, filter):
    p = np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]]) # inverse of Laplacian filter
    # adding padding
    # --fixthis (maybe)
    x,y = img.shape
    img = np.pad(img, (3,3), 'symmetric')

    N,M = img.shape
    a = int((N-3)/2)
    b = int((M-2)/2)
    p = np.pad(p, (a, b))

    n,m = filter.shape
    a = int((N-n)/2)
    b = int((M-m+1)/2)
    filter = np.pad(filter, (a, b))


    # # moving to fourrier's domain
    # img = scipy.fftpack.rfft2(img)
    # p = scipy.fftpack.rfft2(p)
    # filter = scipy.fftpack.rfft2(filter)
    # h_ = np.conj(filter)


    # moving to fourrier's domain
    img = np.fft.rfft2(img)
    p = np.fft.rfft2(p)
    filter = np.fft.rfft2(filter)
    h_ = np.conj(filter)

    F = ( h_ / (filter**2 + gamma * (p**2) ) ) * img

    # move back to visual domain
    F = np.fft.irfft2(F)
    F = np.fft.fftshift(F)
    
    # clip image between [0,255]
    F = np.clip(F, 0, 255) 

    F = F[6:x+6,6:y+6]

    return F

def Gaussian_filter (k = 3, sigma = 1.0):
    arx = np.arange ((-k // 2 ) + 1.0 , ( k // 2 ) + 1.0 )
    x, y = np.meshgrid ( arx , arx )
    filt = np.exp ( -(1/2)*( np.square ( x ) + np.square ( y ) ) / np.square ( sigma ) )
    return filt /np.sum( filt )


# Function that calculates the Root-mean-square deviation (RSME)
def RSME(g, r):
	x, y = g.shape
	return math.sqrt((np.sum(np.square(g - r)))/(x*y))
####################################

####### input reading #######
_img_ref_name = input().rstrip() # read reference image's name
_img_deg_name = input().rstrip() # read degraded image's name
_func_used = int(input()) # read chosen function's id 1 <= x <= 2
_gamma = float(input()) # read parameter γ


if _func_used == 1: # if using method 1 (Adaptive Denoising)
    _row = list(map(int, input().split()))
    _filter_size = int(input())
    _mode = input().rstrip() # read denoising mode: "average" or "robust"

elif _func_used == 2: # if using method 2 (Constrained Least Squares)

    _filter_size = int (input())
    _sigma = float (input()) # reads σ for the gaussian filter

##############################

####### reading image #######
img = imageio.imread(_img_deg_name)
ref_img = imageio.imread(_img_ref_name)
#############################

###### restoring image ######
###### restoring image ######
if _func_used == 1:
    new_img = Adaptive_denoising(_gamma, img, _filter_size, _mode, _row)

elif _func_used == 2:
    filter = Gaussian_filter(_filter_size, _sigma)
    new_img = Constrained_least_square(_gamma, img, filter)

#### Comparing with reference image ####

print("%.4f" % RSME(new_img, ref_img)) # printing the rsme value
#################################