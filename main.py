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

from sim2d.simulator2D import Simulator2D
from sim2d.scene2D import *
from sim2d.utils import state_from_files, yaml_from_xml
from time import sleep 
import datetime
import argparse
from pathlib import Path 
import os 

# Create the parser
parser = argparse.ArgumentParser(description='Command Line Argument Parser for Simulation')

# Add the -d flag for a required draw.io diagram file input
parser.add_argument('-d', "--diagram_path", required=True, type=str, help='Path to the draw.io diagram file (.xml or .drawio)')

# Add the -v flag for an optional YAML configuration file input
parser.add_argument('-y', "--yaml_path", required=False, type=str, help='Path to the configuration YAML file. If not supplied, then a template yaml file will be generated based on the input diagram file.')

# Add the -t flag for specifying simulation time steps with default value
parser.add_argument('-t', "--time", required=False, type=int, default=60, help='Number of minutes to generate synethic data for')

# Add the -v and -a flags for enabling/disabling visualizer and analytics
parser.add_argument('-v', "--visualizer", required=False, action="store_true", help='Enable the visualizer')
parser.add_argument('-a', "--analytics", required=False, action="store_true", help="Enable the analytics output")

args = parser.parse_args()
print(args)

#Collect arguments
diagram_path = args.diagram_path #path to drawio diagram
yaml_path = args.yaml_path #path to yaml config file 
timesteps = args.time * 60 #convert to seconds. Number of timesteps to generate data. 1 timestep = 1 second. 
enable_visualizer = args.visualizer
enable_anlytics = args.analytics

#If yaml not provided, output template yaml
if not yaml_path:
    print("No YAML file provided.")
    print("Generating a template YAML file.")
    
    yaml_path = Path(diagram_path).with_suffix(".yaml")
    if yaml_path.is_file():
        print(f"File named {yaml_path} already exists. Would you like to overwrite this file?")
        choice = input("Would you like to overwrite the file (y/n):")
        if choice.lower() not in ["y", "yes"]:
            print("Did not generate template.")
            exit()  
    yaml_from_xml(diagram_path, yaml_path)
    print(f"Created template yaml at {yaml_path}. Fill out the template, add it as a cmd line argument and run again.")
    exit() 

#Load starting state
starting_state = state_from_files(diagram_path, yaml_path)

#Adjust start time so the end of the simulation will be the current time when the script is run 
start_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=timesteps)

#Instantiate simulation compoenents 
sim = Simulator2D(starting_state) #simulator: moves objects and handle item production 

if enable_visualizer:
    from sim2d.visualizer2D import Visualizer2D_PyGame
    vis = Visualizer2D_PyGame(starting_state) #visualizer: creates visualization of the simualtor (optional)

if enable_anlytics:
    from sim2d.analytics2D import Analytics2D
    analyze = Analytics2D("mdx_elk.json", timestamp=start_time) #analytics: generates detection data as an ELK dump

for i in range(timesteps):
    new_state = sim.timestep() #step simulator 
    if enable_anlytics:
        analyze(new_state, i) #generate analytics and write out ELK dump 
    if enable_visualizer:
        vis(new_state) #visualize a simulator state 
    #sleep(0.01)

    if i % 60 == 0:
        print(f"{i//60} minutes have been generated")