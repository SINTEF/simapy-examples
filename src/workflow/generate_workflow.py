"""
Import a json file with a template for a workflow task and a storage task
Update the storage task to point to the script
"""

import os
from pathlib import Path
from simapy.sima_reader import SIMAReader
from simapy.sima_writer import SIMAWriter
from simapy.sima.sima.storagetask import StorageTask

def generate() -> Path:
    reader = SIMAReader()
    tasks = reader.read("input/workflow/workflow_task.json")
    # Using type hints is not necessary but is useful to get automatic help when using an IDE, such as vscode or pycharm

    # We will now update the storage task to point to this script using the relative root
    here =  Path(__file__).parent
    storage_task: StorageTask = tasks[1]
    storage_task.root = str(here)

    file =  Path("output/workflow/workflow_task_mod.json")
    os.makedirs(file.parent,exist_ok=True)
    writer = SIMAWriter()
    writer.write(tasks,file)
    return file

def main():
    generate()

if __name__ == '__main__':
    main()
