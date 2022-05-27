"""
Create a SIMO task from scratch and export as json
"""
import os
from pathlib import Path
from sima.simo.simotask import SIMOTask
from sima.simo.simomodel import SIMOModel
from sima.simo.simobody import SIMOBody
from sima.simo.bodytype import BodyType
from sima.hydro.structuralmass import StructuralMass

from simapy.sima_writer import SIMAWriter

task = SIMOTask(name="test",model=SIMOModel())
body = SIMOBody(name="body",_type=BodyType.THREE_DOF_TIME_DOMAIN)
body.structuralMass = StructuralMass(mass=100.0)

task.model.bodies.append(body)

file =  Path("output/simo/simo_task.json")
os.makedirs(file.parent,exist_ok=True)
writer = SIMAWriter()
writer.write([task],file,indent=4)


