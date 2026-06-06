# /// script
# requires-python = ">=3.9"
# dependencies = ["diagrams>=0.23"]
# ///
"""Find the exact import path and class name for diagrams library nodes.

Usage:
    uv run scripts/find-node.py <search-term> [<search-term> ...]

Case-insensitive substring match against every Node subclass in the diagrams
library. Prints a ready-to-paste import line for each match, so import paths
and class casing (Cronjob, Dynamodb, IOS) are never guessed.

Exit codes: 0 if every term matched at least one class, 1 otherwise.
"""
import importlib
import inspect
import os
import pkgutil
import sys

import diagrams
from diagrams import Node


def all_node_classes():
    """Enumerate (module, class_name) for every Node subclass in the library.

    Walks providers (diagrams.<provider>) one level deep to their category
    modules (diagrams.<provider>.<category>); the library nests exactly that
    deep, so a full recursive walk would only add import overhead.
    """
    base = os.path.dirname(diagrams.__file__)
    found = set()
    for provider in pkgutil.iter_modules([base]):
        if not provider.ispkg:
            continue
        provider_path = os.path.join(base, provider.name)
        for category in pkgutil.iter_modules([provider_path]):
            if category.ispkg:
                continue
            module_name = f"diagrams.{provider.name}.{category.name}"
            try:
                module = importlib.import_module(module_name)
            except Exception:
                # A single broken module (missing optional dep, upstream bug)
                # should not abort discovery across the other ~234 modules.
                continue
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if name.startswith("_"):
                    continue
                # __module__ check excludes classes re-exported via aliases,
                # which would print duplicate or misleading import paths.
                if issubclass(obj, Node) and obj.__module__ == module_name:
                    found.add((module_name, name))
    return sorted(found)


def main():
    terms = [t.lower() for t in sys.argv[1:]]
    if not terms:
        sys.exit(
            "Provide at least one search term.\n"
            "Usage: uv run scripts/find-node.py <term> [<term> ...]\n"
            "Example: uv run scripts/find-node.py sagemaker cronjob redis"
        )
    classes = all_node_classes()
    all_matched = True
    for term in terms:
        matches = [(m, n) for m, n in classes if term in n.lower()]
        print(f"=== '{term}': {len(matches)} match(es) ===")
        if not matches:
            all_matched = False
            print(
                "  No node class matches. Check spelling, or retry with a"
                " shorter/broader term (e.g. 'gateway', 'db')."
            )
            continue
        for module_name, class_name in matches:
            print(f"  from {module_name} import {class_name}")
    sys.exit(0 if all_matched else 1)


if __name__ == "__main__":
    main()
