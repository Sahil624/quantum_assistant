import json
import os
import nbformat
from nbconvert import HTMLExporter
from traitlets.config import Config
import ast
import sys

from core.base.config import config
from core.pre_processor.common import get_nb_files_path


def safe_exec(code, globals_dict):
    try:
        tree = ast.parse(code)
        exec(compile(tree, filename="<ast>", mode="exec"), globals_dict)
    except Exception as e:
        print(f"Error executing code: {e}")
        return str(e)


def execute_notebook(nb):
    globals_dict = {}
    for cell in nb.cells:
        if cell.cell_type == 'code':
            outputs = []
            if cell.source.strip():  # Only execute non-empty cells
                output = safe_exec(cell.source, globals_dict)
                if output:
                    outputs.append(nbformat.v4.new_output('error', ename='Error', evalue=str(output)))
            cell.outputs = outputs
    return nb


def convert_notebook_to_html_files(notebook_path):
    # Load the notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    # Execute all code cells
    nb = execute_notebook(nb)

    # Configure the HTMLExporter
    c = Config()
    c.HTMLExporter.preprocessors = ['nbconvert.preprocessors.ExtractOutputPreprocessor']
    html_exporter = HTMLExporter(config=c)

    # Create output directory
    output_dir = './server/static/notebooks'
    os.makedirs(output_dir, exist_ok=True)

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
            path = os.path.join(output_dir, filename)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(body)

            print(f"Created {path}")


def generate_output():
    notebook_paths = get_nb_files_path(config['notebook_directory'])
    for path in notebook_paths:
        print(f"Processing {path}...")
        convert_notebook_to_html_files(path)
        print(f"Finished processing {path}")


if __name__ == "__main__":
    generate_output()
