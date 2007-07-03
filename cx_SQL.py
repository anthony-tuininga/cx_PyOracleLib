#------------------------------------------------------------------------------
# cx_SQL.py
#   Module which contains routines for parsing SQL statements.
#------------------------------------------------------------------------------

from __future__ import generators

import cx_OracleUtils, os, sys, types

#------------------------------------------------------------------------------
# Statement
#   High level class for handling statements.
#------------------------------------------------------------------------------
class Statement:

  #----------------------------------------------------------------------------
  # Parse()
  #   Parse the statement from the input stream. Returns the number of lines
  # consumed.
  #----------------------------------------------------------------------------
  def Parse(self, a_FirstLine, a_Iterator):

    # without a terminator, the whole line is assumed to be the command
    if not self.i_Terminator:
      self.i_SQL = a_FirstLine.rstrip()
      return 0

    # otherwise, scan for the terminator
    v_Lines = []
    v_Line = a_FirstLine
    v_Offset = - len(self.i_Terminator)
    v_LinesConsumed = 0
    while 1:
      v_Line = v_Line.rstrip()
      if v_Line.endswith(self.i_Terminator):
        if self.i_Terminator != "/" or v_Line == self.i_Terminator:
          v_Line = v_Line[:v_Offset]
          if v_Line:
            v_Lines.append(v_Line)
          break
      v_Lines.append(v_Line)
      try:
        v_Line = a_Iterator.next()
        v_LinesConsumed += 1
      except StopIteration:
        raise "Unexpected end of stream parsing SQL statement."

    self.i_SQL = "\n".join(v_Lines)
    return v_LinesConsumed

  #----------------------------------------------------------------------------
  # Write()
  #   Write the SQL statement to the file.
  #----------------------------------------------------------------------------
  def Write(self, a_File):
    a_File.write(self.i_SQL)
    if self.i_Terminator:
      if self.i_Terminator == "/":
        a_File.write("\n")
      a_File.write(self.i_Terminator)
    a_File.write("\n\n")

  #----------------------------------------------------------------------------
  # SQL()
  #   Return the SQL statement as a string.
  #----------------------------------------------------------------------------
  def SQL(self):
    if self.i_Terminator == "/":
      return self.i_SQL + "\n" + self.i_Terminator + "\n\n"
    return self.i_SQL + self.i_Terminator + "\n\n"

  #----------------------------------------------------------------------------
  # LineNo()
  #   Return the line number for the statement.
  #----------------------------------------------------------------------------
  def LineNo(self):
    return self.i_LineNo

  #----------------------------------------------------------------------------
  # Process()
  #   Default method for processing a statement.
  #----------------------------------------------------------------------------
  def Process(self, a_Connection, a_Cursor):
    pass

  #----------------------------------------------------------------------------
  # LogMessage()
  #   Default method for returning a log message.
  #----------------------------------------------------------------------------
  def LogMessage(self):
    return None

#------------------------------------------------------------------------------
# CommentStatement
#   Statement for handling comments.
#------------------------------------------------------------------------------
class CommentStatement(Statement):

  #----------------------------------------------------------------------------
  # __init__()
  #   Constructor.
  #----------------------------------------------------------------------------
  def __init__(self, a_LineNo):
    self.i_LineNo = a_LineNo
    self.i_Terminator = "*/"

#------------------------------------------------------------------------------
# CommitStatement
#   Statement for handling commits.
#------------------------------------------------------------------------------
class CommitStatement(Statement):

  #----------------------------------------------------------------------------
  # __init__()
  #   Constructor.
  #----------------------------------------------------------------------------
  def __init__(self, a_LineNo):
    self.i_LineNo = a_LineNo
    self.i_Terminator = ";"

  #----------------------------------------------------------------------------
  # Process()
  #   Process the statement.
  #----------------------------------------------------------------------------
  def Process(self, a_Connection, a_Cursor):
    a_Connection.commit()

  #----------------------------------------------------------------------------
  # LogMessage()
  #   Return a message for logging.
  #----------------------------------------------------------------------------
  def LogMessage(self):
    return "Commit point reached."

