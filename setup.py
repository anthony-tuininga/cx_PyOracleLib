"""Distutils script for cx_PyOracleLib.

To install:
    python setup.py install

"""

from distutils.core import setup

# NOTE: distutils does not currently support specifying both modules and
# packages so the submodules are specified independently; this can be
# eliminated in Python 2.3 and up
modules = [
        "cx_CursorCache",
        "cx_ExportData",
        "cx_ImportData",
        "cx_OracleDebugger",
        "cx_OracleEx",
        "cx_OracleObject.Describer",
        "cx_OracleObject.Environment",
        "cx_OracleObject.Object",
        "cx_OracleObject.Statements",
        "cx_OracleObject.Utils",
        "cx_OracleParser.Dependency",
        "cx_OracleParser.Grammar",
        "cx_OracleParser.Parser",
        "cx_OracleParser.Statements",
        "cx_OracleUtils",
        "cx_RecordSet",
        "cx_SQL"
]


setup(
        name = "cx_PyOracleLib",
        version = "2.4",
        description = "Set of Python modules for handling Oracle databases",
        licence = "See LICENSE.txt",
        long_description = "Set of Python modules for handling Oracle " + \
                "databases and used by a number of Computronix projects, " + \
                "in particular the cx_OracleTools project",
        author = "Anthony Tuininga",
        author_email = "anthony.tuininga@gmail.com",
        url = "http://starship.python.net/crew/atuining",
        py_modules = modules)

