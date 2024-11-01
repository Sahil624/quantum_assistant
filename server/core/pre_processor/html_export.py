import json
import os
import re
import shutil
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import time
import nbformat
from nbconvert import HTMLExporter
from pathlib import Path
from typing import List, Optional
import logging

from server.core.base.config import config
from server.core.pre_processor.common import get_nb_files_path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
OUTPUT_DIR = Path('./voila/out')
RUN_COMMAND = "%run"
MAX_WORKERS = max(1, multiprocessing.cpu_count() - 1)  # Leave one CPU free

class NotebookConverter:
    def __init__(self):
        self._setup_output_directories()
        
    def _setup_output_directories(self):
        """Create necessary output directories"""
        OUTPUT_DIR.mkdir(exist_ok=True)
        (OUTPUT_DIR / 'pyfiles').mkdir(exist_ok=True)
        (OUTPUT_DIR / 'images').mkdir(exist_ok=True)

    @staticmethod
    def find_finalquiz_file(content: str, search_path: Path) -> Optional[Path]:
        """Find the final quiz file path"""
        pattern = r'filename:\s*(finalquiz(\d+))\.ipynb'
        match = re.search(pattern, content)
        if not match:
            return None
        
        quiz_number = match.group(2)
        file_pattern = rf'finalquiz\d*{quiz_number}\.ipynb'
        
        try:
            return next(p for p in search_path.iterdir() 
                       if p.is_file() and re.match(file_pattern, p.name))
        except StopIteration:
            return None

    def copy_dependencies(self, notebook_path: Path):
        """Copy dependency files and images"""
        module_folder = notebook_path.parent
        
        # Copy Python files
        py_files_source = module_folder / 'pyfiles'
        if py_files_source.exists():
            for py_file in py_files_source.glob('*.py'):
                shutil.copy2(py_file, OUTPUT_DIR / 'pyfiles' / py_file.name)
                
        # Copy images
        images_source = module_folder / 'images'
        if images_source.exists():
            for image in images_source.glob('*.png'):
                shutil.copy2(image, OUTPUT_DIR / 'images' / image.name)

    def convert_notebook(self, notebook_path: str):
        """Convert a single notebook to HTML files"""

        try:
            notebook_path = Path(notebook_path)
            self.copy_dependencies(notebook_path)
            logger.info(f"Processing {notebook_path}")
            
            # Read notebook
            with open(notebook_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)

            # Handle common imports
            common_import = None
            if nb.cells and nb.cells[0]["cell_type"] == "code":
                source_lines = nb.cells[0]["source"].splitlines()
                non_comment_lines = [line for line in source_lines if line.strip() and not line.strip().startswith('#')]
                if non_comment_lines and all(line.strip().startswith("import ") for line in [non_comment_lines[0], non_comment_lines[-1]]):
                    common_import = nb.cells[0]
                    logger.debug("Found common import cell")

            # Process cells
            for cell in nb.cells:
                cell_metadata = cell.metadata.get('cell_details', {})
                cell_id = cell_metadata.get('cell_ID')
                
                if not cell_id:
                    continue

                if "notfinalquiz" in cell_id.lower():
                    content = cell["source"]
                    quiz_path = self.find_finalquiz_file(content, notebook_path.parent)
                    if quiz_path:
                        self._process_quiz_file(quiz_path, cell_id)
                        continue

                self._process_cell(cell, cell_id, common_import)

            # Process module
            if cell_id:
                module = cell_id.split("-")[0]
                self._process_module(nb, module)

        except Exception as e:
            logger.error(f"Error processing {notebook_path}: {str(e)}")
            raise

    def _process_quiz_file(self, quiz_path: Path, cell_id: str):
        """Process quiz files"""
        filename = f"{cell_id}_final_quiz"
        self._run_nbconvert(quiz_path, filename)
        self._run_nbconvert(quiz_path, cell_id)

    def _process_cell(self, cell, cell_id: str, common_import):
        """Process individual cells"""
        temp_nb = nbformat.v4.new_notebook()
        if common_import:
            temp_nb.cells.append(common_import)
        temp_nb.cells.append(cell)

        out_path = OUTPUT_DIR / f"{cell_id}"
        with open(f"{out_path}.ipynb", 'w', encoding='utf-8') as f:
            nbformat.write(temp_nb, f)
        
        self._run_nbconvert(f"{out_path}.ipynb", cell_id)

    def _process_module(self, nb, module: str):
        """Process complete modules"""
        out_path = OUTPUT_DIR / module
        with open(f"{out_path}.ipynb", 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
        
        self._run_nbconvert(f"{out_path}.ipynb", module)

    @staticmethod
    def _run_nbconvert(input_path: Path, output_name: str):
        """Run nbconvert command"""
        os.system(f'jupyter nbconvert "{input_path}" --to html --embed-images --output-dir="{OUTPUT_DIR}" --output="{output_name}"')

def process_notebooks_chunk(notebook_paths):
    """Process a chunk of notebooks"""
    converter = NotebookConverter()
    for path in notebook_paths:
        converter.convert_notebook(path)

def generate_output():
    """Main function to generate output"""
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    start_time = time.time()
    notebook_paths = get_nb_files_path(config['notebook_directory'])
    
    # Split notebooks into chunks
    chunk_size = max(1, len(notebook_paths) // MAX_WORKERS)
    chunks = [notebook_paths[i:i + chunk_size] for i in range(0, len(notebook_paths), chunk_size)]
    
    logger.info(f"Processing {len(notebook_paths)} notebooks in {len(chunks)} chunks")
    
    # Use Pool instead of ProcessPoolExecutor for better compatibility
    with multiprocessing.Pool(processes=MAX_WORKERS) as pool:
        pool.map(process_notebooks_chunk, chunks)
    
    end_time = time.time()
    logger.info(f"Total execution time: {end_time - start_time:.2f} seconds")

if __name__ == '__main__':
    multiprocessing.freeze_support()
    generate_output()