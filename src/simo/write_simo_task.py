"""
Create a SIMO task from scratch and export as json
"""
import os
from pathlib import Path
from sima import simo
from sima import hydro

from simapy.sima_writer import SIMAWriter

task = simo.SIMOTask(name="test",model=simo.SIMOModel())
body = simo.SIMOBody(name="body",_type=simo.BodyType.THREE_DOF_TIME_DOMAIN)
body.structuralMass = hydro.StructuralMass(mass=100.0)

task.model.bodies.append(body)

file =  Path("output/simo/simo_task.json")
os.makedirs(file.parent,exist_ok=True)
writer = SIMAWriter()
writer.write([task],file,indent=4)


