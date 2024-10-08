import logging

from common.exceptions import CellMetaDataNotFoundError


_CELL_METADATA = {}
_NOTEBOOK_METADATA = {}

def set_cell_metadata(data: dict):
    for _, cells in data.items():
        for cell in cells:
            meta_data = cell['metadata']['cell_details']
            _CELL_METADATA[meta_data['cell_ID']] = meta_data

def get_cell_meta(cell_id: str, raise_exception = True):
    try:
        return _CELL_METADATA[cell_id]
    except KeyError as e:
        err_str = f"Cell ID {cell_id} not found in META_DATA"
        logging.error(err_str)
        if raise_exception:
            raise CellMetaDataNotFoundError(err_str)
    return None


def set_notebook_metadata(data: dict):
    for title, meta_data in data.items():
        _NOTEBOOK_METADATA[title] = {
            'outcomes': [],
            'module_prereqs': meta_data['module_prereqs']
        }

        for i, outcome in enumerate(meta_data['module_outcomes']):
            try:
                mapping = meta_data['module_outcomes_mapping'][i]
            except IndexError: 
                logging.error(f'Could not find module mapping for topic "{title}", outcome "{outcome}" at index "{i}". Defaulting to []')
                mapping = []
            _NOTEBOOK_METADATA[title]['outcomes'].append({
                'outcome': outcome,
                'outcome_mapping': mapping
            })


def get_all_notebook_meta():
    return _NOTEBOOK_METADATA
