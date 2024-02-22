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

from dataclasses import dataclass 
import yaml
import xml.etree.ElementTree as ET 
import random 
import math 
from collections import Counter 
from random import randint, uniform
import uuid 

class Inventory:
    """Class that holds a collection of Object2D items. Provides methods to easily add an subtract items"""

    def __init__(self, capacity=-1):
        #TODO implement capacity
        self.items = {} #store items by type
        self.capacity = capacity 
    @property 
    def size(self):
        size = 0
        for v in self.items.values():
            size+=len(v)
        return size 

    def available_items(self):
        available_items = {}
        for item_type, item_list in self.items.items():
            available_items[item_type] = len(item_list)
        return available_items

    def check_available(self, items):
        """Check if item list is available"""
        for item_type, item_num in items.items():

            #Check if items are available
            item_list = self.items.get(item_type, [])
            if len(item_list) < item_num:
                return False 

        return True 


    def put(self, items):
        """Put items into inventory
        
        input
        items Dict: {"item_type":[items]}
        
        """
        for item_type, item_list in items.items():
            if item_type in self.items:
                self.items[item_type].extend(item_list)
            else:
                self.items[item_type] = item_list 
    
    def get(self, items):
        """Try to returns available items
        
        input
        
        items Dict: {"item_type":num}
        
        """
        ret_items = {}
        for item_type, item_num in items.items():

            if item_type not in self.items:
                self.items[item_type] = []

            #calc num items to move
            available = len(self.items[item_type])
            to_return = min(available, item_num)

            #move items 
            ret_items[item_type] = self.items[item_type][:to_return]
            del self.items[item_type][:to_return]

        return ret_items


class Object2D:
    '''Everything is a rectangle for simplicity.'''
    def __init__(self, type, gid, x, y, width, height):
        self.type=type
        self.gid = gid #global id for tracking ?

        #position
        self.x = float(x)
        self.y = float(y)

        #size
        self.width = float(width)
        self.height = float(height) 

        #velocity 
        self.dx = 0
        self.dy = 0

        self.registered_move= self._default_move
        self.registered_info = self._default_info

    @property
    def center(self):
        return (self.x + self.width / 2, self.y+self.height/2)

    @property
    def bbox(self):
        return (self.x, self.y, self.x + self.width, self.y + self.height)
    
    def __contains__(self, object2d):
        """if object2d centroid in this objects region return true else false """
        center_x, center_y = object2d.center 
        x1, y1, x2, y2 = self.bbox 
        if center_x >= x1 and center_x <= x2 and center_y >= y1 and center_y <= y2:
            return True 
        return False 

    def move(self, goto_x, goto_y):
        self.registered_move(goto_x, goto_y)

    def info(self):
        return self.registered_info()

    def _default_move(self, goto_x, goto_y):
        """ Move the object """
        self.x += self.dx
        self.y += self.dy 

        # #Check bounds
        # self.x = max(0, self.x)
        # self.y = max(0, self.y)
        # self.x = min(max_x, self.x)
        # self.y = min(max_y, max_y)

        #Add velocity 
        self.dx = random.uniform(-5,5)
        self.dx = random.uniform(-5,5)

    def _default_info(self):
        """ Log data for the object like sensor values """

        return {"sensor1":1}
    
