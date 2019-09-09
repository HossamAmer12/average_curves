# -*- coding: utf-8 -*-
# Hossam Amer
# Run using this way: python3 interpolateFiles.py


# path_to_txt_files ='Gen/Seq-Stats/'

# unified files
path_to_txt_files='/Users/hossam.amer/7aS7aS_Works/work/workspace/TESTS/hevc_intraML_bits/bin/Build/Products/Release/Gen/Seq-Stats-Unified/'

start = 1
# end = 1100
end = 5000
# end = 100


import math
import glob

import numpy as np 

import matplotlib.pyplot as plt
  
def readFileContents(image):
	f = open(image, "r")	
	bpp, msssim, psnr = np.loadtxt(f, delimiter ='\t', usecols =(0, 1, 2), unpack = True)
	f.close()
	return bpp, msssim, psnr


def createXBins(minsBpp, maxsBpp, stepSize=0.05):
	# Get the overlapping range
	minBin = max(minsBpp)
	maxBin = min(maxsBpp)

	# Define your bins for bits per pixel (X-axis)
	binsX = []

	# Append the smallest bin to take care of all bins before the next bin
	binsX.append(minBin)

	start = round(minBin+0.05, 1)
	end   = round(maxBin-0.05, 1)

	for x in np.arange(start, end, stepSize):
		binsX.append(round(x, 2))
	
	return binsX

def createBinsMapIndex(bppAll, binsX, psnrAll, mssimAll, nBins = 200):
	# Initialize binsMap to all zeros (must be all zeros)
	binsMap = [0] * len(bppAll)

	# Initialize the sum arrays
	sumPSNR  = [0] * nBins
	sumMSSIM = [0] * nBins

	# Initilize len arrays:
	lenPSNR  = [0] * nBins
	lenMSSIM = [0] * nBins

	# Create a bins map
	for i in range(len(bppAll)):
		x = bppAll[i]
		if (x > binsX[-1]):
			binsMap[i] = -1 # ignore this one in the calculations
		else:
			if(x >= binsX[1]):
				try:
					binsMap[i] = binsX.index(round(x, 1))
					sumPSNR[binsMap[i]]   = sumPSNR[binsMap[i]]  + psnrAll[i]
					sumMSSIM[binsMap[i]]  = sumMSSIM[binsMap[i]] + mssimAll[i]
					lenPSNR[binsMap[i]]   = 1 + lenPSNR[binsMap[i]]
					lenMSSIM[binsMap[i]]  = 1 + lenMSSIM[binsMap[i]]

				except ValueError:
					binsMap[i] = -1 # ignore this one in the calculations
			else:
				sumPSNR[0]   = sumPSNR[0]  + psnrAll[i]
				sumMSSIM[0]  = sumMSSIM[0] + mssimAll[i]
				lenPSNR[0]   = 1 + lenPSNR[0]
				lenMSSIM[0]  = 1 + lenMSSIM[0]

	return binsMap, sumPSNR, sumMSSIM, lenPSNR, lenMSSIM

