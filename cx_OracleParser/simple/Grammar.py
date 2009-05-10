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
  <SLASH> := '/'
  <CHAR> := [-A-Za-z0-9/*+=,.|()_]
  <token> := literal / CHAR+ / WS+

  # keywords
  <KW_alter> := c"alter"
  <KW_as> := c"as"
  <KW_body> := c"body"
  <KW_commit> := c"commit"
  <KW_context> := c"context"
  <KW_create> := c"create"
  <KW_delete> := c"delete"
  <KW_global> := c"global"
  <KW_grant> := c"grant"
  <KW_index> := c"index"
  <KW_insert> := c"insert"
  <KW_or> := c"or"
  <KW_package> := c"package"
  <KW_public> := c"public"
  <KW_replace> := c"replace"
  <KW_revoke> := c"revoke"
  <KW_role> := c"role"
  <KW_rollback> := c"rollback"
  <KW_sequence> := c"sequence"
  <KW_synonym> := c"synonym"
  <KW_table> := c"table"
  <KW_temporary> := c"temporary"
  <KW_trigger> := c"trigger"
  <KW_type> := c"type"
  <KW_unique> := c"unique"
  <KW_update> := c"update"
  <KW_user> := c"user"
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
  <simple_statement_ender> := token*, SEMICOLON
  <complex_statement_terminator> := WS+, SLASH
  <complex_statement_ender> := simple_statement_ender,
      (?-complex_statement_terminator, simple_statement_ender)*,
      complex_statement_terminator

  # statement
  create_context_statement := KW_create, WS+, KW_context, WS+, identifier,
      simple_statement_ender
  create_index_statement := KW_create, WS+, (KW_unique, WS+)?, KW_index, WS+,
      qualified_identifier, simple_statement_ender
  create_package_statement := create_or_replace_clause, KW_package, WS+,
      qualified_identifier, complex_statement_ender
  create_package_body_statement := create_or_replace_clause, KW_package, WS+,
      KW_body, WS+, qualified_identifier, complex_statement_ender
  create_public_synonym_statement := KW_create, WS+, KW_public, WS+,
      KW_synonym, WS+, identifier, simple_statement_ender
  create_role_statement := KW_create, WS+, KW_role, WS+, identifier,
      simple_statement_ender
  create_sequence_statement := KW_create, WS+, KW_sequence, WS+,
      qualified_identifier, simple_statement_ender
  create_synonym_statement := KW_create, WS+, KW_synonym, WS+,
      qualified_identifier, simple_statement_ender
  create_table_statement := KW_create, WS+,
      (KW_global, WS+, KW_temporary, WS+)?, KW_table, WS+,
      qualified_identifier, simple_statement_ender
  create_trigger_statement := create_or_replace_clause, KW_trigger, WS+,
      qualified_identifier, complex_statement_ender
  create_type_statement := create_or_replace_clause, KW_type, WS+,
      qualified_identifier, complex_statement_ender
  create_type_body_statement := create_or_replace_clause, KW_type, WS+,
      KW_body, WS+, qualified_identifier, complex_statement_ender
  create_user_statement := KW_create, WS+, KW_user, WS+, identifier,
      simple_statement_ender
  create_view_statement := create_or_replace_clause, KW_view, WS+,
      qualified_identifier, WS+, KW_as, simple_statement_ender
  grant_statement := KW_grant, simple_statement_ender
  revoke_statement := KW_revoke, simple_statement_ender

  # SQL statements
  insert_statement := KW_insert
  update_statement := KW_update
  delete_statement := KW_delete
  primary_key_constraint := KW_alter
  unique_constraint := KW_alter
  foreign_key_constraint := KW_alter
  check_constraint := KW_alter
  commit_statement := KW_commit
  rollback_statement := KW_commit

  # SQL statements
  >sql_statement< := insert_statement / update_statement / delete_statement /
      create_table_statement / create_view_statement / primary_key_constraint /
      unique_constraint / foreign_key_constraint / check_constraint /
      create_index_statement / create_sequence_statement / revoke_statement /
      create_public_synonym_statement / create_synonym_statement /
      grant_statement / commit_statement / rollback_statement /
      create_package_body_statement / create_package_statement /
      create_user_statement / create_role_statement /
      create_type_body_statement / create_type_statement /
      create_trigger_statement / create_context_statement

  file := (WS*, sql_statement)*, WS*

"""

