"""
Imports stask then run the given workflow with input from file
"""
import re
import os
import shutil
from pathlib import Path
from simapy.sre import SIMA
from simapy.sima_reader import SIMAReader
from simapy.sima_writer import SIMAWriter
from simapy.sima.signals.container import Container
from simapy.sima.signals.equallyspacedsignal import EquallySpacedSignal

ws = Path("output/workflow/ws")
if ws.exists():
    shutil.rmtree(ws,ignore_errors=True)
os.makedirs(ws,exist_ok=True)



a = EquallySpacedSignal(name="a")
a.value = [1.0 ,2.0, 3.0]
b = EquallySpacedSignal(name="b")
b.value = [3.0 ,4.0, 5.0]

SIMAWriter().write([a,b], ws / "input.json")

# Locate stask file in folder "input" at the root of this repository
stask = Path(__file__).parent / ".." / ".." / "output" / "wfset.stask"

commands = []
commands.append("--import")
commands.append("file="+str(stask.absolute()))
commands.append("--run")
commands.append("task=WorkflowTask")
commands.append("workflow=outer")


def __handle_output(line: str):
    # A status line looks like this: @STATUS "Total" 100 1000
    # The first number is the current value, the second is the total
    pattern = r'@STATUS "(?P<label>\w+)" (?P<current>\d+) (?P<total>\d+)'
    # Match the pattern in the string
    match = re.match(pattern, line)
    if match:
        label = match.group('label')
        current = float(match.group('current'))
        total = float(match.group('total'))
        progress = int(100*current / total)
        print(f"Progress: {label} {progress}")
    else:
        pass
        # print(line)


# Requires that the environment is set, but an alternative path may be given
exe =  os.getenv('SRE_EXE')
sima = SIMA(exe=exe)
sima.console_handler = __handle_output
sima.run(ws,commands)
output = ws / "Output/output.json"

sima_reader = SIMAReader()

items = sima_reader.read(output)
set_container: Container = items[0]
run_containers = set_container.containers
for run_container in run_containers:
    print(f"Run {run_container.name}")
    result: EquallySpacedSignal = run_container.signals[0]
    print(f"{result.name}={result.value}")
