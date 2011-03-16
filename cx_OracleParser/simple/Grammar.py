"""Grammar for parsing SQL as defined by Oracle."""

GRAMMAR = """

  # tokens
  <DASHES> := '--'
  <WS> := [ \t\r\n] / comment
  <STRING_DELIM> := "'"
  <NAME_DELIM> := '"'
  <COMMENT_START> := '/*'
  <COMMENT_END> := '*/'
  <CR> := '\r\n' / '\n' / '\r'
  <SEMICOLON> := ';'
  <SIGN> := [+-]
  <DIGIT> := [0-9]
  <EXPONENT> := [Ee]
  <LETTER> := [A-Za-z]
  <PERIOD> := '.'
  <COMMA> := ','
  <SLASH> := '/'
  <AT> := '@'
  <CHAR> := [-A-Za-z0-9/*+=,.|()<>_:!%"@$#]
  <token> := literal / CHAR+ / WS+
  <LPAREN> := '('

  # object type keywords
  KW_bitmap := c"bitmap"
  KW_body := c"body"
  KW_check := c"check"
  KW_context := c"context"
  KW_foreign := c"foreign"
  KW_function := c"function"
  KW_global := c"global"
  KW_index := c"index"
  KW_key := c"key"
  KW_package := c"package"
  KW_primary := c"primary"
  KW_procedure := c"procedure"
  KW_public := c"public"
  KW_role := c"role"
  KW_sequence := c"sequence"
  KW_synonym := c"synonym"
  KW_table := c"table"
  KW_temporary := c"temporary"
  KW_trigger := c"trigger"
  KW_type := c"type"
  KW_unique := c"unique"
  KW_user := c"user"
  KW_view := c"view"
  KW_wrapped := c"wrapped"

  # keywords
  <KW_add> := c"add"
  <KW_alter> := c"alter"
  <KW_as> := c"as"
  <KW_begin> := c"begin"
  <KW_comment> := c"comment"
  <KW_commit> := c"commit"
  <KW_connect> := c"connect"
  <KW_constraint> := c"constraint"
  <KW_create> := c"create"
  <KW_declare> := c"declare"
  <KW_delete> := c"delete"
  <KW_drop> := c"drop"
  <KW_from> := c"from"
  <KW_grant> := c"grant"
  <KW_into> := c"into"
  <KW_insert> := c"insert"
  <KW_or> := c"or"
  <KW_rename> := c"rename"
  <KW_replace> := c"replace"
  <KW_revoke> := c"revoke"
  <KW_rollback> := c"rollback"
  <KW_truncate> := c"truncate"
  <KW_update> := c"update"

  # comments
  dash_comment := DASHES, -CR*, CR
  slash_comment := COMMENT_START, -COMMENT_END*, COMMENT_END
  comment := (dash_comment / slash_comment)

  # literals
  string_literal := (STRING_DELIM, -STRING_DELIM*, STRING_DELIM)+
  integer_literal := SIGN?, DIGIT+
  float_literal := SIGN?, DIGIT*, PERIOD?, DIGIT+, (EXPONENT, SIGN?, DIGIT+)?
  literal := (string_literal / float_literal / integer_literal)

  # identifiers
  unquoted_identifier := LETTER, [a-zA-Z0-9_$#-]*
  quoted_identifier := NAME_DELIM, [a-zA-Z0-9_$#.]+, NAME_DELIM
  >identifier< := quoted_identifier / unquoted_identifier
  qualified_identifier := identifier, (PERIOD, identifier)?

  # common clauses
  <simple_statement_ender> := token*, SEMICOLON
  <complex_statement_terminator> := CR, WS*, SLASH, (?-CR, WS)*, CR
  <complex_statement_ender> := (?-complex_statement_terminator,
        (token / SEMICOLON))*, complex_statement_terminator

  # object types
  >index_type< := ((KW_bitmap / KW_unique), WS+)?, KW_index
  >synonym_type< := (KW_public, WS+)?, KW_synonym
  >table_type< := (KW_global, WS+, KW_temporary, WS+)?, KW_table
  simple_object_type := KW_context / index_type / KW_role / KW_sequence /
      synonym_type / table_type / KW_user / KW_view
  complex_object_type := KW_function / (KW_package, (WS+, KW_body)?) /
      KW_procedure / KW_trigger / (KW_type, (WS+, KW_body)?)
  constraint_type := KW_check / (KW_foreign, WS+, KW_key) /
      (KW_primary, WS+, KW_key) / KW_unique
  >object_type< := simple_object_type / complex_object_type

  # statements
  anonymous_plsql_block := (KW_declare / KW_begin), complex_statement_ender
  comment_statement := KW_comment, simple_statement_ender
  commit_statement := KW_commit, simple_statement_ender
  connect_statement := KW_connect, WS+, identifier,
      (SLASH, identifier, (AT, identifier)?)?
  create_constraint_statement := KW_alter, WS+, KW_table, WS+,
      qualified_identifier, WS+, KW_add, WS+, KW_constraint, WS+,
      identifier, WS+, constraint_type, simple_statement_ender
  create_object_statement := KW_create, WS+, (KW_or, WS+, KW_replace, WS+)?,
      (simple_object_type, WS+, qualified_identifier, simple_statement_ender) /
      (complex_object_type, WS+, qualified_identifier, complex_statement_ender)
  alter_object_statement := KW_alter, WS+, object_type, WS+,
      qualified_identifier, simple_statement_ender
  delete_statement := KW_delete, WS+, (KW_from, WS+)?, qualified_identifier,
      simple_statement_ender
  drop_object_statement := KW_drop, WS+, object_type, WS+,
      qualified_identifier, simple_statement_ender
  grant_statement := KW_grant, simple_statement_ender
  insert_statement := KW_insert, WS+, KW_into, WS+, qualified_identifier,
      simple_statement_ender
  rename_statement := KW_rename, WS+, identifier, simple_statement_ender
  revoke_statement := KW_revoke, simple_statement_ender
  rollback_statement := KW_rollback, simple_statement_ender
  truncate_statement := KW_truncate, WS+, KW_table, WS+,
      qualified_identifier, simple_statement_ender
  update_statement := KW_update, WS+, (qualified_identifier / LPAREN),
      simple_statement_ender

  # all possible statements
  >sql_statement< := create_object_statement / create_constraint_statement /
      alter_object_statement / drop_object_statement / comment_statement /
      commit_statement / rollback_statement / grant_statement /
      revoke_statement / connect_statement / insert_statement /
      update_statement / delete_statement / rename_statement /
      truncate_statement / anonymous_plsql_block

  statement := WS*, sql_statement, WS*
  file := (WS*, sql_statement)*, WS*

"""

