import importlib
import inspect
import logging

log = logging.getLogger("memapi")


def get_allowed_args(func: callable) -> list:
    """
    Returns allowed arguments for given callable
    :param func: given callable
    :return: allowed arguments list
    """
    allowed_args = list()
    [allowed_args.append(i) for i in inspect.getargs(func.__code__).args or []]
    [allowed_args.append(i) for i in inspect.getargs(func.__code__).varargs or []]

    # remove self because we're not using it here
    allowed_args.remove("self")

    # remove doubled items if any
    allowed_args = list(set(allowed_args))

    return allowed_args


def get_classes_for_path(path: str, allowed_type: type) -> list:
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
