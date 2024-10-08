from server.core.assistant.assistant import main as assistant_main
from server.core.generator.test import main as generator_main
from server.core.pre_processor.html_export import generate_output
from server.core.pre_processor.tokenizer import main as tokenizer_main

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


def pre_processor():
    print('Running pre processing tasks')
    # tokenizer_main()
    generate_output()
    print('Completed pre processing tasks')
