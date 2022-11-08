"""
Modifies an sima workflowset (json) to take input from file, run it using SIMA and load in results for plotting figures
"""

import os
import shutil
from pathlib import Path
from simapy_utilities import run_sima, generate_workflowset_input_file, set_json_workflowset_input_file

from matplotlib import pyplot as plt
import numpy as np
import h5py

# Root folder, path to sima sre exe and other file names
root = str(Path(__file__).parent)
sre_exe_path =  os.getenv('SRE_EXE')
original_json_file = root + "/input/workflow_task.json"
json_file = root + "/output/workflow_task_mod.json"
workspace = root + "/output/ws-tmp"
storage_task_name = "StorageTask"
storage_task_root = root + "/output"
workflow_task_name = "WorkflowTask"
workflow_name = "workflowset"
workflowset_input_file = root + "/input/wf_set_list.txt"
workflowset_input_variables = {
    "dt": 3*[0.01],
    "period" : [10., 20., 30.],
    "scale" : [1., 2., 3.],
    "time" : [100., 100., 100.],
    "hdf5_file_out_prefix" : ["wf_set_run_1", "wf_set_run_2", "wf_set_run_3"]
    }

# Generate workflowset input file
generate_workflowset_input_file(
    file_out = workflowset_input_file,
    input_variables = workflowset_input_variables,
    )

# Modify sima json file to link to workflowset input file
set_json_workflowset_input_file(
    json_input_file = original_json_file,
    json_output_file = json_file,
    storage_task_name = storage_task_name,
    storage_task_root = storage_task_root,
    workflow_task_name = workflow_task_name,
    workflow_name = workflow_name,
    workflow_input_file = workflowset_input_file
    )

# Commands given to sima when executing workflow
commands = []
commands.append("--import")
commands.append(f'file="{json_file}"')
commands.append("--run")
commands.append(f"task={workflow_task_name}")
commands.append(f"workflow={workflow_name}")

# Create worspace folder, run sima and delete worspace folder
# Re-create workspace folder
ws = Path(workspace)
if ws.exists():
    shutil.rmtree(ws, ignore_errors=True)
os.makedirs(ws, exist_ok=True)

# Execute sima sre in specified workspace with list of commands
try:
    run_sima(workspace=workspace, commands=commands, exe=sre_exe_path)
finally:
    # Remove temporary worspace folder
    shutil.rmtree(ws, ignore_errors=True)# not working (sima.log active...)

# Read hdf5 file, modify data and plot results
for i, hdf5_prefix in enumerate(workflowset_input_variables["hdf5_file_out_prefix"]):
    hdf5_file = root + "/output/" + hdf5_prefix + ".h5"
    with h5py.File(hdf5_file, "r") as f:
        
        # Read timeseries data
        signal_cos = f["/signal_cos"]
        signal_sin = f["/signal_sin"]

        # Analyze data
        N = len(signal_cos)
        dt = signal_cos.attrs["delta"]
        t0 = signal_cos.attrs["start"]
        time = np.linspace(t0, dt*(N-1), N)

        # PLot
        plt.figure(i+1)
        plt.plot(time, np.array(signal_cos))
        plt.plot(time, np.array(signal_sin))
        plt.plot(time, 3*np.array(signal_sin) - 2*np.array(signal_cos))

plt.show()
