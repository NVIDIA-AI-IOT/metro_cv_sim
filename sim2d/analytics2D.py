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

import datetime 
import uuid 
from .mdx_schema import *

class Analytics2D:

    """Generates detection metadata in ELK Dump format that is compatible with MDX APIs"""

    def __init__(self, output_file, timestamp=datetime.datetime.utcnow(), place="city=Austin/building=Office/room=Cafeteria"):

        self.frame_count = 0
        self.index_file = output_file
        self.timestamp = timestamp
        self.place = place

        with open(self.index_file, "w+") as file:
            pass 
    
    @property
    def timestamp_formatted(self):
        """Format timestamp as defined by mdx schema"""
    
        return self.timestamp.isoformat("T")[0:-3] + "Z" #take out last 3 digits of seconds

    def _inc_timestamp(self, n):
        """Increment timestamp by n seconds"""
        self.timestamp = self.timestamp + datetime.timedelta(seconds=n)

    def _make_mdx_frames(self, state):
        """Write out mdx-frame index based on passed in state"""
        with open(self.index_file, "a") as index_file:

            #Each camera outputs 1 mdx_frame line to the file 
            for camera_id, camera in state.cameras.items():
                
                #Create fov field - summarizes detected objects and counts 

                #make a fov object for each object type
                fov_list = []
                for type, objects in camera.detections_sorted.items():
                    fov_list.append(fov_pyd(id="", coordinates=[], count=len(objects), ids=[], type=type))


                #Create ROI field
                roi_list = []
                for roi in camera.rois:
                    
                    #One roi_pyd for each object type 
                    for obj_type, obj_list in roi.detections_sorted.items():
                        count = len(obj_list)
                        ids = [x.gid for x in obj_list]
                        coords_list = []
                        for obj in obj_list:
                            coords = coordinates_pyd(z=0, x=obj.x, y=obj.y) #Not sure if this should be relative to ROI or global coordinate system 
                            coords_list.append(coords)

                        roi_list.append(roi_pyd(id=roi.type, coordinates=coords_list, count=count, ids=ids, type=obj_type))

                frame_info = {"place": self.place}
                mdx_frame = mdx_frames_pyd(timestamp=self.timestamp_formatted, fov=fov_list, rois=roi_list, sensorId=camera.type, id=str(self.frame_count), info=frame_info)

                elk_index = elk_index_pyd(index=f"mdx-frames-{self.timestamp_formatted[:10]}", id=str(uuid.uuid1()), source=mdx_frame)
                elk_index_json = elk_index.model_dump_json(by_alias=True)
                index_file.write(elk_index_json)
                index_file.write("\n")
        

    def _make_raw_index(self,state):
        """Write out mdx-raw index based on passed in state"""
        with open(self.index_file, "a") as index_file:

            for _, camera in state.cameras.items():
                
                objects = []
                for obj in camera.detections:
                    box = bbox_pyd(leftX=0, bottomY=0, topY=100, rightX=100)
                    mdx_obj = object_pyd(bbox=box, id=obj.gid, type=obj.type)
                    objects.append(mdx_obj)

                raw = mdx_raw_pyd(timestamp=self.timestamp_formatted, id=str(self.frame_count), sensorId=camera.type, objects=objects)
             
                elk_raw = elk_index_pyd(index=f"mdx-raw-{self.timestamp_formatted[:10]}", id=str(uuid.uuid1()), source=raw)
                elk_json = elk_raw.model_dump_json(by_alias=True)
                index_file.write(elk_json)
                index_file.write("\n")

    def __call__(self, state, timestep):
        self.frame_count = timestep 
        self._inc_timestamp(1)

        self._make_raw_index(state)
        self._make_mdx_frames(state)

        #TODO add trip wire and behavior output