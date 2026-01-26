# HammingDistanceCalculator

![test](https://github.com/UMCUGenetics/python_template/actions/workflows/test.yml/badge.svg)
![lint](https://github.com/UMCUGenetics/python_template/actions/workflows/lint.yml/badge.svg)

HammingDistanceCalculator is a script to calculate the hamming distance for a set of barcodes of the same length.
The script currently only allows for input DNA of letters 'A', 'C', 'T', and 'G'.

This script expects a list as input in the format:

```
Label,Barcode
read_name_1,ACTG
read_name_2,GTTG
read_name_3,ACCT
read_name_4,ACTG
...
```
which you can create or extend as long as you like. 

# Run help command:
``` 
uv run src/hammingdistancecalculator/hamming_distance.py --help
```

# Run example

```
# by default writes hamming distances 0 and 1:
uv run src/hammingdistancecalculator/hamming_distance.py src/input_files/example_barcodes.csv

# you can also specify the max hamming distance you want to see
# it will then create a hamming distance txt file for all distances until the max (for max 3 created 0, 1, 2, 3)
uv run src/hammingdistancecalculator/hamming_distance.py src/input_files/example_barcodes.csv --max-distance 3
```

# Expected output
Two files should be generated if no --max-distance is provided:
```commandline
hamming_distance_0.txt
hamming_distance_1.txt
```

Each of these files contains all barcodes with said hamming distance.


# Progress bar
Due to the nature of the comparisons (n*n), calculation times can be quite long.
Because of this, I make use of the TQDM module, to show a progress bar indicating in both % and absolute numbers the progress while calculating
