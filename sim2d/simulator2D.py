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

from itertools import chain
from .scene2D import Item 

class Simulator2D:
    
    def __init__(self, state):
        self.state = state 

    def add_object(self, object):
        self.objects.append(object)

    def timestep(self):

        #handle movers
        for id, mover in self.state.movers.items():
            mover()
            #print(mover.info())

        #handle processes 
        for id, process in self.state.processes.items():
            process()

        Item.remove() #cleanup used items 
        self.state.items = Item.item_tracker #Update item list

        #Update item positions
        for item in self.state.items:
            item() 

        #handle camera detections
        for id, camera in self.state.cameras.items():
            objs = list(chain(self.state.movers.values(), self.state.items))
            camera(objs)
            
        #handle rois detections 
        for id, roi in self.state.rois.items():
            objs = list(chain(self.state.movers.values(), self.state.items))
            roi(objs)


        return self.state 

    def register_movement(self, function, type):
        for obj in self.objects:
            if obj.type==type:
                obj.move_func=function 
    def register_info(self, function, type):
        for obj in self.objects:
            if obj.type==type:
                obj.info_func=function 