#------------------------------------------------------------------------------
# cx_CursorCache.py
#   Defines simple class for caching cursors.
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# CursorCache
#   Class for caching cursors.
#------------------------------------------------------------------------------
class CursorCache:

  #----------------------------------------------------------------------------
  # __init__()
  #   Constructor.
  #----------------------------------------------------------------------------
  def __init__(self, a_Connection):
    self.i_Connection = a_Connection
    self.i_Cursors = {}

  #----------------------------------------------------------------------------
  # Cursor()
  #   Returns a cursor which is subsequently cached for better performance.
  #----------------------------------------------------------------------------
  def Cursor(self, a_Tag = None):
    v_IsPrepared = v_Cursor = self.i_Cursors.get(a_Tag)
    if not v_Cursor:
      v_Cursor = self.i_Connection.cursor()
      v_Cursor.arraysize = 25
      if a_Tag:
        self.i_Cursors[a_Tag] = v_Cursor
    return v_Cursor, v_IsPrepared

