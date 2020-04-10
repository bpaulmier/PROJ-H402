#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 14:11:14 2020

@author: benjaminpaulmier
"""

import cv2 as cv
import time

def regExtractionFrames(videoName,numberOfFrames):
    a = time.time()
    vidcap = cv.VideoCapture('/Users/benjaminpaulmier/downloads/'+videoName+'.MOV') #vidcap contains the video
    nextFrameExists,image = vidcap.read() # "read" grabs, decodes and returns the next frame
    count = 1
    totalFrames = int(vidcap.get(cv.CAP_PROP_FRAME_COUNT))
    while nextFrameExists:
        if (count%(int(totalFrames/numberOfFrames))==0): #get an even distribution of frames throughout the video
            cv.imwrite('/Users/benjaminpaulmier/downloads/regFrames/frame%d.jpg' % count, image)
        nextFrameExists,image = vidcap.read()
        count +=1
    print ("Number of frames counted : ")
    return count-1, time.time()-a