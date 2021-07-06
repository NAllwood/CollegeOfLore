import functools
import inspect
from typing import Dict, Any


# TODO: Do not use a single global var to store context
GLOBAL_SCOPE: Dict[str, Any] = {}


def get(key):
    return GLOBAL_SCOPE[key]


def inject(fn):
    """decorator

    must be the inner-most decorator to correctly inspect the function"""
    arg_spec = inspect.getfullargspec(fn)
    default_cut_off = len(arg_spec.args)
    if arg_spec.defaults:
        default_cut_off -= len(arg_spec.defaults)

    kwonlydefaults = set()
    if arg_spec.kwonlydefaults:
        kwonlydefaults.update(arg_spec.kwonlydefaults)

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        # possible injection
        missing_args = set(arg_spec.args[len(args):default_cut_off])
        missing_args.update(arg_spec.kwonlyargs)

        for key in set(missing_args):
            if key in kwargs:
                # do not overwrite kwargs from functin call
                continue

            if key in kwonlydefaults:
                # do not overwrite defaults
                continue

            if key not in GLOBAL_SCOPE:
                # we will run into an error later
                # pretty sure about that :]
                continue

            kwargs[key] = get(key)

        return fn(*args, **kwargs)

    return wrapper
