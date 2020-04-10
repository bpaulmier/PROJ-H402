#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 22:24:56 2020

@author: benjaminpaulmier

IMPORTANT : Before shooting yout video, please make sure that the environment is 
well-lit, that there are no hard shadows and no glossy or transparent effects on
the object of interest (use of spray paint is recommended if there are).

Please use a fixed lens (no focal change), do not move the object of interest
while filming and avoid movements in the background. Make sure the object of 
interest remains in the center of your frames as much as possible and avoid
moving around the object too quickly.

"""

import cv2 as cv
import os
import shutil
#from matplotlib import pyplot as plt, if we want to visualize things along the way
#(cv.imshow crashes kernel on my comlputer for some reason so pyplot is needed...)
import numpy as np
import time #to measure performance

def varianceOfLaplacian(image): #to evaluate frame blurriness
    return cv.Laplacian(image, cv.CV_64F).var()

def overlapPercentageFLANN(img1,img2): #FLANN is much, much faster ! x10
    #load images, resize and convert to grayscale to make the process faster
    img1 = cv.resize(img1, (0,0), fx=0.5, fy=0.5)
    img2 = cv.resize(img2, (0,0), fx=0.5, fy=0.5)
    img1=cv.cvtColor(img1, cv.COLOR_BGR2GRAY)
    img2=cv.cvtColor(img2, cv.COLOR_BGR2GRAY)
    
    # Prepare for SURF image analysis
    surf = cv.xfeatures2d.SURF_create(4000)

    # Find keypoints and point descriptors for both images
    kp1, des1 = surf.detectAndCompute(img1, None)
    kp2, des2 = surf.detectAndCompute(img2, None)
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv.FlannBasedMatcher(index_params, search_params)

    # Find matches between the descriptors
    try:
        matches = flann.knnMatch(des1, des2, k=2)
    except cv.error:
        return (0,0)
    good = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance: #for FLANN the parameter is higher
            good.append(m)
    MIN_MATCH_COUNT = 10
    if len(good) > MIN_MATCH_COUNT:
        #calculate homography matrix
        srcPoints = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
        dstPoints = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
        H, __ = cv.findHomography(srcPoints, dstPoints, cv.RANSAC, 5)
        if H is not None:
            #get the translations and overlap percentages
            tx = abs(H[0][2])
            ty = abs(H[1][2])
            px = (1-tx/(len(img1[0])))*100
            py = (1-ty/(len(img1)))*100
        else:
            return (0,0)
    else:
        #print('images not similar enough')
        return (0,0) #consider there's no overlap if the images aren't similar enough to find good features
    #print('Horizontal overlap : %f' % px +' %')
    #print('Vertical overlap : %f' % py + ' %')
    return (px,py)

def extractFrames(videoName,blurThresh,overlapThresh,nbrOfFrames): #recommended blurThresh : 100 or 150, recommended overlapThresh : 2, recommended nbrOfFrames : 150
    a = time.time() #to measure how long the algorithm is
    goodFrames=[]
    vidcap = cv.VideoCapture('/Users/benjaminpaulmier/downloads/'+videoName+'.MOV')
    #vidcap contains the video
    nextFrameExists,image = vidcap.read()
    #"read" grabs, decodes and returns the next frame
    count = 1
    #create the folder in which non-blurry images will be kept
    os.mkdir('/Users/benjaminpaulmier/downloads/allFrames/')
    while nextFrameExists:
        #first filter: 'blur filter'
        cv.imwrite('/Users/benjaminpaulmier/downloads/allFrames/frame%d.jpg' % count, image)  #imwrite saves an image to a specified file.
        src = cv.imread('/Users/benjaminpaulmier/downloads/allFrames/frame%d.jpg' % count)
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
        VoL = varianceOfLaplacian(finalRect)
        #print(VoL) #(to get an idea of where to fix the threshold)
        if VoL < blurThresh:
            os.remove('/Users/benjaminpaulmier/downloads/allFrames/frame%d.jpg' % count)
        else:
            goodFrames.append(src)
        nextFrameExists,image = vidcap.read()
        count +=1
    b = len(goodFrames)
    if b<30:
        shutil.rmtree('/Users/benjaminpaulmier/downloads/allFrames/')
        return 'Video is too blurry. Please set a lower blur threshold or record a new video, try moving slower around the object.'
    else:
        #second filter: 'overlap filter'
        i=0
        consecutiveDiffFrames=0 #counter of how many frames in a row don't look alike enough
        while i<(len(goodFrames)-2): #rather than a for i in range len, because the length of goodFrames is updated whenever there is a pop
            first = overlapPercentageFLANN(goodFrames[i],goodFrames[i+1])
            second = overlapPercentageFLANN(goodFrames[i],goodFrames[i+2])
            horiz = abs(first[0]-second[0])
            vert = abs(first[1]-second[1])
            
            if (horiz<overlapThresh and vert<overlapThresh):
                goodFrames.pop(i+1)
                consecutiveDiffFrames=0 #reset the value to zero
                """i -= 1 #set i one step back to keep comparing the first frame considered with the next one : didn't go through with this idea because it was too long and removed too many frames. Here, we remove 1 out of 2 frames max."""
                i += 1
            else:
                consecutiveDiffFrames += 1
                i +=1
                if (consecutiveDiffFrames>25): #15 was a good value according to my tests...
                    shutil.rmtree('/Users/benjaminpaulmier/downloads/allFrames/')
                    return 'Not enough overlap on the good frames. Please record a new video or set a lower blur threshold / overlap threshold.'
            
    #Filter out the unevenly lit images ? too long, not that useful if the user follows the rules. MAKE A RULE SET AT THE BEGINNING !
    b = len(goodFrames)
    if b<10:
        shutil.rmtree('/Users/benjaminpaulmier/downloads/allFrames/')
        return 'Not enough good frames. Please record a new video or set a lower blur threshold.'
    else:
        #third and final filter, arbitrary filter
        finalFrames=goodFrames
        if b>nbrOfFrames: #remove frames from goodFrames to reach approx. the wanted number of frames in the final folder
            finalFrames=[]
            approxRatio = int(b/nbrOfFrames)
            for i in range(nbrOfFrames-1): #-1 in case the exact ratio is an int
                finalFrames.append(goodFrames[i*approxRatio])

        os.mkdir('/Users/benjaminpaulmier/downloads/good'+videoName+'Frames/')
        for i in range(len(finalFrames)):
            cv.imwrite('/Users/benjaminpaulmier/downloads/good'+videoName+'Frames/frame%d.jpg' % (i+1), finalFrames[i])

    shutil.rmtree('/Users/benjaminpaulmier/downloads/allFrames/')

    return time.time()-a


# try with extractFrames('fauteuil',160,1,150)