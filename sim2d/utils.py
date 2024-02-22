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

from .scene2D import State2D, Object2D, Process, Mover, Camera, ROI
import xml.etree.ElementTree as ET 
import yaml 

def _parse_yaml(yaml_file):
    """Parse YAML file to get mover and process information"""
    with open(yaml_file, 'r') as f:
        data = yaml.full_load(f) #todo convert to all lower case 

    return data["movers"], data["processes"]

def _parse_xml(xml):
    """Parse XML and to extract all mxCells"""
    tree = ET.parse(xml)
    root = tree.getroot()

    #store all mxCell objects by ID - mxCell are all the objects in the diagram 
    mxCells = dict()
    for item in root.findall("./diagram/mxGraphModel/root/"):
        id = item.get("id")
        mxCells[id] = item

    return mxCells 

def _parse_xml_size(xml):
    """Parse XML to get height and width of diagram"""
    tree = ET.parse(xml)
    root = tree.getroot()
    width = float(root.find("./diagram/mxGraphModel").get("dx"))
    height = float(root.find("./diagram/mxGraphModel").get("dy"))
    return width, height

def _categorize_mxcells(mxcells):
    """Categorize mxcells and movers, processes, cameras or rois"""

    cat_cells = {"movers":[], "processes":[], "cameras":[], "rois":[]}
    process_ids = set()

    #Determine all mxCells that are edges
    for id, xml in mxcells.items():
        if "source" in xml.keys() and "target" in xml.keys(): #if true then its a mover (edge)
            cat_cells["movers"].append(xml)
            process_ids.add(xml.get("source"))
            process_ids.add(xml.get("target"))

    #Determine all mxCells that are processes 
    for id, xml in mxcells.items():
        if id in process_ids:
            cat_cells["processes"].append(xml)
        elif "value" in xml.keys():
            name = xml.get("value").lower()
            if "camera:" == name[0:7]:
                cat_cells["cameras"].append(xml)
            elif "roi:" == name[0:4]:
                cat_cells["rois"].append(xml)

    return cat_cells 

def state_from_files(xml, yaml):
    """Parse drawio XML and YAML file to build scene2D"""
    check_xml(xml)
    check_yaml(yaml)

    mx_cells = _parse_xml(xml)
    width, height = _parse_xml_size(xml)
    cat_cells = _categorize_mxcells(mx_cells)

    movers_yaml, processes_yaml = _parse_yaml(yaml)
  
    """Convert XML and YAML definitions to 2D Objects """
    movers = {}
    processes = {}
    cameras = {}
    rois = {}
   
    for process_xml in cat_cells["processes"]:
       id = process_xml.get("id")
       processes[id] = Process.from_xml(process_xml, processes_yaml)

    for camera_xml in cat_cells["cameras"]:
        id = camera_xml.get("id")
        cameras[id] = Camera.from_xml(camera_xml)

    for roi_xml in cat_cells["rois"]:
        id = roi_xml.get("id")
        parent_camera = roi_xml.get("parent")
        rois[id] = ROI.from_xml(roi_xml, cameras[parent_camera])
        cameras[parent_camera].rois.append(rois[id])
        
    for mover_xml in cat_cells["movers"]:
        source_id = mover_xml.get("source")
        target_id = mover_xml.get("target")
        id = mover_xml.get("id")
        movers[id] = Mover.from_xml(mover_xml, movers_yaml, processes[source_id], processes[target_id])

    state = State2D(processes=processes, movers=movers, rois=rois, cameras=cameras, items={}, height=height, width=width)
    return state
            

def yaml_from_xml(xml_path, yaml_path):
    """Make a template YAML file based on the drawio XML"""
    check_xml(xml_path)

    mx_cells = _parse_xml(xml_path)
    cat_cells = _categorize_mxcells(mx_cells)

    with open(yaml_path, "w+") as file:
        file.write("processes:\n")
        for process in cat_cells["processes"]:
            file.write(f"  {process.get('value')}:\n    input:\n    output:\n    time:\n\n")

        file.write("movers:\n")    
        movers_written = set()
        for mover in cat_cells["movers"]:
            if mover.get("value") not in movers_written:
                file.write(f"  {mover.get('value')}:\n    speed:\n    capacity:\n\n")
                movers_written.add(mover.get("value"))

    return yaml_path

def check_xml(xml):
    """Check XML for issues before building a scene. Raise exceptions"""

    tree = ET.parse(xml)
    root = tree.getroot()

    print(f"Checking drawio xml file {xml}")

    #store all mxCell objects by ID - mxCell are all the objects in the diagram 
    mxCells = dict()
    for item in root.findall("./diagram/mxGraphModel/root/"):
    
        if "edge" in item.keys(): #arrow/mover
            if item.get("value") == "":
                raise Exception(f"An arrow in the diagram is not labelled. Ensure all arrows are labelled with the mover type.")


            if "source" not in item.keys():
                raise Exception(f"An arrow in the diagram has no input connection. Ensure the arrow is connected to a process on both ends.")
            
            if "target" not in item.keys():
                raise Exception(f"An arrow in the diagram has no output connection. Ensure the arrow is connected to a process on both ends.")
            
        #Rest are processes, cameras or rois 
        if item.get("value") == "":
            raise Exception(f"A component in the diagram is not labelled. Ensure all components are labelled.")
        
        component_style = item.get("style", "").split(";")
        if "swimlane" in component_style: #container that should be a camera or ROI 
            name = item.get("value").lower()
            if not("camera:" == name[0:7] or "roi:" == name[0:4]):
                raise Exception(f"A container component's lablel does not start with 'camera:' or 'roi:'. Ensure all container components are labelled starting with 'camera:' or 'roi:'")
    print(f"Drawio xml file verified")           
    
def check_yaml(yaml_path):
    """Check yaml for issues before building a scene. Raise exceptions"""
    print(f"Checking yaml file {yaml_path}")
    with open(yaml_path, 'r') as f:
        yaml_data = yaml.full_load(f) #todo convert to all lower case 

        #Verify processes, movers
        if set(yaml_data.keys()) != set(["processes", "movers"]):
            raise Exception(f"YAML file has {list(yaml_data.keys())} top level keys but requires ['processes', 'movers'] as top level keys")
        
        #Verify time, inputs, outputs for each process 
        for process_name, process_data in yaml_data["processes"].items():
            keys = set(process_data.keys())
            if "time" not in keys or ("input" not in keys and "output" not in keys):
                raise Exception(f"{process_name} keys are {list(keys)} but requires ['time', 'input', 'output']. Either 'input' or 'output' can be omitted but not both.")

            #Verify inputs 
            if "input" in keys:
                if process_data["input"] is None:
                    raise Exception(f"The {process_name} process has an 'input' key but no inputs are listed.")
        
            #Verify outputs 
            if "output" in keys:
                if process_data["output"] is None:
                    raise Exception(f"The {process_name} process has an 'output' key but an output is not listed.")
                if len(process_data["output"]) > 1:
                    raise Exception(f"The {process_name} process has too many items listed under the 'output' key. Only 1 item output is supported.")
        
        #Verify movers
        for mover_name, mover_data in yaml_data["movers"].items():
            keys = set(mover_data.keys())
            if keys != set(["speed", "capacity"]):
                raise Exception(f"The {mover_name} mover keys are {list(keys)} but requires ['speed', 'capacity'].")
            
    print("Yaml file verified")

if __name__ == "__main__":

    #_parse_yaml("test.yaml")
    state_from_files("test.drawio", "test.yaml")