#------------------------------------------------------------------------------
# RollbackStatement
#   Statement for handling rollbacks.
#------------------------------------------------------------------------------
class RollbackStatement(Statement):

  #----------------------------------------------------------------------------
  # __init__()
  #   Constructor.
  #----------------------------------------------------------------------------
  def __init__(self, a_LineNo):
    self.i_LineNo = a_LineNo
    self.i_Terminator = ";"

  #----------------------------------------------------------------------------
  # Process()
  #   Process the statement.
  #----------------------------------------------------------------------------
  def Process(self, a_Connection, a_Cursor):
    a_Connection.rollback()

  #----------------------------------------------------------------------------
  # LogMessage()
  #   Return a message for logging.
  #----------------------------------------------------------------------------
  def LogMessage(self):
    return "Rolled back."

#------------------------------------------------------------------------------
# ExitStatement
#   Statement for handling exits.
#------------------------------------------------------------------------------
class ExitStatement(Statement):

  #----------------------------------------------------------------------------
  # __init__()
  #   Constructor.
  #----------------------------------------------------------------------------
  def __init__(self, a_LineNo):
    self.i_LineNo = a_LineNo
    self.i_Terminator = None

#------------------------------------------------------------------------------
# ConnectStatement
#   Statement for handling connects.
#------------------------------------------------------------------------------
class ConnectStatement(Statement):

  #----------------------------------------------------------------------------
  # __init__()
  #   Constructor.
  #----------------------------------------------------------------------------
  def __init__(self, a_LineNo):
    self.i_LineNo = a_LineNo
    self.i_Terminator = None

  #----------------------------------------------------------------------------
  # Process()
  #   Process the statement.
  #----------------------------------------------------------------------------
  def Process(self, a_Connection, a_Cursor):
    raise "Unable to process connect statements at this time."

  #----------------------------------------------------------------------------
  # ArgumentValue()
  #   Returns the argument value for the connect statement.
  #----------------------------------------------------------------------------
  def ArgumentValue(self):
    return self.i_SQL.strip().lower().split()[1]

  #----------------------------------------------------------------------------
  # LogMessage()
  #   Return a message for logging.
  #----------------------------------------------------------------------------
  def LogMessage(self):
    return "Connected to %s" % self.ArgumentValue()

#------------------------------------------------------------------------------
# PLSQLBlock
#   Statement for handling anonymous PL/SQL blocks.
#------------------------------------------------------------------------------
class PLSQLBlock(Statement):

  #----------------------------------------------------------------------------
  # __init__()
  #   Constructor.
  #----------------------------------------------------------------------------
  def __init__(self, a_LineNo):
    self.i_LineNo = a_LineNo
    self.i_Terminator = "/"

  #----------------------------------------------------------------------------
  # Process()
  #   Process the statement.
  #----------------------------------------------------------------------------
  def Process(self, a_Connection, a_Cursor):
    a_Cursor.execute(self.i_SQL)

  #----------------------------------------------------------------------------
  # LogMessage()
  #   Return a message for logging.
  #----------------------------------------------------------------------------
  def LogMessage(self):
    return "PL/SQL procedure successfully completed."

