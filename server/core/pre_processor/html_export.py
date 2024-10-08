import json
import os
import shutil
import nbformat
from nbconvert import HTMLExporter
from traitlets.config import Config
import ast
import sys

from server.core.base.config import config
from server.core.pre_processor.common import get_nb_files_path

# Create output directory
OUTPUT_DIR = './voila'

RUN_COMMAND = "%run"

def fetch_dependency_files(nb) -> list[str]:
    source_files = []
    for cell in nb.cells:
        if cell.cell_type == 'code':
            outputs = []
            if cell.source.strip():  # Only execute non-empty cells
                source_code = cell['source']
                if RUN_COMMAND in source_code:
                    source_files.append(source_code.split(' ')[1]+'.py')
                else:
                    print("No run command in code cell", source_code)
            cell.outputs = outputs
    return source_files


def convert_notebook_to_html_files(notebook_path):


    # Load the notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    # Execute all code cells
    # source_files = fetch_dependency_files(nb)

    dependency = notebook_path.split('/')
    dependency.pop()
    dependency = '/'.join(dependency)
    dependency = os.path.join(dependency, 'pyfiles')
    for file in os.listdir(dependency):
        if not file.endswith('.py'):
            continue
        path = os.path.join(dependency, file)
        out = os.path.join(OUTPUT_DIR, 'pyfiles/'+ file)
        if os.path.exists(path):
            shutil.copyfile(path, out)
            print('Dependency Copied', out)
        else:
            print("Path does not exists", path)


    # Configure the HTMLExporter
    c = Config()
    c.HTMLExporter.preprocessors = ['nbconvert.preprocessors.ExtractOutputPreprocessor']
    html_exporter = HTMLExporter(config=c)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Convert each cell
    for cell in nb.cells:
        if 'cell_details' in cell.metadata and 'cell_ID' in cell.metadata['cell_details']:
            cell_id = cell.metadata['cell_details']['cell_ID']

            # Create a temporary notebook with just this cell
            temp_nb = nbformat.v4.new_notebook()
            temp_nb.cells = [cell]

            # Convert to HTML
            (body, resources) = html_exporter.from_notebook_node(temp_nb)

            # Write to file
            filename = f"{cell_id}.html"
            path = os.path.join(OUTPUT_DIR, filename)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(body)

            filename = f"{cell_id}.ipynb"
            path = os.path.join(OUTPUT_DIR, filename)

            with open(path, 'w', encoding='utf-8') as f:
                nbformat.write(temp_nb, f)
                
            # print(f"Created {path}")


def generate_output():
    try:
        os.mkdir(os.path.join(OUTPUT_DIR, 'pyfiles'))
    except FileExistsError:
        pass

    notebook_paths = get_nb_files_path(config['notebook_directory'])
    for path in notebook_paths:
        print(f"Processing {path}...")
        convert_notebook_to_html_files(path)
        print(f"Finished processing {path}")


if __name__ == "__main__":
    generate_output()
