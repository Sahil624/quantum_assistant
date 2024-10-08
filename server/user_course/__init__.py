
import json
from .metastore import set_cell_metadata, set_notebook_metadata


def load_lo_metadata():
    cell_json = "../../QC_Notes/cell_data.json"
    notebook_json = "../../QC_Notes/notebook_data.json"

    with open(cell_json) as f:
        set_cell_metadata(json.loads(f.read()))

    with open(notebook_json) as f:
        set_notebook_metadata(json.loads(f.read()))



load_lo_metadata()