#------------------------------------------------------------------------------
# DDLStatement
#   Statement for handling DDL statements.
#------------------------------------------------------------------------------
class DDLStatement(Statement):

  #----------------------------------------------------------------------------
  # ObjectType()
  #   Returns the type of the object affected.
  #----------------------------------------------------------------------------
  def ObjectType(self):
    return self.i_ObjectType

  #----------------------------------------------------------------------------
  # ObjectName()
  #   Returns the name of the object affected.
  #----------------------------------------------------------------------------
  def ObjectName(self):
    return self.i_ObjectName

  #----------------------------------------------------------------------------
  # GetObjectTypeAndName()
  #   Get the object type and name.
  #----------------------------------------------------------------------------
  def GetObjectTypeAndName(self, a_Line):
    v_Words = a_Line.lower().split()
    if v_Words[1] == "or":
      del v_Words[1:3]
    if v_Words[1] in ("public", "unique", "database", "bitmap"):
      self.i_ObjectType = v_Words[1] + " " + v_Words[2]
      self.i_ObjectName = v_Words[3]
    elif v_Words[1] == "global":
      self.i_ObjectType = v_Words[1] + " " + v_Words[2] + " " + v_Words[3]
      self.i_ObjectName = v_Words[4]
    elif v_Words[1] in ("package", "type") and v_Words[2] == "body":
      self.i_ObjectType = v_Words[1] + " " + v_Words[2]
      self.i_ObjectName = v_Words[3]
    else:
      self.i_ObjectType = v_Words[1]
      self.i_ObjectName = v_Words[2]
    self.i_ObjectName = self.i_ObjectName.replace("(", "")
    if self.i_ObjectName[-1] == ";":
      self.i_ObjectName = self.i_ObjectName[:-1]

  #----------------------------------------------------------------------------
  # FindTablespace()
  #   Find the tablespace keyword in the SQL and return the index into the
  # string and length of the tablespace name which follows the keyword. If the
  # keyword cannot be located, -1 is returned.
  #----------------------------------------------------------------------------
  def FindTablespace(self, a_SQL):
    v_Pos = 0
    v_LastPos = 0
    v_InToken = v_InString = 0
    v_FoundTablespace = 0
    for v_Char in a_SQL:
      if v_InToken and v_Char in (" ", "\n", "\t"):
        v_InToken = 0
        if v_FoundTablespace:
          return (v_LastPos, a_SQL[v_LastPos:v_Pos])
        if a_SQL[v_LastPos:v_Pos].lower() == "tablespace":
          v_FoundTablespace = 1
      elif v_Char == "'":
        v_InToken = 0
        v_InString = not v_InString
      elif not v_InString and not v_InToken:
        v_InToken = 1
        v_LastPos = v_Pos
      v_Pos += 1
    if v_InToken and v_FoundTablespace:
      return (v_LastPos, a_SQL[v_LastPos:])
    return (-1, "")

  #----------------------------------------------------------------------------
  # ModifyForUpgrade()
  #   Modify the SQL that is executed during an upgrade. This adds the clause
  # novalidate on to check constraints and foreign keys and adds the nologging
  # clause on to all create statements for indexes and tables. It also will
  # modify the names of the tablespaces in which the table or index is to be
  # built, if desired. The first occurrence of the tablespace keyword will be
  # replaced with the primary tablespace and all other occurrences will be
  # replaced with the secondary tablespace. Nothing will be done if the
  # tablespace values are None.
  #----------------------------------------------------------------------------
  def ModifyForUpgrade(self, a_PrimaryTablespace, a_SecondaryTablespace):

    # add the novalidate clause, if applicable
    if self.i_ObjectType in ("foreign key", "check constraint"):
      self.i_SQL += " novalidate"
      return (None, None)

    # otherwise, only statements affecting tables and indexes are relevant
    if self.i_ObjectType not in ("table", "index", "unique index",
        "bitmap index", "primary key", "unique constraint"):
      return (None, None)

    # parse the statement for the tablespace keyword
    v_SQL = self.i_SQL
    self.i_SQL = ""
    v_PrimaryTablespace = v_SecondaryTablespace = None
    v_NewTablespaceName = a_PrimaryTablespace
    v_AddNoLogging = 1
    while 1:
      v_StartPos, v_TablespaceName = self.FindTablespace(v_SQL)
      if v_StartPos < 0:
        break
      if v_NewTablespaceName is None:
        v_NewTablespaceName = v_TablespaceName
      if not v_PrimaryTablespace:
        v_PrimaryTablespace = v_TablespaceName
      else:
        v_SecondaryTablespace = v_TablespaceName
      if v_AddNoLogging:
        v_NewTablespaceName += " nologging"
      self.i_SQL += v_SQL[:v_StartPos] + v_NewTablespaceName
      v_SQL = v_SQL[v_StartPos + len(v_TablespaceName):]
      v_NewTablespaceName = a_SecondaryTablespace
      v_AddNoLogging = 0
    self.i_SQL += v_SQL
    return (v_PrimaryTablespace, v_SecondaryTablespace)
  
  #----------------------------------------------------------------------------
  # Process()
  #   Process the statement.
  #----------------------------------------------------------------------------
  def Process(self, a_Connection, a_Cursor):
    a_Cursor.execute(self.i_SQL)
    if self.i_Terminator == "/":
      v_ObjectName = self.i_ObjectName
      if "." in self.i_ObjectName:
        v_ObjectName = self.i_ObjectName.split(".")[1]
      v_Cursor = cx_OracleUtils.PrepareErrorsCursor(a_Connection, "all")
      cx_OracleUtils.CheckForErrors(v_Cursor, a_Connection.username.upper(),
          v_ObjectName.upper(), self.i_ObjectType.upper(),
          self.i_Action + " with", self.i_LineNo - 1)

  #----------------------------------------------------------------------------
  # LogMessage()
  #   Return a message for logging.
  #----------------------------------------------------------------------------
  def LogMessage(self):
    return "%s %s %s." % (self.i_ObjectType.capitalize(), \
        self.i_ObjectName.upper(), self.i_Action)