def getAveragePSNRSSIM(binsX, binsMapIndex, bppAll, sumPSNR, sumMSSIM, lenPSNR, lenMSSIM):
	YSSIM = []
	YPSNR = []
	deletedIndices = []


	# compute the average curve for each bin
	for i in range(len(binsX)):
		# print('Iteration: %d' % i)
		# find all occurances of the current bin

		assert(lenPSNR[i] == lenMSSIM[i]) # they have to be the same
		numOccurances = lenPSNR[i] # this is correct or lenSSIM[i], should be the same

		# only consider if index occurances are not empty (won't interpolate)
		if numOccurances:
			# Compute Average PSNR
			sumPSNR_val = sumPSNR[i]
			avgPSNR_val = 1.0*sumPSNR_val/numOccurances

			# print(sumPSNR == sumPSNR[i])
			# print(sumPSNR_val, indexOcurrances)

			# append to PSNR
			YPSNR.append(avgPSNR_val)

			# Compute Average MSSIM
			sumMSSIM_val = sumMSSIM[i]
			avgSSIM_val = 1.0*sumMSSIM_val/numOccurances


			# print(avgSSIM_val == 1.0*sumMSSIM[i]/lenMSSIM[i])

			# append to MSSIM
			YSSIM.append(avgSSIM_val)
		else:
			deletedIndices.append(i)

	# 	if i == 16:
	# 		print(len(binsX))
	# 		print('Length: ', len(YSSIM))
	# 		for ii in range(len(binsX)):
	# 			indexOcurrances = [j for j, value in enumerate(binsMapIndex) if value == ii]
	# 			numOccurances = len(indexOcurrances)
	# 			print(ii, ') Source: ')
	# 			sumVal = 0
	# 			for index, val in enumerate(mssimAll):					
	# 				if index in indexOcurrances:
	# 					sumVal = sumVal + val
	# 					print(bppAll[index], val)

	# 			if not numOccurances:
	# 				print('Number of occurances is 0 in ', ii)
	# 			else:
	# 				print(ii, ') Source bin %f and Corresponding SSIM %f' % (binsX[ii], YSSIM[ii]))
	# 		break

	# exit(0)
	# Delete the bins that were not found
	binsX = [elem for index, elem in enumerate(binsX) if index not in deletedIndices]
	return binsX, YSSIM, YPSNR, deletedIndices

#### Main: 


# Define your accumulator lists
bppAll = []
mssimAll = []
psnrAll = []

# Define mins/maxs of each bits per pixel
minsBpp = []
maxsBpp = []

# Create bpp ORG, SSIM Org, PSNR ORG lists.
for imgID in range(start, end):

	original_img_ID = imgID
	imgID = str(imgID).zfill(8)
	shard_num  = round(original_img_ID/10000);
	folder_num = math.ceil(original_img_ID/1000);
	filesList = glob.glob(path_to_txt_files + 'ILSVRC2012_val_' + imgID + '*.txt')	
	name = filesList[0].split('/')[-1]
	rgbStr = name.split('_')[-1].split('.')[0]
	width  = int(name.split('_')[-3])
	height = int(name.split('_')[-2])

	image = path_to_txt_files + 'ILSVRC2012_val_' + imgID + '_' + str(width) + '_' + str(height) + '_' + rgbStr + '.txt'
	bpp, msssim, psnr = readFileContents(image)

	minsBpp.append(min(bpp))
	maxsBpp.append(max(bpp))

	bppAll.extend(bpp)
	mssimAll.extend(msssim)
	psnrAll.extend(psnr)

	if not original_img_ID % 50:
		print('Collecting info done with %s images.' % imgID)

# print(bppAll)

print('Collecting info is Done')

# Define your bins for bits per pixel
binsX = []
binsY = []
binsX = createXBins(minsBpp, maxsBpp, 0.05)

print('createXBins Done')

# print(len(binsX)) # 98

# Create a binsMap to map each value in the data into a specific bin index
binsMapIndex, sumPSNR, sumMSSIM, lenPSNR, lenMSSIM = createBinsMapIndex(bppAll, binsX, psnrAll, mssimAll)

print('createBinsMapIndex Done')

# Average curves
binsX, YSSIM, YPSNR, deletedIndices = getAveragePSNRSSIM(binsX, binsMapIndex, bppAll, sumPSNR, sumMSSIM, lenPSNR, lenMSSIM)

print('getAveragePSNRSSIM Done')
# print(binsX)
# print(len(YSSIM))
# print(YPSNR)


# fig = plt.figure()
# plt.hist(bppAll, bins = len(binsX))
# plt.hist(bppAll, bins = )


fig = plt.figure()
plt.plot(binsX, YSSIM, '-o')


fig = plt.figure()
plt.plot(binsX, YPSNR, '-o')

plt.show()