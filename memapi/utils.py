import importlib
import inspect
import logging
from typing import List

log = logging.getLogger("memapi")


def get_allowed_args(func: callable) -> dict:
    """
    Returns allowed arguments, and their suggested types for given callable
    :param func: given callable
    :return: allowed arguments
    """
    allowed_args = dict()
    typemap = {
        dict: "object",
        int: "integer",
        str: "string",
        float: "float",
        bool: "boolean",
    }

    sig = inspect.signature(func)
    for param in sig.parameters.values():
        allowed_args[param.name] = typemap.get(param.annotation) or "object"

    return allowed_args


def get_classes_for_path(path: str, allowed_type: type) -> List[callable]:
    """
    Dynamically searches for classes on specified python (dot-separated) paths, only for classes of specified type

    :param path: Dot-separated python package path
    :param allowed_type: Type of class, to check with issubclass
    :return: List of classes
    """
    found_classes = []

    try:
        module = importlib.import_module(path)
    except ImportError as ie:
        log.error(f"Cannot import path {path}.")
        raise ie

    for item in module.__dict__:
        cls = getattr(module, item)
        if callable(cls) and issubclass(cls, allowed_type) and cls is not allowed_type:
            found_classes.append(cls)
            log.info(f"Found class {cls}")

    return found_classes
