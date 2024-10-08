"""
Generate a workflow then run it with input using SIMA
"""
import os
import shutil
from pathlib import Path
from simapy.sre import SIMA
from simapy.sima_reader import SIMAReader
from simapy.sima import signals

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

# Create a handler to print the progress while running
def __handle_output(line):
    # "@STATUS "Total" 800 1000"
    if line.startswith("@STATUS"):
        # Findt the last number
        parts = line.split()
        worked = float(parts[-1-1])
        total = float(parts[-1])
        progress = 100 * worked/total
        print("Progress: ",progress,"%")

sima.console_handler = __handle_output
sima.run(ws,commands)

output = ws / "out.json"

sima_reader = SIMAReader()

items = sima_reader.read(output)
container: signals.Container = items[0]
mynum: signals.DimensionalScalar = container.signals[1]
print(f"{mynum.name}={mynum.value}")
if mynum.value != scale:
    raise ValueError(f"Number not as expected {mynum.value} vs {scale}")
