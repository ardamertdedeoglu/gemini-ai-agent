import os

from google.genai import types


def get_files_info(working_directory, directory="."):
    working_dir_abs = os.path.abspath(working_directory)
    target_dir = os.path.normpath(
        os.path.join(working_dir_abs, directory)
    )  # normpath "normalizes" .. . like stuff
    valid_target_dir = (  # Commonpath returns the longest sub-path between two paths
        os.path.commonpath([working_dir_abs, target_dir]) == working_dir_abs
    )
    if not valid_target_dir:  # This way it doesnt work outside of the working directory
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory.'
    if not os.path.isdir(target_dir):
        return f'Error: "{directory}" is not a valid directory.'

    result = ""
    try:
        with os.scandir(target_dir) as dir_contents:
            for entry in dir_contents:
                info = entry.stat()
                result += f"{entry.name}: file_size={info.st_size} bytes, is_dir={entry.is_dir()}\n"
        return result
    except Exception as e:
        return f"Error: {e}"


schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
)
