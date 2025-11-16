import os
from google.genai import types

from config import MAX_CHARS

def get_file_content(working_directory, file_path):
    abs_working_dir = os.path.abspath(working_directory)
    target_file = os.path.abspath(os.path.join(working_directory, file_path))

    if not target_file.startswith(abs_working_dir):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(target_file):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    try:
        with open(target_file, "r") as f:
            file_content = f.read(MAX_CHARS)
            if os.path.getsize(target_file) > MAX_CHARS:
                file_content += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
        return file_content
    except Exception as e:
        return f'Error reading file "{target_file}": {e}'


schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Read file's content, constrained to the file path in the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file to read content from, relative to the working directory. Must be provided.",
            ),
        },
    ),
)
