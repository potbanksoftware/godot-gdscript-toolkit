"""GDScript parser

By default, nothing is being printed on success and the exitcode is 0.
On failure, python exception is shown and exitcode is non-zero.

Usage:
  gdparse <file>... [options]

Options:
  -p --pretty   Print pretty parse tree
  -v --verbose  Print parse tree
  -h --help     Show this screen.
  --version     Show version.
"""
import sys
import pkg_resources

import lark
from docopt import docopt

from gdtoolkit.parser import parser
from gdtoolkit.common.exceptions import lark_unexpected_input_to_str


def main():
    arguments = docopt(
        __doc__,
        version="gdparse {}".format(
            pkg_resources.get_distribution("gdtoolkit").version
        ),
    )

    if not isinstance(arguments, dict):
        print(arguments)
        sys.exit(0)

    success = True
    files = arguments["<file>"]

    if files == ["-"]:
        file_content = sys.stdin.read()
        success = _parse_file_content(file_content, arguments)
    else:
        for file_path in arguments["<file>"]:
            success &= _parse_file(file_path, arguments)

    if not success:
        sys.exit(1)


def _parse_file(file_path, arguments):
    try:
        with open(file_path, "r") as fh:
            file_content = fh.read()
            return _parse_file_content(file_content, arguments, file_path)
    except OSError as e:
        print(
            "Cannot open file '{}': {}".format(file_path, e.strerror),
            file=sys.stderr,
        )
    return False


def _parse_file_content(content, arguments, file_path=None):
    actual_file_path = "STDIN" if file_path is None else file_path
    try:
        tree = parser.parse(content)  # TODO: handle exceptions
    except lark.exceptions.UnexpectedInput as e:
        print(
            f"{actual_file_path}:\n",
            lark_unexpected_input_to_str(e, content),
            sep="\n",
            file=sys.stderr,
        )
        return False
    if arguments["--pretty"]:
        print(tree.pretty())
    elif arguments["--verbose"]:
        print(tree)
    return True


if __name__ == "__main__":
    main()
