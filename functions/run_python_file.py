import os
import subprocess

from google.genai import types
from typing_extensions import List


def run_python_file(working_directory, file_path: str, args: List = []):
    working_dir_abs = os.path.abspath(working_directory)
    target_file = os.path.normpath(
        os.path.join(working_dir_abs, file_path)
    )  # normpath "normalizes" .. . like stuff
    valid_target_file = (  # Commonpath returns the longest sub-path between two paths
        os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs
    )
    if not valid_target_file:
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory.'
    if not os.path.isfile(target_file):
        return f'Error: "{file_path}" does not exist or is not regular file'
    if not file_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file'

    try:
        command = ["python", target_file]
        if args is not None:
            command.extend(args)
        process = subprocess.run(
            command, timeout=30, capture_output=True, cwd=working_dir_abs, text=True
        )
        output_string = ""
        if process.returncode != 0:
            output_string += f"Process exited with code {process.returncode}\n"
        if len(process.stdout) == 0 and len(process.stderr) == 0:
            output_string += "No output produced\n"
        else:
            output_string += f"STDOUT: {process.stdout}\n"
            output_string += f"STDERR: {process.stderr}\n"
        return output_string
    except Exception as e:
        return f"Error: executing Python file: {e}"


schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Execute a python file with optional arguments provided in a specific file path relative to the working directory",
    parameters=types.Schema(
        required=["file_path"],
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Mandatory file path to execute a python file, relative to the working directory",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Optional extra arguments list including arguments to execute a python file with",
                items=types.Schema(
                    type=types.Type.STRING,
                    description="Singular arguments in the args list (default is an empty list)",
                ),
            ),
        },
    ),
)
