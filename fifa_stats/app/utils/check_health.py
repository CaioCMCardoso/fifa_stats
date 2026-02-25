import os


def check_storage(csv_path: str) -> bool:
    # se a pasta do arquivo existe (ou dá pra criar), estamos ok
    folder = os.path.dirname(csv_path) or "."
    os.makedirs(folder, exist_ok=True)
    return True
