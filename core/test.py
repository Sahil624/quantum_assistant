from core.assistant.assistant import main as assistant_main
from core.generator.test import main as generator_main


main_map = {
    'assistant': assistant_main,
    'generator': generator_main
}

def test_core(module: str):
    try:
        print(f'Will try to run {module} module')
        main_map[module]()
    except KeyError as e:
        print(f"Module {e} is invalid. Valid Options are {list(main_map.keys())}")
