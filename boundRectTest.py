#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 19:53:53 2020

@author: benjaminpaulmier
"""
import cv2 as cv
import os
import time #to measure performance


def extractFramesWithoutBR(videoName):
    a=time.time()
    vidcap = cv.VideoCapture('/Users/benjaminpaulmier/downloads/'+videoName+'.MOV') #vidcap contains the video
    nextFrameExists,image = vidcap.read() # "read" grabs, decodes and returns the next frame
     #create the folder in which the frames will be kept
    os.mkdir('/Users/benjaminpaulmier/downloads/frames1/')
    count=1
    while nextFrameExists:
        cv.imwrite('/Users/benjaminpaulmier/downloads/frames1/frame%d.jpg' % count, image)
        nextFrameExists,image = vidcap.read()
        count +=1
    return time.time()-a

def extractFramesWithBR(videoName):
    a=time.time()
    vidcap = cv.VideoCapture('/Users/benjaminpaulmier/downloads/'+videoName+'.MOV') #vidcap contains the video
    nextFrameExists,image = vidcap.read() # "read" grabs, decodes and returns the next frame
     #create the folder in which the frames will be kept
    os.mkdir('/Users/benjaminpaulmier/downloads/frames2/')
    count=1
    while nextFrameExists:
        cv.imwrite('/Users/benjaminpaulmier/downloads/frames2/frame%d.jpg' % count, image)  #imwrite saves an image to a specified file.
        src = cv.imread('/Users/benjaminpaulmier/downloads/frames2/frame%d.jpg' % count)
        gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
        gray = cv.blur(gray, (5,5)) #to eliminate "false" contours
        
        # Detect edges using Canny edge detection
        canny_output = cv.Canny(gray, 100, 200)
        # Find contours
        _, contours, hierarchy = cv.findContours(canny_output, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        # Approximate contours to polygons + get bounding rects
        contours_poly = [None]*len(contours)
        boundRect = [None]*len(contours)
        for i, c in enumerate(contours):
            contours_poly[i] = cv.approxPolyDP(c, 3, True)
            boundRect[i] = cv.boundingRect(contours_poly[i])
        #Calculate the final cropped ROI
        keyValues = [boundRect[0][0],boundRect[0][1],boundRect[0][0]+boundRect[0][2],boundRect[0][1]+boundRect[0][3]]
        for i in range(1,len(boundRect)):
            if boundRect[i][0] < keyValues[0]:
                keyValues[0] = boundRect[i][0]
            if boundRect[i][1] < keyValues[1]:
                keyValues[1] = boundRect[i][1]
            if boundRect[i][0]+boundRect[i][2] > keyValues[2]:
                keyValues[2] = boundRect[i][0]+boundRect[i][2]
            if boundRect[i][1]+boundRect[i][3] > keyValues[3]:
                keyValues[3] = boundRect[i][1]+boundRect[i][3]
        #Obtain cropped image of ROI
        finalRect = src[keyValues[1]:keyValues[3], keyValues[0]:keyValues[2]]
        #finalRect won't be used, this is simply to test the time it takes to compute it
        nextFrameExists,image = vidcap.read()
        count +=1
    return time.time()-a