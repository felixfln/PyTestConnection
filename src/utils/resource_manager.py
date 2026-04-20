import os
import sys

def get_resource_path(relative_path: str) -> str:
    """Obtém o caminho absoluto para um recurso, funcionando em desenvolvimento ou no executável PyInstaller."""
    try:
        # PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except (AttributeError, Exception):
        # Em modo desenvolvimento, o diretório do projeto pode ser um nível acima se src for o root
        # mas como PyInstaller está sendo executado da raiz do repo,
        # vamos usar o caminho absoluto do arquivo atual como referência ou o CWD
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
