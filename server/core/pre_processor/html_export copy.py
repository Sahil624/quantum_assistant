import json
import os
import re
import shutil
import threading
import time
import nbformat
from nbconvert import HTMLExporter
from traitlets.config import Config
import ast
import sys

from server.core.base.config import config
from server.core.pre_processor.common import get_nb_files_path

# Create output directory
OUTPUT_DIR = './voila/out'

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

def get_module_folder(notebook_path):
    dependency = notebook_path.split('/')
    dependency.pop()
    dependency = '/'.join(dependency)
    return dependency

def copy_source_code(notebook_path):

    try:
        os.mkdir(os.path.join(OUTPUT_DIR, 'pyfiles'))
    except FileExistsError:
        pass

    dependency = get_module_folder(notebook_path)
    dependency = os.path.join(dependency, 'pyfiles')

    if not os.path.exists(dependency):
        print("No Dep Folder")
        return

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

def copy_images(notebook_path):
    try:
        os.mkdir(os.path.join(OUTPUT_DIR, 'images'))
    except FileExistsError:
        pass

    dependency = notebook_path.split('/')
    dependency.pop()
    dependency = '/'.join(dependency)
    dependency = os.path.join(dependency, 'images')

    if not os.path.exists(dependency):
        return

    for file in os.listdir(dependency):
        if not file.endswith('.png'):
            continue
        path = os.path.join(dependency, file)
        out = os.path.join(OUTPUT_DIR, 'images/'+ file)
        if os.path.exists(path):
            shutil.copyfile(path, out)
            print('Dependency Copied', out)
        else:
            print("Path does not exists", path)
    
def find_finalquiz_file(content, search_path):
    # Extract the base name and number from the content
    pattern = r'filename:\s*(finalquiz(\d+))\.ipynb'
    match = re.search(pattern, content)
    if not match:
        return None
    
    base_name = match.group(1)
    quiz_number = match.group(2)
    
    # Create a regex pattern for file search
    file_pattern = rf'finalquiz\d*{quiz_number}\.ipynb'
    
    # Search for matching files in the given path
    for file in os.listdir(search_path):
        if re.match(file_pattern, file):
            return os.path.join(search_path, file)
    
    return None

def convert_notebook_to_html_files(notebook_path):

    # Load the notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    # Execute all code cells
    # source_files = fetch_dependency_files(nb)
    # copy_source_code(notebook_path)
    # copy_images(notebook_path)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    common_import = None
    if nb.cells[0]["cell_type"] == "code":
        source_lines = nb.cells[0]["source"].split("\n")

        first_line = ""
        for source in source_lines:
            first_line = source
            if first_line and first_line[0] != "#":
                break

        # If first cell starts and end with import (after ignoring comments) this is import cell (most probably for visualizations).
        # This should be imported in each sub cell.
        if first_line.startswith("import ") and source_lines[-1].startswith("import "):
            common_import = nb.cells[0]
            print("Common Import cell found", source_lines)
        
    cell_id = None
    # Convert each cell
    for cell in nb.cells:
        if 'cell_details' in cell.metadata and 'cell_ID' in cell.metadata['cell_details']:
            cell_id = cell.metadata['cell_details']['cell_ID']
            
            if "notfinalquiz" in cell_id.lower():
                content = cell["source"]
                dependency = get_module_folder(notebook_path)
                quiz_path = find_finalquiz_file(content, dependency)
                print("++++++++++++++++++")
                print(quiz_path)
                print("++++++++++++++++++")
                if quiz_path:
                    # filename = quiz_path.split('/')[-1].split('.')[0]
                    filename = cell_id + '_final_quiz'
                    # out_path = os.path.join(OUTPUT_DIR, filename)
                    # cmd = f'jupyter nbconvert "{quiz_path}" --to html --embed-images --output-dir={OUTPUT_DIR} --output={filename}'
                    # os.system(cmd)
                    cmd = f'jupyter nbconvert "{quiz_path}" --to notebook --embed-images --output-dir={OUTPUT_DIR} --output={filename}'
                    os.system(cmd)
                    # cmd = f'jupyter nbconvert "{quiz_path}" --to html --embed-images --output-dir={OUTPUT_DIR} --output={cell_id}'
                    # os.system(cmd)
                    cmd = f'jupyter nbconvert "{quiz_path}" --to notebook --embed-images --output-dir={OUTPUT_DIR} --output={cell_id}'
                    os.system(cmd)
                    print("Quiz Convert File Path", cmd)
                    continue
            


            # Create a temporary notebook with just this cell
            temp_nb = nbformat.v4.new_notebook()
            temp_nb.cells = []

            if common_import:
                temp_nb.cells.append(common_import)

            temp_nb.cells.append(cell)

            # # Convert to HTML
            # (body, resources) = html_exporter.from_notebook_node(temp_nb)

            # # Write to file
            filename = f"{cell_id}.html"
            out_path = os.path.join(OUTPUT_DIR, filename)
            # with open(path, 'w', encoding='utf-8') as f:
            #     f.write(body)

            filename = f"{cell_id}.ipynb"
            path = os.path.join(OUTPUT_DIR, filename)

            with open(path, 'w', encoding='utf-8') as f:
                nbformat.write(temp_nb, f)
                
            os.system(f'jupyter nbconvert {path} --to html --embed-images -o {out_path}')
            # print(f"Created {path}")
    
        if cell_id:
            module = cell_id.split("-")[0]
            # Convert to HTML
            # (body, resources) = html_exporter.from_notebook_node(nb)

            # Write to file
            filename = f"{module}.html"
            out_path = os.path.join(OUTPUT_DIR, filename)
            # with open(path, 'w', encoding='utf-8') as f:
            #     f.write(body)

            filename = f"{module}.ipynb"
            path = os.path.join(OUTPUT_DIR, filename)

            with open(path, 'w', encoding='utf-8') as f:
                nbformat.write(nb, f)
                
            os.system(f'jupyter nbconvert {path} --to html --embed-images -o {out_path}')

def run_process(notebook_paths):
    time.sleep(3)
    for path in notebook_paths:
        print(f"Processing {path}...")
        convert_notebook_to_html_files(path)

        # module = path.split("/")[-1].split('.')[0]
        # filename = f"{module}.html"
        # out_path = os.path.join(OUTPUT_DIR, filename)
        # cmd = f'jupyter nbconvert "{path}" --to html --embed-images --output-dir={OUTPUT_DIR}'
        # print(cmd)
        # os.system(cmd)

        print(f"Finished processing {path}")

def generate_output():
    notebook_paths = get_nb_files_path(config['notebook_directory'])

    threads = 50

    thread_objs = []
    step =  len(notebook_paths)//threads
    for i in range(0, len(notebook_paths),step):
        print(f"Thread #{i} started")
        thread_objs.append(threading.Thread(target=run_process, args=(notebook_paths[i:i+step],), daemon=True))

    for t in thread_objs:
        t.run()

if __name__ == "__main__":
    generate_output()
