#!/usr/bin/env python3
# Program: Compare PDB
# Author: Darren Trieu Nguyen
# Version: 1.0
# Function: Takes in two PDB files to compare
#           Outputs two edited PDB files that are aligned for calculation

import argparse
import sys
import os
import numpy as np
import pandas as pd
import logging
import inspect
import collections
from pdbReader import PDBReader

""" Class that houses Compare PDB
"""
class ComparePDB:

    """ Initialization function
        Handles options from the CLI
    """
    def __init__(self):
        # When called directly from script
        if __name__ == '__main__':
            version = 1.0
            
            # Parsing the CLI for options and parameters
            parser = argparse.ArgumentParser(
                description='Compare two PDB files'
            )
            parser.add_argument('pdb', metavar='file', nargs='+',
                                help='pdb file(s) to compare')
            parser.add_argument('--strip', help='Removes side chains',\
                                action='store_true')
            parser.add_argument('-v', '--verbose', 
                                help='Increases output verbosity',\
                                action='store_true')
            parser.add_argument('--log', nargs='?', default='WARNING',
                                help='Controls logging verbosity based off of'\
                                ' log message priority. Levels include:'\
                                'DEBUG, INFO, WARNING, ERROR, CRITICAL')

            args = parser.parse_args()

            # Initializing log file and log level
            logLevel = args.log
            logFile = None

            # Initalizing logging
            logger = logging.getLogger(self.__class__.__name__)

            numeric_level = getattr(logging, logLevel.upper(), None)
            if not isinstance(numeric_level, int):
                raise ValueError('Invalid log level: %s' % logLevel)
            if logFile is not None:
                logging.basicConfig(filename=logFile, filemode='w', \
                                    level=numeric_level)
            else:
                logging.basicConfig(level=numeric_level)

            self.logger = logger

            # TODO: Doesn't accurately compare unless the stripped flag is true
            self.compare(args.pdb, args.strip)

        # When called from another script
        else:
            # Initalizing logging
            frame = inspect.currentframe().f_back
            try:
                try:
                    self_obj = frame.f_locals['self']
                    logName = type(self_obj).__name__
                except KeyError:
                    logName = self.__class__.__name__
            finally:
                del frame
                    
            logger = logging.getLogger(logName + '.' \
                                       + str(self.__class__.__name__))
            self.logger = logger

    """ Takes in a list of paths to pdb files, compares the n number of passed 
        pdb files
    """
    def compare(self, pdbList, strip, inPath=None, outPath=None, baseList=None):

        # Defining a dictionary that points to the molecule furthest
        # away from the alpha carbon in each type of amino acid
        AAMidpointDict = { 
            'ALA' : 'CB',
            'ARG' : 'CZ',
            'ASN' : 'CG',
            'ASP' : 'CG',
            'CYS' : 'SG',
            'GLU' : 'CD',
            'GLN' : 'CD',
            'GLY' : 'CA',
            'HIS' : 'CE1',
            'ILE' : 'CD1',
            'LEU' : 'CG',
            'LYS' : 'NZ',
            'MET' : 'CE',
            'PHE' : 'CZ',
            'PRO' : 'CD',
            'SER' : 'OG',
            'THR' : 'OG1',
            'TRP' : 'CH2',
            'TYR' : 'OH',
            'VAL' : 'CB',
        }

        # Reads the csv files into a Pandas dataframe
        # (Dataframes will allow for better manipulations for further
        #  expansions of this code)
        # Then filters the dataframes to Residue Numbers (indices) that are 
        # common to both frames

        pdbr = PDBReader()
        
        pdbFrameList = [None]*len(pdbList)
        for index, pdb in enumerate(pdbList):
            if inPath is None:
                pdbFrame = pdbr.PDBToDataFrame(pdb)
            else:
                pdbFrame = pdbr.PDBToDataFrame(os.path.join(inPath, pdb))
            pdbFrameList[index] = pdbFrame

        pdbFrameFilteredList = [None]*len(pdbList)
        for index, pdbFrame in enumerate(pdbFrameList):

            # Filtering for ATOM
            pdbFrame = pdbFrame.loc[\
                            (pdbFrame['Atom Type'].str.strip() == 'ATOM')\
                        ]

            # Changing the alpha carbon coordinates to the midpoint between
            # the alpha carbon and the furthest atom of the given amino acid
            alphaFrame = pdbFrame.loc[\
                        ((pdbFrame['Positional Label'] == 'CA'))]

            peripheralFrame = pdbFrame.loc[\
                        ((pdbFrame['Positional Label'] != 'CA'))]

            for i, row in alphaFrame.iterrows():
                pRow = peripheralFrame.loc[\
                            (peripheralFrame['Residue Number'] \
                             == row['Residue Number'])]

                aminoAcid = pRow['Amino Acid'].iloc[0]
                furthestAtom = AAMidpointDict[aminoAcid]

                pRow = pRow.loc[(pRow['Positional Label'] == furthestAtom)]

                if (pRow.size != 0):
                    if (pRow.size > 1):
                        pRow = pRow.iloc[0]
                    row['X-Coord'] = (float(row['X-Coord']) \
                                     + float(pRow['X-Coord']))/2.0
                    row['Y-Coord'] = (float(row['Y-Coord']) \
                                     + float(pRow['Y-Coord']))/2.0
                    row['Z-Coord'] = (float(row['Z-Coord']) \
                                     + float(pRow['Z-Coord']))/2.0
                    pRow = None

            # Stripping the sequence down to alpha carbons
            if strip:
                pdbFrameList[index] = alphaFrame

                self.logger.info('Removing side chains for ' \
                                 + pdbList[index])
                self.logger.info('Stripping down to alpha carbons for '\
                                 + pdbList[index])
            pdbFrameFiltered = pd.DataFrame(
                columns=list(pdbFrame.columns.values)
            )
            pdbFrameFilteredList[index] = pdbFrameFiltered


        # Figuring out the length of the largest pdb frame so we don't go out
        # of bounds later
        pdbMaxLength = 0
        for pdbFrame in pdbFrameList:
            if len(pdbFrame.index) > pdbMaxLength:
                pdbMaxLength = len(pdbFrame.index)
            
        # Creating a boolean list that denotes which amino acids are common
        # to all PDB files
        commonAminoAcidList = [None]*pdbMaxLength
        for index in range(pdbMaxLength):
            commonAminoAcidList[index] = True
            for pdbFrame in pdbFrameList:
                try:
                    if pdbFrame.iloc[index]['Amino Acid'] \
                        != pdbFrameList[0].iloc[index]['Amino Acid']:
                        commonAminoAcidList[index] = False
                except IndexError:
                    commonAminoAcidList[index] = False


        # Creating a dictionary of chains and residue numbers common
        # between all pdb files
        commonDict = {}

        # Checking to see which chains and their corresponding residue ranges 
        # are common to all pdb files 
        for index, pdbFrame in enumerate(pdbFrameList):
            for chain in sorted(str(i) for i in list(set(pdbFrame['Chain']))):
                chainFrame = pdbFrameList[index].loc[pdbFrameList[index]['Chain']\
                                .str.strip() == chain]

                pdbResidueSet = set([int(x) for x \
                                    in set(chainFrame['Residue Number'])])

                if chain not in commonDict:
                    commonDict[chain] = pdbResidueSet
                else:
                    commonDict[chain] = \
                        commonDict[chain].intersection(pdbResidueSet)

        # Creating a set of all possible chains in the set of pdb files
        commonChains = set()
        for index, pdbFrame in enumerate(pdbFrameList):
            for chain in sorted(str(i) for i in list(set(pdbFrame['Chain']))):
                commonChains.update(chain)
        for index, pdbFrame in enumerate(pdbFrameList):
            commonChains = commonChains.intersection(set(pdbFrame['Chain']))

        # Creating a set of all chains that are not common to all pdb files
        uncommonChains = set(commonDict.keys()).difference(commonChains)

        # Removing uncommon chains from the common chains dictionary
        for chain in uncommonChains:
            commonDict.pop(chain)
            self.logger.info('Chain ' + str(chain) + ' not common')

        # Removing amino acids that do not match
        for index, pdbFrame in enumerate(pdbFrameList):
            self.logger.debug('pdbFrame Length:' + str(len(list(pdbFrame['Chain']))))
            pdbCommon = []
            # Residue numbers are only unique within a given chain so we iterate 
            # through the chains to filter
            for chain in sorted(str(i) for i in list(set(pdbFrame['Chain']))):
                if (chain in commonDict.keys()):
                    chainFrame = pdbFrameList[index].loc[\
                                        pdbFrameList[index]['Chain']\
                                    .str.strip() == chain]

                    # Extracts a set of all possible residues
                    pdbIndexSet = [int(i) for i \
                                   in set(chainFrame['Residue Number'])]

                    # Getting a list of duplicate residues
                    residueCnt = collections.Counter(\
                                    list(chainFrame['Residue Number']))

                    # For duplicate residues, takes the average of the 
                    # Cartesian coordinate values
                    for dupRes in residueCnt.keys():
                        if residueCnt[dupRes] > 1:
                            # Retrieving dataframe of duplicate residue
                            tempFrame = chainFrame.loc[\
                                            chainFrame['Residue Number'] \
                                            == str(dupRes)]
                            firstIndex = tempFrame.index[0]
                            dupIndices = [tempFrame.index[i] for i\
                                          in range(1, len(tempFrame.index))]

                            # Averaging the spatial coordinates
                            averagedRow = tempFrame.iloc[0]
                            averagedRow['X-Coord'] = \
                                    np.average(\
                                        [float(i) for i in \
                                         tempFrame['X-Coord']] \
                                    )
                            averagedRow['Y-Coord'] = \
                                    np.average(\
                                        [float(i) for i in \
                                         tempFrame['Y-Coord']] \
                                    )
                            averagedRow['Z-Coord'] = \
                                    np.average(\
                                        [float(i) for i in \
                                         tempFrame['Z-Coord']] \
                                    )
                            # Of the rows corresponding to the duplicate
                            # residue, we set the first one to the averaged
                            # row and then wipe the rest
                            chainFrame.loc[firstIndex] = averagedRow
                            chainFrame.drop(index=dupIndices, inplace=True)
                            self.logger.debug('dupRes: ' + str(dupRes) \
                                              + '\nFrame: ' + str(tempFrame))


                    pdbCommonBool = pd.Series(
                            sorted(pdbIndexSet)
                        ).isin(commonDict[chain])

                    self.logger.debug('pdbCommonBool Length: ' \
                                      + str(len(pdbCommonBool)))

                    # When rows with duplicate Residue Numbers are found,
                    # take the average of the Cartesian coordinate values
                    # TODO: Set B-Factor t o 1

                    self.logger.debug('chainFrameLoc: ' \
                                    + str(chainFrame.loc[pdbCommonBool.array]))

                    # Adding valid rows into the filtered list
                    pdbFrameFilteredList[index] = pd.concat(
                        [pdbFrameFilteredList[index], 
                        chainFrame.loc[pdbCommonBool.array]]
                    )

        # Adding output path onto names in pdbList
        if outPath is not None:
            for i, pdb in enumerate(pdbList):
                pdbList[i] = os.path.join(outPath, pdb)

        # Printing out the reformatted PDB files
        for index, pdbFrame in enumerate(pdbFrameList):
            if baseList is None:
                pdbr.DataFrameToPDB(pdbList[index], 
                                    pdbFrameFilteredList[index])
            else:
                pdbr.DataFrameToPDB(os.path.join(outPath, baseList[index]),
                                    pdbFrameFilteredList[index])

        # This line is only here for testing
        # After the convertAminoAcidSeq is determined to work
        # higher level analysis must be done to determine where it should be
        # called
        # TODO: Higher level analysis
        # self.convertAminoAcidSeq(pdb1FrameFiltered)


    """ Converts the given DataFrame object to an amino acid sequence
        (Based off of the one letter code)
    """
    def convertAminoAcidSeq(self, pdbFrame):
        
        # Defining a dictionary to translate amino acid 3-letter codes to
        # 1-letter codes
        AADict = { 
            'ALA' : 'A',
            'ARG' : 'R',
            'ASN' : 'N',
            'ASP' : 'D',
            'CYS' : 'C',
            'GLU' : 'E',
            'GLN' : 'Q',
            'GLY' : 'G',
            'HIS' : 'H',
            'ILE' : 'I',
            'LEU' : 'L',
            'LYS' : 'K',
            'MET' : 'M',
            'PHE' : 'F',
            'PRO' : 'P',
            'SER' : 'S',
            'THR' : 'T',
            'TRP' : 'W',
            'TYR' : 'Y',
            'VAL' : 'V',
        }

        # Automatically sorts into order of ASCII values
        aminoAcidQuadString = ''
        for chain in sorted(set(pdbFrame['Chain'])):
            print(list(pdbFrame['Residue Number']))

            # Converting the pdbFrame into a 3-letter code amino acid sequence
            aminoAcidSeq = list(set(zip(pdbFrame['Amino Acid'],\
                                pdbFrame['Residue Number'])))
            aminoAcidSeq.sort(key=lambda tup: tup[1])
            residueSeq, indexSeq = zip(*aminoAcidSeq)
            residueSeq = list(residueSeq)
            residueSeq = [AADict[aminoAcid] for aminoAcid\
                in list(residueSeq)]
            aminoAcidQuadString += \
                ''.join(str(aminoAcid) for aminoAcid in residueSeq)

    
    """ Matches sequences based off of similarities as opposed to index
        (For case where the indices are misaligned)
        Parameters: DataFrame seq1 - Holds the information for pdb1
                    DataFrame seq2 - Holds the information for pdb2
                    int n - Specifies the threshold length of a significant
                            sequence
    """
    #def matchSequences(self, seq1, seq2, n):
        
comparePDB = ComparePDB()
