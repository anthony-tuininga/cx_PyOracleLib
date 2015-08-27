"""Module for use in exporting data to a file."""

import cx_Logging
import cx_Oracle
import pickle
import sys

# define constant for pickle protocol
BINARY = 1

class Exporter:
    """Export data from a database in a cross platform manner."""

    def __init__(self, outFile, cursor, reportPoint, prefix = ""):
        self.outFile = outFile
        self.cursor = cursor
        self.cursor.numbersAsStrings = True
        self.reportPoint = reportPoint
        self.prefix = prefix

    def __ExportTableHeader(self, tableName):
        """Export the table header to the file."""
        cx_Logging.Trace("%sExporting table %s...", self.prefix, tableName)
        self.cursor.execute("select * from " + tableName)
        columns = [(r[0], self.__StringRepOfType(r[1], r[2])) \
                for r in self.cursor.description]
        pickle.dump(tableName, self.outFile, BINARY)
        pickle.dump(columns, self.outFile, BINARY)

    def __ExportTableRows(self, rowsToSkip, rowLimit):
        """Export the rows in the table to the file."""
        numRows = 0
        format = self.prefix + "  %d rows exported."
        cursor = self.cursor
        outFile = self.outFile
        reportPoint = self.reportPoint
        for row in cursor:
            numRows += 1
            if numRows > rowLimit:
                numRows -= 1
                break
            elif numRows > rowsToSkip:
                pickle.dump(row, outFile, BINARY)
            if reportPoint is not None and numRows % reportPoint == 0:
                cx_Logging.Trace(format, numRows)
        if reportPoint is None or numRows == 0 or numRows % reportPoint != 0:
            cx_Logging.Trace(format, numRows)
        pickle.dump(None, outFile, BINARY)

    def __StringRepOfType(self, dataType, displaySize):
        """Return the string representation of the type."""
        if dataType == cx_Oracle.NUMBER:
            return "STRING,%d" % displaySize
        for stringRep in ("BINARY", "STRING", "ROWID", "FIXED_CHAR", "NCHAR",
                "FIXED_NCHAR"):
            if getattr(cx_Oracle, stringRep) == dataType:
                return "%s,%d" % (stringRep, displaySize)
        for stringRep in ("BLOB", "CLOB", "NCLOB", "DATETIME", "LONG_BINARY",
                "LONG_STRING", "TIMESTAMP"):
            if getattr(cx_Oracle, stringRep) == dataType:
                return stringRep
        raise Exception("Unsupported type: %s!" % dataType)

    def ExportTable(self, tableName, rowsToSkip = None, rowLimit = None):
        """Export the data in the table to the file."""
        if rowsToSkip is None:
            rowsToSkip = 0
        if rowLimit is None:
            rowLimit = sys.maxsize
        self.__ExportTableHeader(tableName)
        self.__ExportTableRows(rowsToSkip, rowLimit)

    def FinalizeExport(self):
        """Finalize the export."""
        pickle.dump(None, self.outFile, BINARY)

    def TablesInSchema(self):
        """Return a list of tables found in the schema."""
        self.cursor.execute("""
                select table_name
                from user_tables
                where temporary = 'N'""")
        return [n for n, in self.cursor.fetchall()]

