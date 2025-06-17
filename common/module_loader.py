import importlib


def load_uploader_module(name: str):
    module_path = f"uploaders.{name}_content_uploader"
    content_uploader_module = importlib.import_module(f"{module_path}.content_uploader")
    init_module = importlib.import_module(f"{module_path}.__init__")

    return content_uploader_module.ContentUploader, init_module.UPLOADER_NAME
