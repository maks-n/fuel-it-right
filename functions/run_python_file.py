import os
import subprocess
from google.genai import types


def run_python_file(working_directory, file_path, args=[]):
    abs_working_dir = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))

    if not abs_file_path.startswith(abs_working_dir):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    if not os.path.exists(abs_file_path):
        return f'Error: File "{file_path}" not found.'

    if not abs_file_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'

    # https://docs.python.org/3/library/subprocess.html#subprocess.run
    try:
        commands=["python", abs_file_path]
        if args:
            commands.extend(args)
        completed_process = subprocess.run(
            commands,
            timeout=30,
            capture_output=True,
            text=True,
            cwd=abs_working_dir,
        )
        result = []
        if completed_process.stdout:
            result.append(f'STDOUT:\n{completed_process.stdout}')
        if completed_process.stderr:
            result.append(f'STDERR:\n{completed_process.stderr}')
        if completed_process.returncode != 0:
            result.append(f'Process exited with code {completed_process.returncode}')
        return "\n".join(result) if result else "No output produced."
    except Exception as e:
        return f'Error: executing Python file: {e}'


schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Execute Python files with optional arguments. Constrained to the file path in the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The python file to execute, relative to the working directory. Must be provided. Must have '.py' extension.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="The optional commands to execute python file with.",
                items=types.Schema(type=types.Type.STRING),
            ),
        },
    ),
)
