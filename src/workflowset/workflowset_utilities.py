"""
User functions for running sima via the Python simapy module
"""

import csv
import os
from pathlib import Path

from sima.sima.storagetask import StorageTask
from sima.workflow import WorkflowSetNode, WorkflowTask
from simapy.sima import SIMA
from simapy.sima_reader import SIMAReader
from simapy.sima_writer import SIMAWriter

# pylint: disable=line-too-long
def set_json_workflowset_input_file(
    json_input_file: str = "",
    json_output_file: str = "",
    storage_task_name: str = "StorageTask",
    storage_task_root: str = "",
    workflow_task_name: str = "WorkflowTask",
    workflow_name: str = "workflow",
    workflow_input_file: str = "",
):
    """
    Reads a sima json file and sets StorageTask Path and WorkflowSet input file.

    Loops through all tasks (assuming no folders) until it finds the one with the specified workflow_task_name.
    For this task, it loops through all sub tasks and find the one with the specified workflow_name.
    For this sub taks, it takes the first node in the workflow and sets the path to a user specified workflow_input_file.

    Loops through all tasks (assuming no folders) until it finds the one with the specified storage_task_name.
    For this task, it specifies the root as storage_task_root.

    Then, it saves the modified json file at the specified json_output_file location and returns the path.
    """

    # Find all tasks inside sima json file (assuming no folders)
    reader = SIMAReader()
    tasks = reader.read(json_input_file)

    # Loop through tasks and find specified workflow and storage tasks
    for task in tasks:
        if task.name == storage_task_name:
            storage_task: StorageTask = task
            storage_task.root = storage_task_root

        if task.name == workflow_task_name:
            workflow_task: WorkflowTask = task
            workflows = workflow_task.workflows
            for workflow in workflows:
                if workflow.name == workflow_name:
                    # Assume its the first item (nodes[0]) inside workflow, which is the workflow set
                    node: WorkflowSetNode = workflow.nodes[0]
                    node.filename = workflow_input_file

    # Print search results to use
    if not storage_task:
        raise ValueError(
            f"Could not find a StorageTask with the name '{storage_task_name}'."
        )
    if not workflow_task:
        raise ValueError(
            f"Could not find a WorkflowTask with the name '{workflow_task_name}'."
        )
    if not node:
        raise ValueError(f"Could not find a Workflow with the name '{workflow_name}'.")

    # Write modifications to new json file
    file_out = Path(json_output_file)
    os.makedirs(file_out.parent, exist_ok=True)
    writer = SIMAWriter()
    writer.write(tasks, file_out)


def generate_workflowset_input_file(file_out: str, input_variables: dict):
    """ Generate input file for workflowset from a dict of input variables."""

    # Check if length of all inputs are the same
    lengths = [len(val) for val in input_variables.values()]
    set_length = lengths[0]
    for input_length in lengths:
        if set_length != input_length:
            raise ValueError("Values in input_variables does not have the same length")

    with open(file_out, "w", newline="",encoding="utf8") as f:
        file_header = "'" + " ".join(input_variables.keys()) + "\n"
        f.write(file_header)
        csv.writer(f, delimiter=" ").writerows(zip(*input_variables.values()))


def run_sima(workspace: str, commands: list[str], exe: str):
    """Run SIMA with the given workspace directory and command line arguments."""
    sima = SIMA(exe=exe)
    output = sima.run(workspace, commands)

    return output
