# CV Metadata Simulator 

The replace_objects.py program can take in an ELK dump from an existing MDX database that detects a 'Person' class and replace all 'Person' detections with user specified objects. 

Example: 

```
python3 replace_objects.py -f mdx-frames-2023-12-12.json -o pallet forklift box -p 0.3 0.2 0.5
```

This will take the mdx-frames...json file and replace all "Person" detections with 'pallet', 'forklift' or 'box' based on the probabilities for each object. The output file will have 30% pallets, 20% forklifts and 50% boxes. The default output file is the the same as the input file with 'replaced_' appended to the beginning. The command above will output to 'replaced_mdx-frames-2023-12-12.json'

By default, the program will look for "Person", a custom list of existing objects can be supplied with the -eo flag. 

* Note: The object list and existing object list need to be disjoint. If they overlap then the program will enter an infinite loop.

## Usage

Minimally supply one input file, the list of objects and probabilities. There must be a probability for each object. 

```
python3 replace_objects.py -f mdx-frames-2023-12-12.json -o pallet forklift box -p 0.3 0.2 0.5
```

You can supply several files as well as a custom list of existing objects and the output file suffix

```
python3 replace_objects.py -f mdx-behavior-2023-12-12.json mdx-tripwire-2023-12-12.json -o pallet forklift -p 0.5 0.5 -eo Person Table -op updated_file
```

The probabilities are relative to each other so they do not have to add up to 1.0. 

```
python3 replace_objects.py -f mdx-frames-2023-12-12.json -o hardhat shelf person -p 50 20 30 -eo pallet forklift box
```


```
usage: MDX Object Replacer [-h] -f FILEPATHS [FILEPATHS ...] -o OBJECTS [OBJECTS ...] -p PROBABILITIES [PROBABILITIES ...] [-eo EXISTING_OBJECTS [EXISTING_OBJECTS ...]]
                           [-op OUTPUT_PREFIX]

Replaces all detected objects with user specified classes in existing MDX ELK dumps.

options:
  -h, --help            show this help message and exit
  -f FILEPATHS [FILEPATHS ...], --filepaths FILEPATHS [FILEPATHS ...]
                        Filepaths to ELK dump with MDX data. Accepts multiple files.
  -o OBJECTS [OBJECTS ...], --objects OBJECTS [OBJECTS ...]
                        List of objects to be added to the ELK dump
  -p PROBABILITIES [PROBABILITIES ...], --probabilities PROBABILITIES [PROBABILITIES ...]
                        List of probablities for each object to be added the ELK dump
  -eo EXISTING_OBJECTS [EXISTING_OBJECTS ...], --existing_objects EXISTING_OBJECTS [EXISTING_OBJECTS ...]
                        List of existing object types in the ELK dump.
  -op OUTPUT_PREFIX, --output_prefix OUTPUT_PREFIX
                        Add an output_prefix to append to filenames for the output.
```