class Process(Object2D):
    def __init__(self, type, gid, x, y, width, height, time, inputs=None, outputs=None):
        super().__init__(type, gid, x, y, width, height)
        
        self.required_inputs = Counter(inputs)
        self.required_outputs = Counter(outputs)
        
        self.inventory = Inventory()

        self.required_time = time
        self.current_time = self.required_time

        self.state = 0 #0,1

    @classmethod
    def from_xml(cls, xml, yaml):
        geo =  xml.find("mxGeometry")
        x = geo.get("x", 0)
        y = geo.get("y", 0)
        width = geo.get("width")
        height = geo.get("height")
        type = xml.get("value")
        id =xml.get("id")

        #Get I/O from yaml 
        yaml = yaml[type]
        time = yaml["time"]
        inputs = yaml.get("input", None)
        outputs = yaml.get("output", None)


        return cls(type, id, x ,y , width, height, time, inputs=inputs, outputs=outputs)


    def put(self, items): #TODO could implement a size limit for process inventory 
        """Return True if process accepted items otherwise false

            TODO - If capacity is implemented, should return items that could not be put. 
        
        """
        
        self.inventory.put(items)
        return True 
         

    def get(self, items): #TODO Update to take in a counter to generalize 
        """Removed specified number of items from output inventory"""
        return self.inventory.get(items)

    def __call__(self):
        

        if self.state == 0: #wait for enough inputs 

            if self.inventory.check_available(self.required_inputs):
                #If we have all the inputs then produce the outputs 
                used_items = self.inventory.get(self.required_inputs) #consume inputs 
                Item.set_used(used_items)
                self.state = 1 #go to output state 

        elif self.state == 1: #process inputs for some time then make outputs 
            if self.current_time > 0:
                self.current_time -=1
            else:
                self.state = 0
                self.current_time = self.required_time 

                #Create output items 
                output_items = Item.items_from_dict(self.required_outputs, self)
                self.inventory.put(output_items)

        else:
            return 
        
class Mover(Object2D):
    def __init__(self, type, gid, source_x, source_y, width, height, capacity, speed, source, target):
        super().__init__(type, gid, source_x, source_y, width, height)
        self.capacity = capacity
        self.speed = speed 

        #home
        self.source_x = source_x
        self.source_y = source_y

        #source and target processes 
        self.source_p = source 
        self.target_p = target

        self.registered_move = self.travel

        #State machine info 
        self.state = 0 #0,1,2,3

        self.inventory = Inventory()
    def rotate_vector(self, dx, dy, angle):
        """Rotate a 2D vector by a given angle."""
        radians = math.radians(angle)
        rotated_dx = dx * math.cos(radians) - dy * math.sin(radians)
        rotated_dy = dx * math.sin(radians) + dy * math.cos(radians)
        return rotated_dx, rotated_dy

    def travel(self, goto_x, goto_y):
        """Updates the direction towards the target ROI."""

        #calculate direction vector and normalize  
        dx, dy = goto_x - self.x, goto_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        dx = (dx/distance)  
        dy = (dy/distance)

        #Apply random rotation to get variable movement 
        rotation_angle = random.uniform(-90, 90)
        dx, dy = self.rotate_vector(dx, dy, rotation_angle)
        
        #Apply speed
        self.dx = dx * self.speed 
        self.dy = dy * self.speed 

        #Move object 
        self.x += self.dx
        self.y += self.dy 

    @classmethod
    def from_xml(cls, xml, yaml, source, target):
        x, y = source.center

        width = 10
        height = 10

        type = xml.get('value')
        id = xml.get("id")

        speed = yaml[type]["speed"]
        capacity = yaml[type]["capacity"]

        return cls(type, id, x, y, width, height, capacity, speed, source, target)

    def __call__(self):
        if self.state == 0: #pick up items until inventory is full 
            item_type = list(self.source_p.required_outputs.keys())[0] #get item type to move 
            got_items = self.source_p.get({item_type:self.capacity})
            Item.set_parent(got_items, self)
            self.inventory.put(got_items) #TODO fix - this will make the mover have more items that capacity in some cases 
            if self.inventory.size >= self.capacity:
                self.state = 1

        elif self.state == 1: #move to target process 
            self.move(*self.target_p.center)
            if self in self.target_p:
                self.state = 2

        elif self.state == 2: #drop items until inventory is empty 
            got_items = self.inventory.get(self.inventory.available_items())
            Item.set_parent(got_items, self.target_p)
            self.target_p.put(got_items)
            if self.inventory.size == 0:
                self.state = 3

        elif self.state == 3: #move to source process 
            self.move(*self.source_p.center)
            if self in self.source_p:
                self.state = 0

        else:
            return 

    def __str__(self):
        return f"{self.speed=}, {self.type=}"

