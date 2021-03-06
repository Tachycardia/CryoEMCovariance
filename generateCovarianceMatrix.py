#!/usr/bin/env python3
# Program: Generate Covariance Matrix
# Author: Darren Trieu Nguyen
# Version: 1.0
# Function: Takes in multiple npy files containing distance difference matrices
#           and calculates a covariance matrix. 

import sys
import argparse
import numpy as np
import time
import os

""" Class that houses Generate Covariance Matrix
"""
class GenerateCovarianceMatrix:

    """ Extracts the distance difference values from a given difference
        matrix and outputs it into a list
    """
    def extractDistDiff(self, distDiffMatrixPath):

        differenceMatrix = np.load(distDiffMatrixPath)
        distanceDifferenceList = np.zeros(int((len(differenceMatrix)\
                                *(len(differenceMatrix)-1))/2))
        i = 0
        for j in range(len(differenceMatrix)):
            for k in range(len(differenceMatrix)):
                if k > j:
                    distanceDifferenceList[i] = differenceMatrix[j][k]
                    i += 1

        return distanceDifferenceList

    """ Computes the covariance matrix given a list of paths to (npy files)
        distance difference matrices
    """
    def calcCovarianceMatrix(self, npyList):
        distDiffListList = []
        for index, npy in enumerate(npyList):
            distDiffListList.append(self.extractDistDiff(npy))
        covarianceMatrix = np.cov(distDiffListList, rowvar=False)
        return covarianceMatrix
        
""" Handles options from the CLI when called as a script
"""
if __name__ == '__main__':
    version = 1.0

    # Parsing the CLI for options and parameters
    parser = argparse.ArgumentParser(description='Generate a'\
        ' covariance matrix for a given distance difference matrix')
    parser.add_argument('npy', metavar='npy', nargs='+',
                        help='npy file(s) that contain distance'\
                        'difference matrix(ices)')
    parser.add_argument('-v', '--verbose',
                       help='Increases output verbosity',\
                       action='store_true')
    parser.add_argument('--processes',
                        dest='processQuantity',
                        default=os.cpu_count(),
                        const=1,
                        action='store',
                        nargs='?',
                        type=int,
                        help='The number of separate processes the'
                        ' computation will be split into')
    args = parser.parse_args()

    gCovarianceMatrix = GenerateCovarianceMatrix()

    print(gCovarianceMatrix.calcCovarianceMatrix(args.npy))

