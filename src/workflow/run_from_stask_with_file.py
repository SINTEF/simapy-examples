"""
Imports stask then run the given workflow with input from file
"""
import os
import shutil
from pathlib import Path
from simapy.sima import SIMA
from simapy.sima_reader import SIMAReader
from simapy.sima_writer import SIMAWriter
from marmo.containers.container import Container
from marmo.containers.equallyspacedsignal import EquallySpacedSignal

ws = Path("output/workflow/ws")
if ws.exists():
    shutil.rmtree(ws,ignore_errors=True)
os.makedirs(ws,exist_ok=True)



a = EquallySpacedSignal(name="a")
a.value = [1.0 ,2.0, 3.0]
b = EquallySpacedSignal(name="b")
b.value = [3.0 ,4.0, 5.0]

SIMAWriter().write([a,b], ws / "input.json")

stask = Path("input/workflow/simple_workflow_run.stask")

commands = []
commands.append("--import")
commands.append("file="+str(stask.absolute()))
commands.append("--run")
commands.append("task=WorkflowTask")
commands.append("workflow=outer")

# Requires that the environment is set, but an alternative path may be given
exe =  os.getenv('SIMA_EXE')
sima = SIMA(exe=exe)
output = sima.run(workspace=str(ws),commands=commands)
for line in output:
    print(line)

output = ws / "Output/output.json"

sima_reader = SIMAReader()

items = sima_reader.read(output)
set_container: Container = items[0]
run_containers = set_container.containers
for run_container in run_containers:
    print(f"Run {run_container.name}")
    result: EquallySpacedSignal = run_container.signals[0]
    print(f"{result.name}={result.value}")