#------------------------------------------------------------------------------
# GrantStatement
#   Statement for handling granting privilegs.
#------------------------------------------------------------------------------
class GrantStatement(DDLStatement):

  #----------------------------------------------------------------------------
  # __init__()
  #   Constructor.
  #----------------------------------------------------------------------------
  def __init__(self, a_LineNo):
    self.i_LineNo = a_LineNo
    self.i_Terminator = ";"
    self.i_ObjectType = self.i_ObjectName = None

  #----------------------------------------------------------------------------
  # LogMessage()
  #   Return a message for logging.
  #----------------------------------------------------------------------------
  def LogMessage(self):
    return "Privilege(s) granted."

#------------------------------------------------------------------------------
# CommentObjectStatement
#   Statement for handling granting privilegs.
#------------------------------------------------------------------------------
class CommentObjectStatement(DDLStatement):

  #----------------------------------------------------------------------------
  # __init__()
  #   Constructor.
  #----------------------------------------------------------------------------
  def __init__(self, a_LineNo):
    self.i_LineNo = a_LineNo
    self.i_Terminator = ";"
    self.i_ObjectType = self.i_ObjectName = None

  #----------------------------------------------------------------------------
  # LogMessage()
  #   Return a message for logging.
  #----------------------------------------------------------------------------
  def LogMessage(self):
    return "Comment created."

#------------------------------------------------------------------------------
# RevokeStatement
#   Statement for handling revoking privilegs.
#------------------------------------------------------------------------------
class RevokeStatement(DDLStatement):

  #----------------------------------------------------------------------------
  # __init__()
  #   Constructor.
  #----------------------------------------------------------------------------
  def __init__(self, a_LineNo):
    self.i_LineNo = a_LineNo
    self.i_Terminator = ";"
    self.i_ObjectType = self.i_ObjectName = None

  #----------------------------------------------------------------------------
  # LogMessage()
  #   Return a message for logging.
  #----------------------------------------------------------------------------
  def LogMessage(self):
    return "Privilege(s) revoked."

#------------------------------------------------------------------------------
# CreateStatement
#   Statement for handling the creation of database objects.
#------------------------------------------------------------------------------
class CreateStatement(DDLStatement):

  #----------------------------------------------------------------------------
  # __init__()
  #   Constructor.
  #----------------------------------------------------------------------------
  def __init__(self, a_LineNo, a_Line):
    self.i_LineNo = a_LineNo
    self.i_Terminator = ";"
    self.i_Action = "created"
    self.GetObjectTypeAndName(a_Line)
    if self.i_ObjectType in ("package", "package body", "type", "type body", \
        "trigger", "procedure", "function"):
      self.i_Terminator = "/"

#------------------------------------------------------------------------------
# AlterStatement
#   Statement for handling the alteration of database objects.
#------------------------------------------------------------------------------
class AlterStatement(DDLStatement):

  #----------------------------------------------------------------------------
  # __init__()
  #   Constructor.
  #----------------------------------------------------------------------------
  def __init__(self, a_LineNo, a_Line):
    self.i_LineNo = a_LineNo
    self.i_Terminator = ";"
    self.i_Action = "altered"
    self.GetObjectTypeAndName(a_Line)

  #----------------------------------------------------------------------------
  # GetConstraintTypeAndName()
  #   Parses the SQL to determine the constraint type and name. Note that only
  # alter table statements contain the constraint clause.
  #----------------------------------------------------------------------------
  def GetConstraintTypeAndName(self):
    self.i_ConstraintType = self.i_ConstraintName = None
    if self.i_ObjectType == "table":
      v_Words = self.i_SQL.lower().split()
      if len(v_Words) > 4 and v_Words[4] == "constraint":
        self.i_ObjectName = v_Words[5]
        if v_Words[3] == "add":
          self.i_Action = "created"
          if v_Words[7] == "key":
            self.i_ObjectType = v_Words[6] + " key"
          else:
            self.i_ObjectType = v_Words[6] + " constraint"
        else:
          if v_Words[3] == "enable":
            self.i_Action = "enabled"
          elif v_Words[3] == "disable":
            self.i_Action = "disabled"
          elif v_Words[3] == "modify":
            self.i_Action = "modified"
          else:
            self.i_Action = "dropped"
          self.i_ObjectType = "constraint"

