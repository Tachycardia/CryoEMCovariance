# CryoEMCovariance

The CryoEMCovariance tool is a series of scripts written to facilitate
the calculation and visualization of distance difference matrices and 
covariance matrices of protein residues. It takes in text files in the
[Protein Data Bank](https://www.cgl.ucsf.edu/chimera/docs/UsersGuide/tutorials/pdbintro.html)
(PDB) format, also referred to as "PDB files".

Quickstart/User Manual
======================

To see all available flags and brief descriptions run:

```
./analyzePDB.py --help
```

To compare two pdb files and create plots of the distance difference matrices, 
run:

```
./analyzePDB.py --strip --plot <file1.pdb> <file2.pdb>
```
The ``--plot`` flag creates .png and .html files containing the unscaled
plots of the distance difference matrices.
Note: While there won't be much issue .png files for large plots, the
      .html files will likely get progressively slower to view as the plots grow
      larger

To compare two pdb files and create an interactive plot hosted on a web server,
run:

```
./analyzePDB.py --strip --display <file1.pdb> <file2.pdb>
```

The interactive plot that is generated when the ``--display`` flag is
specified contains individual web elements (called glyphs in the Bokeh API)
for each point on the plot. This is also the case for the plots in the
.html files generated when the ``--plot`` flag is specified. For this reason,
the plots that are generated in this manner will slow down (both in
plot generation and user interactivity) proportionally to the size of the plot.

To remedy this, the user has the option to scale the displayed plot into a
binned version where each point on the plot represents values for a range of 
residue pairs as opposed to just one residue pair. This can be done using the
``--scale`` flag, which takes an integer argument that determines how many
bins there should be in the final plot. For example:

```
./analyzePDB.py --strip --scale 15 --display <file1.pdb> <file2.pdb>
```
would generate a display where all of the residue pairs along the
axes of the plot are binned into 15 bins (for a total of 225 plotted points).
Note: This scale only applies to the plots that are generated for the
display and not the .png/.html plots.

Using Directories
-----------------

When there are many pdb files, it may be convenient to put all of the pdb
files to be processed into a directory. This directory can be specified using
the ``--directory`` flag followed by either the absolute or relative path to
the directory.

```
./analyzePDB.py --strip --plot --directory /path/to/directory/
```

An output directory can also be specified with the ``--outDirectory`` flag
followed by either the absolute or relative path to the directory. If the 
directory does not exist, the script will generate it. If the outDirectory 
specified is an absolute path, the script will take the
path specifically as it is typed. Example of absolute path usage:

```
./analyzePDB.py --strip --plot --directory /path/to/directory/ --outDirectory /path/to/outDirectory/
```

However, if the outDirectory specified is a relative path and there is a
specified directory, then the outDirectory will be treated as if it is
relative to the specified directory. 

If there is not specified directory, but the outDirectory is still specified 
as a relative path then the outDirectory will be treated as if it is relative
to the current working directory (i.e. the directory from which the script
is called).

Using Text Files
----------------

In addition to reading multiple pdb files from a directory, the script
can also read multiple specific files in its working directory. A list of
pdb files to be processed can be written in a text file which
can be specified using the ``--pdbTextList`` followed by the path to said
text file. For example for a text file labeled "TextList.txt":

```
./analyzePDB.py --strip --plot --pdbTextList TextList.txt
```

would tell the script to process each pdb file listed in TextList.txt.
The text file should contain the relative path to each pdb file on a separate 
line. For example, the contents of the text file may look something like:

```
4FKO.pdb
4FKP.pdb
4FKU.pdb
5A14.pdb
5IF1.pdb
```

Choosing a Reference File
-------------------------

Any given distance difference matrix is calculated using two distance matrices,
each generated from its own pdb file. For analyzing multiple pdb files, it is
useful to choose a file from which all other distance matrices will be 
subtracted. This file acts as a reference from which all distance differences
are relative. When running the script directly with only two pdb files, the 
first one that is specified will act as the reference. 

When specifying multiple pdb files through a directory, the script 
will choose one that will be consistent for that one run of the script.
However, it may not be consistent between separate runs of the script.
To remedy this, the reference file can be specified with the
``--reference`` flag followed by the path to the reference file.

Multiprocessing
---------------

The distance matrix calculation is written such that it can be processed
using multiple cores. By default, the script will use the maximum number of
cores that are available. But an arbitrary number can be specified using the
``--processes`` flag followed by the number of separate processes into which the
distance matrix computation is intended to split.

