import os
import sys
from glob import glob
from typing import List


def get_nb_files_path(directory: str) -> List[str]:
    if not os.path.exists(directory):
        print('Invalid notebook path', directory)
        sys.exit(-1)
    notebook_pattern = os.path.join(directory, "**", "*.ipynb")
    print('Search path', notebook_pattern)
    notebook_files = glob(notebook_pattern, recursive=True)
    return notebook_files
