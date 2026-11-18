"""Shared by the measures of the pet shop and of its children: load the work,
run each scenario, print the number. A scenario passes if it raises nothing."""
import importlib.util
import json
import sys
import traceback
from pathlib import Path

SCENARIOS = []


def scenario(function):
    SCENARIOS.append(function)
    return function


def load(unit_dir, name):
    path = Path(unit_dir).resolve() / "work" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"{name}_under_measure", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def refuses(error, function, *args, **kwargs):
    """The call must raise `error` (ValueError: not valid; LookupError: not found)."""
    try:
        function(*args, **kwargs)
    except error:
        return
    except Exception as other:
        raise AssertionError(f"raised {other!r}, not {error.__name__}")
    raise AssertionError(f"accepted what it must refuse: {args} {kwargs}")


def through_json(state):
    return json.loads(json.dumps(state))


def main(name, expected):
    """Run every scenario against the unit in sys.argv[1]. `expected` is the
    number of scenarios, so that a measure that lost some does not pass."""
    failed = []
    try:
        module = load(sys.argv[1], name)
    except Exception:
        module, failed = None, [f"the work could not be loaded: {traceback.format_exc(limit=1).splitlines()[-1]}"]
    passed = 0
    if module:
        for function in SCENARIOS:
            try:
                function(module)
                passed += 1
            except Exception as error:
                failed.append(f"{function.__doc__ or function.__name__}: {error!r}"[:300])
    ok = module is not None and passed == len(SCENARIOS) == expected
    print(json.dumps({"pass": ok, "passed": passed, "total": expected, "failed": failed}, indent=1))
    sys.exit(0 if ok else 1)
