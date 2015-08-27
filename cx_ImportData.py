"""Defines class for importing data from an export file."""

import pickle
import cx_Logging
import cx_Oracle
import os
import sys

class Importer:
    """Handles importing data from the file."""

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.inFile = None
        self.reportPoint = None
        self.reportFunc = self.ReportProgress
        self.commitPoint = None

    def __iter__(self):
        return self

    def DataInTable(self):
        """Return a list of the data stored in the table."""
        rows = []
        while True:
            row = pickle.load(self.inFile)
            if row is None:
                break
            rows.append(row)
        return rows

    def ImportTable(self):
        """Import the data into the table and return the number of rows
           imported."""
        numRows = 0
        rowsToInsert = []
        while True:
            row = pickle.load(self.inFile)
            if row is None:
                break
            rowsToInsert.append(row)
            numRows += 1
            commit = (self.commitPoint is not None \
                    and numRows % self.commitPoint == 0)
            if commit or len(rowsToInsert) == self.cursor.arraysize:
                self.cursor.executemany(None, rowsToInsert)
                rowsToInsert = []
            if commit:
                self.connection.commit()
            if self.reportPoint and numRows % self.reportPoint == 0:
                self.reportFunc(numRows)
        if rowsToInsert:
            self.cursor.executemany(None, rowsToInsert)
        self.connection.commit()
        if not self.reportPoint or numRows == 0 \
                or numRows % self.reportPoint != 0:
            self.reportFunc(numRows)
        return numRows

    def __next__(self):
        """Return the next table name to process."""
        tableName = pickle.load(self.inFile)
        if tableName is None:
            raise StopIteration
        columnNames = []
        bindVarNames = []
        bindVars = []
        columns = pickle.load(self.inFile)
        for name, dataType in columns:
            dataSize = 0
            if "," in dataType:
                dataType, dataSize = dataType.split(",")
                dataSize = int(dataSize)
            dataType = getattr(cx_Oracle, dataType)
            columnNames.append(name)
            bindVars.append(self.cursor.var(dataType, dataSize))
            bindVarNames.append(":%s" % len(bindVars))
        sql = "insert into %s (%s) values (%s)" % \
                (tableName, ",".join(columnNames), ",".join(bindVarNames))
        self.cursor.prepare(sql)
        self.cursor.setinputsizes(*bindVars)
        return tableName, columnNames

    def OpenFile(self, fileName):
        """Open the file for importing."""
        if fileName == "-":
            self.inFile = sys.stdin
            self.inFileSize = None
        else:
            self.inFile = open(fileName, "rb")
            self.inFileSize = os.stat(fileName).st_size * 1.0

    def ReportProgress(self, numRows):
        """Report progress on the import."""
        if self.inFileSize is not None:
            percent = (self.inFile.tell() / self.inFileSize) * 100
            cx_Logging.Trace("  %d rows imported (%.0f%% of file).",
                    numRows, percent)
        else:
            cx_Logging.Trace("  %d rows imported.", numRows)

    def SkipTable(self):
        """Skip the import of the table."""
        while pickle.load(self.inFile):
            pass

