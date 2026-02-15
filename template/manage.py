#!/usr/bin/env python3
import argparse
import importlib
import inspect
import os
import pkgutil
import sys

from holo.commands.command import BaseCommand


if __name__ == "__main__":
    # Generic command runner for BaseCommand implementations.
    # Supports commands in module paths containing "commands".
    project_root = os.path.dirname(os.path.abspath(__file__))
    service_dir = os.path.join(project_root, "service")

    def find_commands_modules(package, print_commands=False, command_name=None):
        """
        Find all CLI command modules.
        """
        for finder, modname, ispkg in pkgutil.iter_modules([package]):
            path = os.path.join(finder.path, modname)
            if ispkg:
                # Recurse in sub package.
                module = find_commands_modules(path, print_commands=print_commands, command_name=command_name)
                if module:
                    return module
            elif "commands" in path.split(os.sep):
                # Split off the path before the root and change path into
                # dot-separated module string.
                path_from = len(project_root) + 1
                module = path.replace(os.sep, ".")[path_from:]
                if print_commands:
                    print(modname)
                elif command_name == modname:
                    return importlib.import_module(module)

    def split_args():
        """
        Split up argv into a list for this script and a list for the command.
        """
        manage_args, command_args = [], []
        found_positional_arg = False
        for arg in sys.argv[1:]:
            if not found_positional_arg:
                manage_args.append(arg)
                if not arg.startswith("-"):
                    # Found the first positional arg, the rest is for command.
                    found_positional_arg = True
            else:
                command_args.append(arg)
        return manage_args, command_args

    manage_args, command_args = split_args()
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", help="Run a command or omit to see all commands.")
    options = parser.parse_args(args=manage_args)

    if not options.command:
        print("Available commmands:\n")
        find_commands_modules(service_dir, print_commands=True)
    else:
        # Run the command.
        command_name = options.command

        command_module = find_commands_modules(service_dir, command_name=command_name)
        if not command_module:
            print(f'Command "{command_name}" not found')
            sys.exit(1)

        def _is_command_class(member):
            return (
                inspect.isclass(member)
                and issubclass(member, BaseCommand)
                # This is to skip imported BaseCommand classes.
                and member.__module__ == command_module.__name__
            )

        command_classes = [klass for name, klass in inspect.getmembers(command_module, _is_command_class)]

        if not command_classes:
            print(f'No class inheriting BaseCommand found in "{command_name}"')
            sys.exit(1)
        elif len(command_classes) > 1:
            print(f'Multiple classes inheriting BaseCommand found in "{command_name}": {command_classes}')
            sys.exit(1)

        command_class = command_classes[0]
        command_class.run_from_args(command_args)
