import os, sys
from PIL import Image
from scipy import misc


outfile = "20x20.png"
im = Image.open(outfile)
M = misc.imread(outfile)
for x in M:
    for y in x:
        print y
for x in M:
    for y in x:
        if y[3] > 0:
            y[3] = 255

for x in M:
    for y in x:
        temp = sum(y[:3])
        if temp > 0 and temp < 765:
            y[0] = 0
            y[1] = 0
            y[2] = 0
            y[3] = 0
for x in M:
    for y in x:
        if sum(y) != 765:
            y[0] = -1
            y[1] = -1
            y[2] = -1
            y[3] = -1
for x in M:
    for y in x:
        if sum(y) == 0:
            y[0] = 255
            y[1] = 255
            y[2] = 255
            y[3] = 255
            
for x in M:
    for y in x:
        if sum(y) == -4:
            y[0] = 0
            y[1] = 0
            y[2] = 0
            y[3] = 0

misc.toimage(M).show()



