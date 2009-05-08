"""Grammar for parsing SQL as defined by Oracle."""

GRAMMAR = """

  # tokens
  <DASHES> := '--'
  <WS> := [ \t\n] / comment
  <STRING_DELIM> := "'"
  <NAME_DELIM> := '"'
  <COMMENT_START> := '/*'
  <COMMENT_END> := '*/'
  <CR> := '\n'
  <SEMICOLON> := ';'
  <SIGN> := [+-]
  <DIGIT> := [0-9]
  <EXPONENT> := [Ee]
  <LETTER> := [A-Za-z]
  <PERIOD> := '.'
  <COLON> := ':'
  <COMMA> := ','
  <CHAR> := [-A-Za-z0-9/*+=,.|()_]
  <token> := literal / CHAR+ / WS+

  # keywords
  <KW_alter> := c"alter"
  <KW_as> := c"as"
  <KW_commit> := c"commit"
  <KW_create> := c"create"
  <KW_delete> := c"delete"
  <KW_global> := c"global"
  <KW_grant> := c"grant"
  <KW_insert> := c"insert"
  <KW_or> := c"or"
  <KW_replace> := c"replace"
  <KW_revoke> := c"replace"
  <KW_rollback> := c"rollback"
  <KW_table> := c"table"
  <KW_temporary> := c"temporary"
  <KW_update> := c"update"
  <KW_view> := c"view"

  # comments
  dash_comment := DASHES, -CR+, CR
  slash_comment := COMMENT_START, -COMMENT_END*, COMMENT_END
  comment := (dash_comment / slash_comment)

  # literals
  string_literal := (STRING_DELIM, -STRING_DELIM*, STRING_DELIM)+
  integer_literal := SIGN?, DIGIT+
  float_literal := SIGN?, DIGIT*, PERIOD?, DIGIT+, (EXPONENT, SIGN?, DIGIT+)?
  literal := (string_literal / float_literal / integer_literal)

  # identifiers
  unquoted_identifier := COLON?, LETTER, [a-zA-Z0-9_$#]*
  quoted_identifier := NAME_DELIM, [a-zA-Z0-9_$#.]+, NAME_DELIM
  >identifier< := quoted_identifier / unquoted_identifier
  qualified_identifier := identifier, (PERIOD, identifier)?

  # common clauses
  <create_or_replace_clause> := KW_create, WS+, (KW_or, WS+, KW_replace, WS+)?
  <simple_statement_ender> := token+, SEMICOLON

  # statement
  create_table_statement := KW_create, WS+,
      (KW_global, WS+, KW_temporary, WS+)?, KW_table, WS+,
      qualified_identifier, simple_statement_ender
  create_view_statement := create_or_replace_clause, KW_view, WS+,
      qualified_identifier, WS+, KW_as, simple_statement_ender
  grant_statement := KW_grant, simple_statement_ender

  # SQL statements
  insert_statement := KW_insert
  update_statement := KW_update
  delete_statement := KW_delete
  primary_key_constraint := KW_alter
  unique_constraint := KW_alter
  foreign_key_constraint := KW_alter
  check_constraint := KW_alter
  create_index_statement := KW_create
  create_sequence_statement := KW_create
  revoke_statement := KW_revoke
  create_synonym_statement := KW_create
  commit_statement := KW_commit
  rollback_statement := KW_commit
  create_package_statement := KW_create
  create_user_statement := KW_create
  create_role_statement := KW_create
  create_type_statement := KW_create
  create_trigger_statement := KW_create
  create_context_statement := KW_create

  # SQL statements
  >sql_statement< := insert_statement / update_statement / delete_statement /
      create_table_statement / create_view_statement / primary_key_constraint /
      unique_constraint / foreign_key_constraint / check_constraint /
      create_index_statement / create_sequence_statement / revoke_statement /
      create_synonym_statement / grant_statement / commit_statement /
      rollback_statement / create_package_statement / create_user_statement /
      create_role_statement / create_type_statement /
      create_trigger_statement / create_context_statement

  file := (WS*, sql_statement)*, WS*

"""

