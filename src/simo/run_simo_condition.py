"""
Imports stask then run the given condition with input from file
"""
import os
import shutil
from pathlib import Path

from simapy.sima import SIMA

ws = Path("output/simo/condition")
if ws.exists():
    shutil.rmtree(ws, ignore_errors=True)
os.makedirs(ws, exist_ok=True)


stask = Path("input/simo/simo.stask")

commands = []
commands.append("--import")
commands.append("file=" + str(stask.absolute()))
commands.append("--condition")
commands.append("task=BouncingBalls")
commands.append("condition=conditionSet")
commands.append("runType=dynamic")

# Requires that the environment is set, but an alternative path may be given
exe = os.getenv("SRE_EXE")
sima = SIMA(exe=exe)
output = sima.run(workspace=str(ws), commands=commands)
for line in output:
    print(line)
