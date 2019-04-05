"""Distutils script for cx_PyOracleLib.

To install:
    python setup.py install

"""

from distutils.core import setup

modules = [
        "cx_ExportData",
        "cx_ImportData",
        "cx_OracleDebugger",
        "cx_OracleEx",
        "cx_OracleUtils",
        "cx_PatchCommands"
]

packages = [
        "cx_OracleObject",
        "cx_OracleParser",
        "cx_OracleParser.full",
        "cx_OracleParser.simple"
]


setup(
        name = "cx_PyOracleLib",
        version = "3.0",
        description = "Set of Python modules for handling Oracle databases",
        license = "See LICENSE.txt",
        long_description = "Set of Python modules for handling Oracle " + \
                "databases and used by a number of projects, " + \
                "in particular the cx_OracleTools project",
        author = "Anthony Tuininga",
        author_email = "anthony.tuininga@gmail.com",
        url = "https://github.com/anthony-tuininga/cx_PyOracleLib",
        py_modules = modules,
        packages = packages)