class Item(Object2D):

    item_tracker = []

    def __init__(self, type, gid, x, y, width, height, parent):
        super().__init__(type, gid, x, y, width, height)
        self.update_parent(parent)
        self.used = False #Set to true if the item needs to be deleted from simulation  
        Item.item_tracker.append(self)

    @staticmethod
    def set_parent(items, parent):
        for item_type, item_list in items.items():
            for item in item_list:
                item.update_parent(parent)

    @staticmethod
    def set_used(items):
        for item_type, item_list in items.items():
            for item in item_list:
                item.used = True 

    @staticmethod
    def remove():
        Item.item_tracker = [item for item in Item.item_tracker if item.used == False]

    @classmethod
    def items_from_dict(cls, items, parent):
        
        ret_items = {}
        for item_type, num in items.items():
            item_list = [cls(item_type, "-1", -1, -1, 5, 5, parent) for x in range(num)]
            ret_items[item_type] = item_list 

        return ret_items

    def update_parent(self, parent):
        self.parent = parent
        self._update_local_pos()
    
    def _update_local_pos(self):
        #Place item randomly inside the parent 
        self.local_x = uniform(0, self.parent.width) 
        self.local_y = uniform(0, self.parent.height)

        #update global x,y based on parent's postition 
        self.x = self.local_x + self.parent.x
        self.y = self.local_y + self.parent.y

    def __call__(self):
        #update global x,y based on parent's postition 
        self.x = self.local_x + self.parent.x
        self.y = self.local_y + self.parent.y 


class Camera(Object2D):
    def __init__(self, type, gid, x, y, width, height):
        super().__init__(type, gid, x, y, width, height)
        self.rois = []
        self.detections = []

    @property
    def detections_sorted(self):
        sorted_detections = {}
        for object in self.detections:
            if object.type in sorted_detections:
                sorted_detections[object.type].append(object)
            else:
                sorted_detections[object.type] = [object]

        return sorted_detections
 
    def __call__(self, objects):
        self.detections = []
        for obj in objects:
            if obj in self:
                self.detections.append(obj)
                #print(f"Camera: {self.gid} detected object: {obj.type}")
        return self.detections


    @classmethod
    def from_xml(cls, xml):
        geo = xml.find("mxGeometry")
        x = geo.get("x", 0)
        y = geo.get("y", 0)
        width = geo.get("width")
        height = geo.get("height")
        type = xml.get("value").split(":")[1]
        id = xml.get("id")

        return cls(type, id, x ,y , width, height)

class ROI(Object2D):
    def __init__(self, type, gid, x, y, width, height, parent):
        super().__init__(type, gid, x, y, width, height)
        self.parent = parent #parent camera
        self.detections = []

    
    @property
    def detections_sorted(self):
        sorted_detections = {}
        for object in self.detections:
            if object.type in sorted_detections:
                sorted_detections[object.type].append(object)
            else:
                sorted_detections[object.type] = [object]

        return sorted_detections


    def __call__(self, objects):
        self.detections = []
        for obj in objects:
            if obj in self:
                self.detections.append(obj)
                #print(f"Object: {obj.type} entered ROI: {self.gid}")
        return self.detections 

    @classmethod
    def from_xml(cls, xml, parent):
        """Create ROI Object from XML section"""
        geo = xml.find("mxGeometry")
        x = float(geo.get("x", 0))
        y = float(geo.get("y", 0))
        width = float(geo.get("width"))
        height = float(geo.get("height"))
        type = xml.get("value").split(":")[1]
        id = xml.get("id")

        x = x + parent.x
        y = y + parent.y
        return cls(type, id, x, y, width, height, parent)


@dataclass 
class State2D:
    """
    State of simulator 
    Should hold position of all objects 
    Animator should be able to take in this state and produce visualization 
    """
    processes: dict[str, Object2D]
    movers: dict[str, Object2D]
    rois: dict[str, Object2D]
    cameras: dict[str, Object2D]
    items: list[Object2D]
    height: float 
    width: float 