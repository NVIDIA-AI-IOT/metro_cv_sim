# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import argparse
from pathlib import Path
from tqdm import tqdm
import os 
import random
import json 


def prefix_filename(path, prefix):
    path = Path(path)
    return f"{prefix}_{path.name}"


def replace_objects(filepath, objects, probs, existing_objects, output_prefix="replaced"):
    
    file_size = os.path.getsize(filepath)
    print(f"File Size: {file_size} bytes")
    with tqdm(total=file_size) as pbar: #progress bar based on processed bytes
        input_file = open(filepath, "r")
        output_file = open(prefix_filename(filepath, output_prefix), "w+")
        for line in input_file:
            line_size = len(line)
            #json.loads(line) #loading json adds 2.6x overhead 5GB = 40s without json, 5GB = 105s w/json 
            
            #Replace objects 
            for eo in existing_objects: #objects and existing_objects must be disjoint otherwise will loop forever 
                while eo in line:
                    new_object = random.choices(objects, weights=probs, k=1)[0] #get random objects weights on probability 
                    #print(f"Replacing line: {line}")
                    line = line.replace(eo, new_object, 1)
                    #print(f"New line: {line}")

            output_file.write(line)
            pbar.update(line_size)

        input_file.close()
        output_file.close()

if __name__ == "__main__":
    """
    Example Usage:
    python3 replace_objects.py -f mdx-frames-2023-12-12.json -o pallet forklift box -p 0.3 0.2 0.5
    python3 replace_objects.py -f mdx-behavior-2023-12-12.json mdx-tripwire-2023-12-12.json -o pallet forklift -p 0.5 0.5 -eo Person -op updated
    python3 replace_objects.py -f mdx-frames-2023-12-12.json -o hardhat shelf person -p 50 20 30 -eo pallet forklift box -ov
    """
    parser = argparse.ArgumentParser(prog="MDX Object Replacer", description="Replaces all detected objects with user specified classes in existing MDX ELK dumps.")
    parser.add_argument("-f", "--filepaths", nargs= '+', help="Filepaths to ELK dump with MDX data. Accepts multiple files.", required=True)
    parser.add_argument("-o", "--objects", nargs='+', help="List of objects to be added to the ELK dump", required=True)
    parser.add_argument("-p", "--probabilities", nargs='+', type=float, help="List of probablities for each object to be added the ELK dump", required=True)
    parser.add_argument("-eo", "--existing_objects", nargs='+', type=str, default=["Person"], help="List of existing object types in the ELK dump.")
    parser.add_argument("-op", "--output_prefix", default="replaced", help="Add an output_prefix to append to filenames for the output.")

    args = parser.parse_args()
    print(args)

    for file in args.filepaths:
        replace_objects(file, args.objects, args.probabilities, args.existing_objects, args.output_prefix)
        print(f"Wrote new file {prefix_filename(file, args.output_prefix)} with objects {args.objects}")
       




 