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

from typing import Union 
from pydantic import BaseModel, Field 

class bbox_pyd(BaseModel):
    leftX: float 
    bottomY: float
    topY: float 
    rightX: float 

class object_pyd(BaseModel):
    bbox: bbox_pyd
    id: str
    type: str
    confidence: float = 1.0
    dir: list = []
    embedding: float = None
    pose: float = None
    lipActivity: str = None 
    speed: float = 0
    info: dict = {}
    coordinate: str = None
    gaze: str = None
    location: str = None 

class mdx_raw_pyd(BaseModel):
    timestamp: str
    id: str
    sensorId: str 
    objects: list[object_pyd]
    type: str = "mdx-raw"
    version: str = "4.0"

class coordinates_pyd(BaseModel):
    x: float
    y: float
    z: float 

class fov_pyd(BaseModel):
    id: str 
    coordinates: list[coordinates_pyd]
    count: int 
    ids: list
    type: str 

class roi_pyd(BaseModel):
    id: str
    coordinates: list[coordinates_pyd]
    count: int
    ids: list[str]
    type: str 

class mdx_frames_pyd(BaseModel):
    timestamp: str
    fov: list[fov_pyd]
    rois: list[roi_pyd]
    version: str = "4.0"
    sensorId: str
    objects: list = []
    id: str
    info: dict 
    type: str = "mdx-frames"


class elk_index_pyd(BaseModel):
    index: str = Field(serialization_alias="_index")
    type: str = Field("logs", serialization_alias="_type")
    id: str = Field(serialization_alias="_id")
    score: int = Field(1, serialization_alias="_score")
    source: Union[mdx_raw_pyd, mdx_frames_pyd] = Field(serialization_alias="_source")

    class Config:
        fields = {'index': '_index', 'type':"_type", 'id':"_id", 'score':"_score", "source":"_source"}