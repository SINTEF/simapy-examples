"""
This example demonstrates how the Python module concurrent.futures may be used to run
workflows with multiple SIMA instances concurrently.
"""
import os
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from simapy.sima import SIMA
from simapy.sima_writer import SIMAWriter
from marmo.containers.equallyspacedsignal import EquallySpacedSignal

def run_single(case_num: int, a: float, b: float):
    print(f'Starting case {case_num}')
    ws = Path(f'ws_{case_num}')
    if ws.exists():
        shutil.rmtree(ws,ignore_errors=True)
    os.makedirs(ws,exist_ok=True)

    a_signal = EquallySpacedSignal(name='a')
    a_signal.value = [a]
    b_signal = EquallySpacedSignal(name='b')
    b_signal.value = [b]

    SIMAWriter().write([a_signal, b_signal], ws / 'input.json')

    # Locate stask file in folder 'input' at the root of this repository
    stask = Path(__file__).parent / '..' / '..' / 'input' / 'workflow' / 'simple_workflow_run.stask'

    commands = []
    commands.append('--import')
    commands.append('file='+str(stask.absolute()))
    commands.append('--run')
    commands.append('task=WorkflowTask')
    commands.append('workflow=outer')

    # Requires that the environment is set, but an alternative path may be given
    exe =  os.getenv('SRE_EXE')
    sima = SIMA(exe=exe)
    output = sima.run(workspace=str(ws),commands=commands)
    with open(ws / 'sre-output.txt', 'w') as f:
        for line in output:
            f.write(line + '\n')
    print(f'Case {case_num} completed')


# Run a maximum of cpu_count() - 1 workflows at the same time
num_concurrent = os.cpu_count() - 1
# Total number of workflow runs
num_cases = 10
with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
    for i in range(num_cases):
        # Set some arbitrary values for a and b
        a = i * 2.0
        b = (i + 1) * 10.0
        # Submit job
        executor.submit(run_single, i, a, b)

print('All cases completed')
