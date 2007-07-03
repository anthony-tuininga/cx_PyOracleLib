#------------------------------------------------------------------------------
# cx_RecordSet.py
#   Module which provides record set processing.
#------------------------------------------------------------------------------

class RecordSet:

  # attributes for defining record sets for COM on Win32
  _public_methods_ = ["RecordCount", "MoveFirst", "MoveNext", "Value",
      "Fields", "Labels", "DumpAsXML"]
  _reg_progid_ = "Computronix.RecordSet"
  _reg_verprogid_ = "Computronix.RecordSet.1"
  _reg_desc_ = "Computronix RecordSet"
  _reg_clsid_ = "{6DAD12D1-FD23-11D4-98DA-00500418115C}"

  #----------------------------------------------------------------------------
  # __init__()
  #   Constructor.
  #----------------------------------------------------------------------------
  def __init__(self, a_Cursor = None, a_SQL = None, a_Fields = None,
      **a_BindVars):
    self.i_Rows = []
    if a_Cursor:
      a_Cursor.execute(a_SQL, **a_BindVars)
      self.i_Rows = a_Cursor.fetchall()
      if not a_Fields:
        a_Fields = [x[0] for x in a_Cursor.description]
    if a_Fields:
      self.SetFields(a_Fields)
      self.i_Labels = self.i_Names
    self.i_RowNum = 0
    self.i_Indexes = {}

  #----------------------------------------------------------------------------
  # AppendRows()
  #   Append the rows to the record set. Note that we assume the structure is
  # the same.
  #----------------------------------------------------------------------------
  def AppendRows(self, a_Rows):
    self.i_Rows += a_Rows
    for v_Index in self.i_Indexes.values():
      v_Index.AppendRows(a_Rows)

  #----------------------------------------------------------------------------
  # SetFields()
  #   Set the names of the parameters.
  #----------------------------------------------------------------------------
  def SetFields(self, a_Names):
    self.i_Names = a_Names
    self.i_ParamsByName = {}
    for v_Name in self.i_Names:
      self.i_ParamsByName[v_Name.upper()] = len(self.i_ParamsByName)

  #----------------------------------------------------------------------------
  # SetLabels()
  #   Set the labels of the parameters.
  #----------------------------------------------------------------------------
  def SetLabels(self, a_Labels):
    self.i_Labels = a_Labels

  #----------------------------------------------------------------------------
  # RecordCount()
  #   Returns the number of records.
  #----------------------------------------------------------------------------
  def RecordCount(self):
    return len(self.i_Rows)

  #----------------------------------------------------------------------------
  # MoveFirst()
  #   Moves the internal pointer to the first row.
  #----------------------------------------------------------------------------
  def MoveFirst(self):
    self.i_RowNum = 0

  #----------------------------------------------------------------------------
  # MoveNext()
  #   Moves the internal pointer to the next row.
  #----------------------------------------------------------------------------
  def MoveNext(self):
    self.i_RowNum += 1

  #----------------------------------------------------------------------------
  # MoveToRow()
  #   Moves the internal pointer to the specified row.
  #----------------------------------------------------------------------------
  def MoveToRow(self, a_RowNum):
    self.i_RowNum = a_RowNum

  #----------------------------------------------------------------------------
  # ValueForRow()
  #   Returns the value for the named column on the given row.
  #----------------------------------------------------------------------------
  def ValueForRow(self, a_Row, a_Name):
    if type(a_Row) == type(()):
      return a_Row[self.i_ParamsByName[a_Name.upper()]]
    return self.i_Rows[a_Row][self.i_ParamsByName[a_Name.upper()]]

  #----------------------------------------------------------------------------
  # Value()
  #   Returns the value for the named column on the current row.
  #----------------------------------------------------------------------------
  def Value(self, a_Name):
    return self.ValueForRow(self.i_RowNum, a_Name)

  #----------------------------------------------------------------------------
  # Index()
  #   Create an index on the given fields and return the index object.
  #----------------------------------------------------------------------------
  def Index(self, a_Name, *a_ColumnNames):
    self.i_Indexes[a_Name] = RecordSetIndex(self, *a_ColumnNames)
    self.i_Indexes[a_Name].AppendRows(self.i_Rows)

  #----------------------------------------------------------------------------
  # FindRow()
  #   Find the row given the index name and key values and position the current
  # row pointer on that row. An error will be raised if the number of rows is
  # not exactly one.
  #----------------------------------------------------------------------------
  def FindRow(self, a_Name, *a_Values):
    self.i_RowNum, = self.FindRows(a_Name, *a_Values)

  #----------------------------------------------------------------------------
  # FindRows()
  #   Return the row number(s) given the index name and key values.
  #----------------------------------------------------------------------------
  def FindRows(self, a_Name, *a_Values):
    return self.i_Indexes[a_Name].FindRows(*a_Values)

  #----------------------------------------------------------------------------
  # Rows()
  #   Returns the rows in the record set.
  #----------------------------------------------------------------------------
  def Rows(self, a_IndexName = None):
    if not a_IndexName:
      return self.i_Rows
    v_Index = self.i_Indexes[a_IndexName].i_Index
    v_Keys = v_Index.keys()
    v_Keys.sort()
    return [v_Row for v_Key in v_Keys for v_Row in v_Index[v_Key]]

  #----------------------------------------------------------------------------
  # Fields()
  #   Returns the names of the fields in the record set.
  #----------------------------------------------------------------------------
  def Fields(self):
    return self.i_Names

  #----------------------------------------------------------------------------
  # Labels()
  #   Returns the labels of the fields in the record set.
  #----------------------------------------------------------------------------
  def Labels(self):
    return self.i_Labels

  #----------------------------------------------------------------------------
  # CurrentRowNum()
  #   Returns the current row number.
  #----------------------------------------------------------------------------
  def CurrentRowNum(self):
    return self.i_RowNum

  #----------------------------------------------------------------------------
  # DumpAsHTML()
  #   Dump the record set contents as HTML.
  #----------------------------------------------------------------------------
  def DumpAsHTML(self, a_Title):
    v_HTML = a_Title + " <BR> <table border=1>\n<tr>\n"
    for v_Name in self.i_Names:
      v_HTML += "  <th> " + v_Name + " </th>\n"
    v_HTML += "</tr>\n"
    for v_Row in self.i_Rows:
      v_HTML += "<tr>\n"
      for v_Name in self.i_Names:
        v_HTML += "  <td> " + str(self.ValueForRow(v_Row, v_Name)) + " </td>\n"
      v_HTML += "</tr>\n"
    return v_HTML + "</table>"

  #----------------------------------------------------------------------------
  # DumpAsXML()
  #   Dump the record set contents as XML.
  #----------------------------------------------------------------------------
  def DumpAsXML(self, a_MainTag, a_RowTag):
    import cgi
    v_XML = "<" + a_MainTag + ">\n"
    for v_Row in self.i_Rows:
      v_XML += "  <" + a_RowTag + ">\n"
      for v_Name in self.i_Names:
        v_Value = self.ValueForRow(v_Row, v_Name)
        if v_Value == None:
          v_Value = ""
        else:
          v_Value = cgi.escape(str(v_Value))
        v_XML += "    <" + v_Name + ">" + v_Value + "</" + v_Name + ">\n"
      v_XML += "  </" + a_RowTag + ">\n"
    v_XML += "</" + a_MainTag + ">\n"
    return v_XML

#------------------------------------------------------------------------------
# RecordSetIndex
#   Class which contains an index into the rows of a particular record set.
#------------------------------------------------------------------------------
class RecordSetIndex:

  #----------------------------------------------------------------------------
  # __init__()
  #   Constructor.
  #----------------------------------------------------------------------------
  def __init__(self, a_RecordSet, *a_Names):
    self.i_Index = {}
    self.i_Params = [a_RecordSet.i_ParamsByName[s.upper()] for s in a_Names]

  #----------------------------------------------------------------------------
  # AppendRows()
  #   Append the rows to the index.
  #----------------------------------------------------------------------------
  def AppendRows(self, a_Rows):
    v_RowNum = 0
    for v_Row in a_Rows:
      v_Key = tuple([v_Row[i] for i in self.i_Params])
      if not self.i_Index.has_key(v_Key):
        self.i_Index[v_Key] = []
      self.i_Index[v_Key].append(v_RowNum)
      v_RowNum += 1

  #----------------------------------------------------------------------------
  # FindRows()
  #   Return the row number(s) given the key values.
  #----------------------------------------------------------------------------
  def FindRows(self, *a_Values):
    return self.i_Index.get(a_Values, [])

