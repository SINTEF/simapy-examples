"""
Import a json file exported from SIMA using the Simple Flexible Riser Example.
Then use parts of the model as a template to create new models.
Last export to a json file so this can be imported into SIMA
"""

import os
from pathlib import Path
from random import random
from simapy.sima_reader import SIMAReader
from sima.riflex.riflextask import RIFLEXTask
from sima.riflex.supernode import SuperNode
from simapy.sima_writer import SIMAWriter

def __copy_and_move(sn: SuperNode, offset):
    """Copy node and move the copy with the given offset"""
    sn_copy = sn.copy()
    sn_copy.xGInitial = sn_copy.xGInitial+ offset
    sn_copy.yGInitial = sn_copy.yGInitial+ offset
    sn_copy.xGStatic = sn_copy.xGStatic+ offset
    sn_copy.yGStatic = sn_copy.yGStatic+ offset
    return sn_copy

reader = SIMAReader()
contents = reader.read("input/riflex/simple_flexible_riser.json")
# Using type hints is not necessary but is useful to get automatic help when using an IDE, such as vscode or pycharm
task: RIFLEXTask = contents[0]
# We will use the first line as a template to generate new ones
model = task.model
lines = model.slenderSystem.lines
nodes = model.slenderSystem.superNodes
line = lines[0]

for name in ["line_1","line_2","line_3"]:
    line_i = line.copy()
    line_i.name = name
    # create two new nodes and move to random position
    offset = 300.0*random()

    sn_end_1: SuperNode = __copy_and_move(line_i.end1,offset)
    sn_end_1.name = name + "_end1"
    line_i.end1 = sn_end_1
    nodes.append(sn_end_1)

    sn_end_2: SuperNode = __copy_and_move(line_i.end2,offset)
    sn_end_2.name = name + "_end2"
    line_i.end2 = sn_end_2
    nodes.append(sn_end_2)
    
    lines.append(line_i)

file =  Path("output/riflex/simple_flexible_riser_mod.json")
os.makedirs(file.parent,exist_ok=True)
writer = SIMAWriter()
writer.write([task],file)
