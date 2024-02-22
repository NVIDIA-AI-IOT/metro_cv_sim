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

import pygame  
from time import sleep

class Visualizer2D_PyGame:
    def __init__(self,state):
        pygame.init()
        pygame.display.set_caption('Simulation Visualization')
        self.screen = pygame.display.set_mode((int(state.width), int(state.height)))
        
        self.cam_color = (255, 174, 0)
        self.roi_color = (0, 132, 255)
        self.process_color = (44, 191, 75, 128)
        self.mover_color = (13, 45, 189)
        self.item_color = (237, 5, 16, 128)

        self(state)

    def __call__(self,state):
        self.screen.fill((255,255,255))

        for _, obj in state.movers.items():
            surface = pygame.Surface((obj.width, obj.height), pygame.SRCALPHA)
            surface.fill(self.mover_color)
            self.screen.blit(surface, (obj.x, obj.y))

        for _, obj in state.processes.items():
            surface = pygame.Surface((obj.width, obj.height), pygame.SRCALPHA)
            surface.fill(self.process_color)
            self.screen.blit(surface, (obj.x, obj.y))

        for _, obj in state.cameras.items():
            pygame.draw.rect(self.screen, self.cam_color, (obj.x,obj.y,obj.width,obj.height), width=4)

        for _, obj in state.rois.items():
            pygame.draw.rect(self.screen, self.roi_color, (obj.x,obj.y,obj.width,obj.height), width=4)

        for obj in state.items:
            surface = pygame.Surface((obj.width, obj.height), pygame.SRCALPHA)
            surface.fill(self.item_color)
            self.screen.blit(surface, (obj.x, obj.y))

        pygame.display.flip()