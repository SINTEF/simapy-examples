"""
Generate a workflow then run it with input using SIMA
"""
import os
import shutil
from pathlib import Path
from simapy.sima import SIMA
from simapy.sima_reader import SIMAReader
from marmo.containers.container import Container
from marmo.containers.dimensionalscalar import DimensionalScalar

from generate_workflow import generate

ws = Path("output/workflow/ws")
if ws.exists():
    shutil.rmtree(ws,ignore_errors=True)
os.makedirs(ws,exist_ok=True)

json_file = generate()

# This will be used as an input
scale = 3.0

commands = []
commands.append("--import")
commands.append("file="+str(json_file))
commands.append("--run")
commands.append("task=WorkflowTask")
commands.append("workflow=workflow")
commands.append(f"input=scale={scale}")

# Requires that the environment is set, but an alternative path may be given
exe =  os.getenv('SRE_EXE')
sima = SIMA(exe=exe)
output = sima.run(workspace=str(ws),commands=commands)
for line in output:
    print(line)

output = ws / "out.json"

sima_reader = SIMAReader()

items = sima_reader.read(output)
container: Container = items[0]
signals = container.signals
mynum: DimensionalScalar = container.signals[1]
print(f"{mynum.name}={mynum.value}")
if mynum.value != scale:
    raise Exception(f"Number not as expected {mynum.value} vs {scale}")