#------------------------------------------------------------------------------
# DropStatement
#   Statement for handling the dropping of database objects.
#------------------------------------------------------------------------------
class DropStatement(DDLStatement):

  #----------------------------------------------------------------------------
  # __init__()
  #   Constructor.
  #----------------------------------------------------------------------------
  def __init__(self, a_LineNo, a_Line):
    self.i_LineNo = a_LineNo
    self.i_Terminator = ";"
    self.i_Action = "dropped"
    self.GetObjectTypeAndName(a_Line)

#------------------------------------------------------------------------------
# RenameStatement
#   Statement for handling the renaming of database objects.
#------------------------------------------------------------------------------
class RenameStatement(DDLStatement):

  #----------------------------------------------------------------------------
  # __init__()
  #   Constructor.
  #----------------------------------------------------------------------------
  def __init__(self, a_LineNo, a_Line):
    self.i_LineNo = a_LineNo
    self.i_Terminator = ";"
    self.i_Action = "renamed"
    self.i_ObjectType = "object"
    v_Words = a_Line.lower().split()
    self.i_ObjectName = v_Words[1]

#------------------------------------------------------------------------------
# TruncateStatement
#   Statement for handling the truncation of database objects.
#------------------------------------------------------------------------------
class TruncateStatement(DDLStatement):

  #----------------------------------------------------------------------------
  # __init__()
  #   Constructor.
  #----------------------------------------------------------------------------
  def __init__(self, a_LineNo, a_Line):
    self.i_LineNo = a_LineNo
    self.i_Terminator = ";"
    self.i_Action = "truncated"
    self.GetObjectTypeAndName(a_Line)

#------------------------------------------------------------------------------
# DMLStatement
#   Statement for handling DML statements.
#------------------------------------------------------------------------------
class DMLStatement(Statement):

  #----------------------------------------------------------------------------
  # Process()
  #   Process the statement.
  #----------------------------------------------------------------------------
  def Process(self, a_Connection, a_Cursor):
    self.i_RowsAffected = 0
    a_Cursor.execute(self.i_SQL)
    self.i_RowsAffected = a_Cursor.rowcount

  #----------------------------------------------------------------------------
  # LogMessage()
  #   Return a message for logging.
  #----------------------------------------------------------------------------
  def LogMessage(self):
    return "%s %d row(s) in %s." % (self.i_Action.capitalize(), \
        self.i_RowsAffected, self.i_ObjectName.upper())

#------------------------------------------------------------------------------
# InsertStatement
#   Statement for handling the insertion of rows.
#------------------------------------------------------------------------------
class InsertStatement(DMLStatement):

  #----------------------------------------------------------------------------
  # __init__()
  #   Constructor.
  #----------------------------------------------------------------------------
  def __init__(self, a_LineNo, a_Line):
    self.i_LineNo = a_LineNo
    self.i_Terminator = ";"
    self.i_Action = "inserted"
    self.GetObjectName(a_Line)

  #----------------------------------------------------------------------------
  # GetObjectName()
  #   Get the object name.
  #----------------------------------------------------------------------------
  def GetObjectName(self, a_Line):
    v_Words = a_Line.lower().split()
    self.i_ObjectName = v_Words[v_Words.index("into") + 1]

#------------------------------------------------------------------------------
# UpdateStatement
#   Statement for handling the updating of rows.
#------------------------------------------------------------------------------
class UpdateStatement(DMLStatement):

  #----------------------------------------------------------------------------
  # __init__()
  #   Constructor.
  #----------------------------------------------------------------------------
  def __init__(self, a_LineNo, a_Line):
    self.i_LineNo = a_LineNo
    self.i_Terminator = ";"
    self.i_Action = "updated"
    self.i_ObjectName = a_Line.lower().split()[1]

