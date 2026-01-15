import os

from google.genai import types

from config import MAX_CHARS


def get_file_content(working_directory, file_path):
    working_dir_abs = os.path.abspath(working_directory)
    target_file = os.path.normpath(
        os.path.join(working_dir_abs, file_path)
    )  # normpath "normalizes" .. . like stuff
    valid_target_file = (  # Commonpath returns the longest sub-path between two paths
        os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs
    )
    if (
        not valid_target_file
    ):  # This way it doesnt work outside of the working directory
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory.'
    if not os.path.isfile(target_file):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    try:
        with open(target_file) as f:
            file_content = f.read(MAX_CHARS)
            if f.read(1):
                file_content += (
                    f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
                )
            return file_content
    except Exception as e:
        return f"Error: {e}"


schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Read file contents in a specific file path relative to the working directory, providing a maximum amount of chars",
    parameters=types.Schema(
        required=["file_path"],
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Mandatory file path to read contents from, relative to the working directory",
            ),
        },
    ),
)
