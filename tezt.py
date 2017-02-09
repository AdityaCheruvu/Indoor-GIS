import scipy
from PIL import Image
from scipy import ndimage
import matplotlib.pyplot as plt
import numpy as np
import Image
import PIL.ImageOps
from skimage.measure import label

image = Image.open('mukul.jpg')

inverted_image = PIL.ImageOps.invert(image)

inverted_image.save('new_mukul.jpg')
im2 = Image.open('new_mukul.jpg')
im2 = ndimage.binary_dilation(im2)
im2 = ndimage.binary_dilation(im2)
im2 = ndimage.binary_dilation(im2)
scipy.misc.imsave('dilation.jpg', im2)
#im = Image.open('flower.png')
im = ndimage.imread('dilation.jpg')
im = ndimage.binary_erosion(im).astype(np.float32)
scipy.misc.imsave('erosion.jpg', im)

X=np.array([[0,0,1,1],[0,0,0,0],[1,1,0,0]])
Y='erosion.jpg'
data = np.asarray( im, dtype="bool" )
for i in (x[0][0] for x in data):
	print i

yay = label(data,background = 1,return_num=True)
#print yay