#------------------------------------------------------------------------------
# DeleteStatement
#   Statement for handling the deletion of rows.
#------------------------------------------------------------------------------
class DeleteStatement(DMLStatement):

  #----------------------------------------------------------------------------
  # __init__()
  #   Constructor.
  #----------------------------------------------------------------------------
  def __init__(self, a_LineNo, a_Line):
    self.i_LineNo = a_LineNo
    self.i_Terminator = ";"
    self.i_Action = "deleted"
    self.GetObjectName(a_Line)

  #----------------------------------------------------------------------------
  # GetObjectName()
  #   Get the object name.
  #----------------------------------------------------------------------------
  def GetObjectName(self, a_Line):
    v_Words = a_Line.lower().split()
    if v_Words[1] == "from":
      self.i_ObjectName = v_Words[2]
    else:
      self.i_ObjectName = v_Words[1]

#------------------------------------------------------------------------------
# ChooseStatementClass
#   Chooses a statement class from the list of possible classes given the first
# line of the statement.
#------------------------------------------------------------------------------
def ChooseStatementClass(a_LineNo, a_Line):

  # handle simple cases
  if a_Line[:2] == "/*":
    return CommentStatement(a_LineNo)
  elif a_Line == "commit;":
    return CommitStatement(a_LineNo)
  elif a_Line == "rollback;":
    return RollbackStatement(a_LineNo)
  elif a_Line == "exit":
    return ExitStatement(a_LineNo)

  # otherwise, base the statement on the first word of the line
  v_Word = a_Line.split()[0].lower()
  if v_Word == "connect":
    return ConnectStatement(a_LineNo)
  elif v_Word in ("declare", "begin"):
    return PLSQLBlock(a_LineNo)
  elif v_Word == "comment":
    return CommentObjectStatement(a_LineNo)
  elif v_Word == "grant":
    return GrantStatement(a_LineNo)
  elif v_Word == "revoke":
    return RevokeStatement(a_LineNo)
  elif v_Word == "create":
    return CreateStatement(a_LineNo, a_Line)
  elif v_Word == "alter":
    return AlterStatement(a_LineNo, a_Line)
  elif v_Word == "drop":
    return DropStatement(a_LineNo, a_Line)
  elif v_Word == "rename":
    return RenameStatement(a_LineNo, a_Line)
  elif v_Word == "truncate":
    return TruncateStatement(a_LineNo, a_Line)
  elif v_Word == "insert":
    return InsertStatement(a_LineNo, a_Line)
  elif v_Word == "update":
    return UpdateStatement(a_LineNo, a_Line)
  elif v_Word == "delete":
    return DeleteStatement(a_LineNo, a_Line)

  # otherwise, we don't know anything about this type of statement
  raise "Unknown statement at line %d: %s" % (a_LineNo, a_Line)

#------------------------------------------------------------------------------
# ParseStatements()
#   Parse statements from the iterator.
#------------------------------------------------------------------------------
def ParseStatements(a_Iterator):
  v_LineNo = 0
  while 1:
    v_Line = a_Iterator.next()
    v_LineNo += 1
    v_StrippedLine = v_Line.strip()
    if not v_StrippedLine:
      continue
    elif v_StrippedLine[:2] == "--":
      continue
    v_Statement = ChooseStatementClass(v_LineNo, v_StrippedLine)
    v_LineNo += v_Statement.Parse(v_Line, a_Iterator)
    yield v_Statement

#------------------------------------------------------------------------------
# ParseStatementsInFile()
#   Parse statements found in a file.
#------------------------------------------------------------------------------
def ParseStatementsInFile(a_FileOrName):
  v_File = a_FileOrName
  if type(a_FileOrName) == types.StringType:
    if a_FileOrName == "-":
      v_File = sys.stdin
    elif os.path.isfile(a_FileOrName):
      v_File = open(a_FileOrName)
    elif a_FileOrName[-4:].lower() != ".sql":
      v_File = open(a_FileOrName + ".sql")
    else:
      v_File = open(a_FileOrName)
  return ParseStatements(iter(v_File))

