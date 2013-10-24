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
  <RANGE> := '..'
  <OPERATOR_KEYWORDS> := ((KW_not, WS+)?, (KW_in / KW_between)) / KW_and /
      KW_or / KW_like / KW_escape / KW_mod
  <OPERATOR> := [+*/-] / '||' / '=' / '!=' / '<=' / '>=' / '<>' / '<' /
      '>' / ('(+)', WS*, '=') / (OPERATOR_KEYWORDS, WS+)
  <LPAREN> := '('
  <RPAREN> := ')'
  <PLSQL_EQ> := ':='
  <PLSQL_KW> := '=>'

  # keywords
  KW_access := c"access"
  KW_accessed := c"accessed"
  KW_add := c"add"
  KW_admin := c"admin"
  KW_administer := c"administer"
  KW_all := c"all"
  KW_alter := c"alter"
  KW_analyze := c"analyze"
  KW_and := c"and"
  KW_any := c"any"
  KW_as := c"as"
  KW_audit := c"audit"
  KW_authid := c"authid"
  KW_backup := c"backup"
  KW_become := c"become"
  KW_begin := c"begin"
  KW_between := c"between"
  KW_body := c"body"
  KW_bulk := c"bulk"
  KW_by := c"by"
  KW_byte := c"byte"
  KW_cache := c"cache"
  KW_cascade := c"cascade"
  KW_case := c"case"
  KW_cast := c"cast"
  KW_char := c"char"
  KW_check := c"check"
  KW_close := c"close"
  KW_cluster := c"cluster"
  KW_collect := c"collect"
  KW_comment := c"comment"
  KW_commit := c"commit"
  KW_connect := c"connect"
  KW_constant := c"constant"
  KW_constraint := c"constraint"
  KW_context := c"context"
  KW_cost := c"cost"
  KW_count := c"count"
  KW_create := c"create"
  KW_cross := c"cross"
  KW_current_user := c"current_user"
  KW_cursor := c"cursor"
  KW_database := c"database"
  KW_debug := c"debug"
  KW_declare := c"declare"
  KW_default := c"default"
  KW_deferred := c"deferred"
  KW_definer := c"definer"
  KW_delete := c"delete"
  KW_dictionary := c"dictionary"
  KW_dimension := c"dimension"
  KW_directory := c"directory"
  KW_disable := c"disable"
  KW_distinct := c"distinct"
  KW_drop := c"drop"
  KW_else := c"else"
  KW_elsif := c"elsif"
  KW_end := c"end"
  KW_errors := c"errors"
  KW_escape := c"escape"
  KW_exception := c"exception"
  KW_execute := c"execute"
  KW_exempt := c"exempt"
  KW_exists := c"exists"
  KW_exit := c"exit"
  KW_externally := c"externally"
  KW_fetch := c"fetch"
  KW_flashback := c"flashback"
  KW_for := c"for"
  KW_forall := c"forall"
  KW_force := c"force"
  KW_foreign := c"foreign"
  KW_from := c"from"
  KW_function := c"function"
  KW_global := c"global"
  KW_globally := c"globally"
  KW_grant := c"grant"
  KW_group := c"group"
  KW_having := c"having"
  KW_identified := c"identified"
  KW_if := c"if"
  KW_immediate := c"immediate"
  KW_in := c"in"
  KW_index := c"index"
  KW_indextype := c"indextype"
  KW_initialized := c"initialized"
  KW_initially := c"initially"
  KW_insert := c"insert"
  KW_instead := c"instead"
  KW_intersect := c"intersect"
  KW_into := c"into"
  KW_is := c"is"
  KW_join := c"join"
  KW_key := c"key"
  KW_left := c"left"
  KW_library := c"library"
  KW_like := c"like"
  KW_limit := c"limit"
  KW_link := c"link"
  KW_lob := c"lob"
  KW_lock := c"lock"
  KW_log := c"log"
  KW_loop := c"loop"
  KW_manage := c"manage"
  KW_matched := c"matched"
  KW_materialized := c"materialized"
  KW_merge := c"merge"
  KW_minus := c"minus"
  KW_mod := c"mod"
  KW_nocache := c"nocache"
  KW_nocopy := c"nocopy"
  KW_not := c"not"
  KW_null := c"null"
  KW_object := c"object"
  KW_of := c"of"
  KW_on := c"on"
  KW_open := c"open"
  KW_operator := c"operator"
  KW_option := c"option"
  KW_or := c"or"
  KW_order := c"order"
  KW_organization := c"organization"
  KW_out := c"out"
  KW_outer := c"outer"
  KW_outline := c"outline"
  KW_package := c"package"
  KW_pipe := c"pipe"
  KW_pipelined := c"pipelined"
  KW_policy := c"policy"
  KW_preserve := c"preserve"
  KW_pragma := c"pragma"
  KW_primary := c"primary"
  KW_prior := c"prior"
  KW_privilege := c"privilege"
  KW_privileges := c"privileges"
  KW_procedure := c"procedure"
  KW_profile := c"profile"
  KW_public := c"public"
  KW_query := c"query"
  KW_raise := c"raise"
  KW_range := c"range"
  KW_read := c"read"
  KW_record := c"record"
  KW_ref := c"ref"
  KW_references := c"references"
  KW_refresh := c"refresh"
  KW_reject := c"reject"
  KW_replace := c"replace"
  KW_resource := c"resource"
  KW_restricted := c"restricted"
  KW_resumable := c"resumable"
  KW_return := c"return"
  KW_returning := c"returning"
  KW_reverse := c"reverse"
  KW_revoke := c"revoke"
  KW_rewrite := c"rewrite"
  KW_role := c"role"
  KW_rollback := c"rollback"
  KW_row := c"row"
  KW_rows := c"rows"
  KW_segment := c"segment"
  KW_select := c"select"
  KW_sequence := c"sequence"
  KW_session := c"session"
  KW_set := c"set"
  KW_snapshot := c"snapshot"
  KW_start := c"start"
  KW_storage := c"storage"
  KW_store := c"store"
  KW_subtype := c"subtype"
  KW_synonym := c"synonym"
  KW_sysdba := c"sysdba"
  KW_sysoper := c"sysoper"
  KW_system := c"system"
  KW_table := c"table"
  KW_tablespace := c"tablespace"
  KW_temporary := c"temporary"
  KW_then := c"then"
  KW_to := c"to"
  KW_transaction := c"transaction"
  KW_trigger := c"trigger"
  KW_type := c"type"
  KW_under := c"under"
  KW_union := c"union"
  KW_unique := c"unique"
  KW_unlimited := c"unlimited"
  KW_update := c"update"
  KW_user := c"user"
  KW_using := c"using"
  KW_values := c"values"
  KW_view := c"view"
  KW_when := c"when"
  KW_where := c"where"
  KW_while := c"while"
  KW_with := c"with"
  KW_write := c"write"

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
  unquoted_identifier := COLON?, LETTER, [a-zA-Z0-9_$#]*
  quoted_identifier := NAME_DELIM, [a-zA-Z0-9_$#.]+, NAME_DELIM
  >identifier< := quoted_identifier / unquoted_identifier
  identifier_list := identifier, (WS*, COMMA, WS*, identifier)*
  identifier_modifier := ('%' / '@'), identifier
  qualified_identifier := identifier, (PERIOD, identifier)*,
      identifier_modifier?
  qualified_identifier_list := qualified_identifier,
      (WS*, COMMA, WS*, qualified_identifier)*

  # expressions
  prior_expression := (KW_prior, WS+)?, qualified_identifier
  count_expression := KW_count, WS*, LPAREN, WS*, '*', WS*, RPAREN
  function_expression := qualified_identifier, WS*,
      (LPAREN, WS*, expression_list?, WS*, RPAREN)+, (PERIOD, identifier)*
  case_clause := KW_when, WS+, expression, WS+, KW_then, WS+, expression
  case_header := KW_case, (WS+, ?-KW_when, expression)?
  case_expression := case_header, WS+, case_clause, (WS+, case_clause)*, WS+,
      (KW_else, WS+, expression, WS+)?, KW_end
  cast_expression := KW_cast, WS*, LPAREN, WS*, expression, WS+, KW_as, WS+,
      data_type, WS*, RPAREN
  paren_expression := LPAREN, WS*, expression, WS*, RPAREN
  exists_expression := KW_exists, WS+, subquery
  >simple_expression< := literal / count_expression / cast_expression /
      function_expression / paren_expression_list / paren_expression /
      case_expression / subquery / exists_expression / prior_expression
  unary_operator := (KW_not / SIGN), WS*
  post_operator := WS+, KW_is, WS+, (KW_not, WS+)?, KW_null
  expression := (identifier, WS*, PLSQL_KW, WS*)?, unary_operator?,
      simple_expression, post_operator?,
      (WS*, OPERATOR, WS*, unary_operator?, simple_expression, post_operator?)*
  expression_list := expression, (WS*, COMMA, WS*, expression)*
  paren_expression_list := LPAREN, WS*, expression_list, WS*, RPAREN

  # statement enders
  <simple_statement_ender> := WS*, SEMICOLON
  <complex_statement_ender> := simple_statement_ender, WS+, SLASH

  # select statement
  select_keyword := (KW_from / KW_bulk / KW_cross / KW_into / KW_union /
      KW_minus / KW_intersect / KW_left / KW_join / KW_where / KW_start /
      KW_on / KW_for / KW_group), WS+
  select_clause := expression, (WS+, ?-select_keyword, WS*, identifier)?
  select_clause_list := select_clause,
      (WS*, COMMA, WS*, select_clause)*
  >subquery< := LPAREN, WS*, select_statement, WS*, RPAREN
  table_cast_clause := KW_table, WS*, LPAREN, WS*, KW_cast, WS*, LPAREN, WS*,
      expression, WS+, KW_as, WS+, data_type, WS*, RPAREN, WS*, RPAREN
  table_clause := KW_table, WS*, LPAREN, WS*, expression, WS*, RPAREN
  from_clause := (table_cast_clause / table_clause / qualified_identifier /
      subquery), (WS+, ?-select_keyword, identifier)?
  join_type := (KW_left, WS+, KW_outer, WS+) / (KW_cross, WS+)
  join_clause := join_type?, KW_join, WS+, from_clause, (WS+, KW_on, WS+,
          expression)?
  table_ref := from_clause, (WS+, join_clause)*
  from_clause_list := table_ref, (WS*, COMMA, WS*, table_ref)*
  where_clause := KW_where, WS+, expression
  start_with_clause := KW_start, WS+, KW_with, WS+, expression,
      (WS+, KW_connect, WS+, KW_by, WS+, expression)?
  order_by_clause := KW_order, WS+, KW_by, WS+, select_clause_list
  group_by_clause := KW_group, WS+, KW_by, WS+, expression_list
  having_clause := KW_having, WS+, expression
  for_update_clause := KW_for, WS+, KW_update,
      (WS+, KW_of, WS+, identifier_list)?
  >select_modifier_clause< := start_with_clause / where_clause /
      for_update_clause / order_by_clause / group_by_clause / having_clause
  >simple_select_statement< := KW_select, WS+, (KW_distinct, WS+)?,
      ('*' / select_clause_list), WS+, KW_from, WS+, from_clause_list,
      (WS+, select_modifier_clause)*
  set_operation := (KW_union, (WS+, KW_all)?) / KW_minus / KW_intersect
  paren_select_statement := LPAREN, WS*, select_statement, WS*, RPAREN
  select_statement := simple_select_statement,
      ( WS+, set_operation, WS+,
          (simple_select_statement / paren_select_statement) )*

  # PL/SQL definitions
  >data_size_modifier< := WS+, (KW_char / KW_byte)
  >data_scale< := WS*, COMMA, WS*, integer_literal
  >data_size< := integer_literal, (data_scale / data_size_modifier)?
  data_type := qualified_identifier, (LPAREN, WS*, data_size, WS*, RPAREN)?
  argument := identifier, WS+, (KW_in, WS+)?, (KW_out, WS+)?,
      (KW_nocopy, WS+)?, data_type, (WS+, KW_default, WS+, expression)?,
      (WS*, PLSQL_EQ, WS*, expression)?
  argument_list := argument, (WS*, COMMA, WS*, argument)*
  common_definition := identifier,
      (WS*, LPAREN, WS*, argument_list, WS*, RPAREN)?
  procedure_definition := KW_procedure, WS+, common_definition
  procedure_body := WS+, (KW_is / KW_as), WS+, !,
      declaration_list?, WS*, basic_compound_statement, (WS+, identifier)?
  return_clause := KW_return, WS+, qualified_identifier
  function_definition := KW_function, WS+, common_definition, WS+,
      return_clause, (WS+, KW_pipelined)?
  cursor_definition := KW_cursor, WS+, common_definition, WS+,
      (KW_is / KW_as), WS+, select_statement
  range_clause := KW_range, WS+, integer_literal, PERIOD, PERIOD,
      integer_literal

  # PL/SQL declarations
  simple_declaration := ?-KW_begin, identifier, WS+, (KW_constant, WS+)?,
      data_type, (WS*, PLSQL_EQ, WS*, expression)?
  subtype_declaration := KW_subtype, WS+, identifier, WS+, KW_is, WS+,
      qualified_identifier, (WS+, range_clause)?
  record_item_list := simple_declaration,
      (WS*, COMMA, WS*, simple_declaration)*
  record_declaration := KW_type, WS+, identifier, WS+, KW_is, WS+,
      KW_record, WS*, LPAREN, WS*, record_item_list, WS*, RPAREN
  ref_cursor_declaration := KW_type, WS+, identifier, WS+, KW_is, WS+,
      KW_ref, WS+, KW_cursor, (WS+, KW_return, WS+, data_type)?
  index_by_clause := KW_index, WS+, KW_by, WS+, data_type
  array_declaration := KW_type, WS+, identifier, WS+, KW_is, WS+,
      KW_table, WS+, KW_of, WS+, data_type, (WS+, index_by_clause)?
  procedure_declaration := procedure_definition, procedure_body?
  function_declaration := function_definition, procedure_body?
  pragma_declaration := KW_pragma, WS+, identifier,
          (LPAREN, WS*, expression_list?, WS*, RPAREN)?
  declaration := (procedure_declaration / function_declaration /
      cursor_definition / subtype_declaration / record_declaration /
      array_declaration / ref_cursor_declaration / pragma_declaration /
      simple_declaration), WS*, SEMICOLON
  declaration_list := declaration, (WS+, ?-KW_end, declaration)*

  # PL/SQL control statements
  range_expression := expression, (WS*, RANGE, WS*, expression)?
  elsif_clause := KW_elsif, WS+, expression, WS+, KW_then, WS+,
      plsql_statement_list, WS+
  if_statement := KW_if, WS+, expression, WS+, KW_then, WS+,
      plsql_statement_list, WS+, elsif_clause*,
      (KW_else, WS+, plsql_statement_list, WS+)?, KW_end, WS+, KW_if,
      simple_statement_ender
  for_clause := identifier, WS+, KW_in, WS+, (KW_reverse, WS+)?,
      (subquery / range_expression)
  loop_statement := KW_loop, WS+, plsql_statement_list, WS+, KW_end, WS+,
      KW_loop, simple_statement_ender
  for_statement := KW_for, WS+, for_clause, WS+, KW_loop, WS+,
      plsql_statement_list, WS+, KW_end, WS+, KW_loop, simple_statement_ender
  forall_statement := KW_forall, WS+, identifier, WS+, KW_in, WS+,
      expression, WS*, RANGE, WS*, expression, WS+,
      (insert_statement / update_statement / delete_statement)
  while_statement := KW_while, WS+, expression, WS+, KW_loop, WS+,
      plsql_statement_list, WS+, KW_end, WS+, KW_loop, simple_statement_ender

  # PL/SQL assignment statements
  assignment_statement := expression, WS*, PLSQL_EQ, WS*, expression,
      simple_statement_ender
  into_clause := (KW_bulk, WS+, KW_collect, WS+)?, KW_into, WS+,
      expression_list
  select_into_statement := KW_select, WS+, (KW_distinct, WS+)?,
      ('*' / select_clause_list), WS+, into_clause, WS+, KW_from, WS+,
      from_clause_list, (WS+, select_modifier_clause)*
  plsql_select_statement := select_into_statement,
      (WS+, set_operation, WS+, select_statement)*, simple_statement_ender

  # PL/SQL compound statements
  declare_section := KW_declare, WS+, (declaration_list, WS+)?
  exception_clause := KW_when, WS+, expression, WS+, KW_then, WS+,
      plsql_statement_list
  exception_clause_list := exception_clause, (WS+, exception_clause)*
  exception_section := KW_exception, WS+, exception_clause_list, WS+
  basic_compound_statement := KW_begin, WS+, plsql_statement_list, WS+,
      exception_section?, KW_end
  compound_statement := declare_section?, basic_compound_statement

  # PL/SQL statements
  return_statement := KW_return, (WS+, expression)?, simple_statement_ender
  using_clause := (KW_out, WS+)?, expression
  using_clause_list := using_clause, (WS*, COMMA, WS*, using_clause)*
  execute_immediate_statement := KW_execute, WS+, KW_immediate, WS+,
      expression, (WS+, KW_using, WS+, using_clause_list)?,
      simple_statement_ender
  null_statement := KW_null, simple_statement_ender
  raise_statement := KW_raise, (WS+, qualified_identifier)?,
      simple_statement_ender
  close_statement := KW_close, WS+, identifier, simple_statement_ender
  fetch_statement := KW_fetch, WS+, identifier, WS+, into_clause,
      simple_statement_ender
  open_statement := KW_open, WS+, identifier, WS+, KW_for, WS+,
      select_statement, simple_statement_ender
  function_call := function_expression, simple_statement_ender
  procedure_call := ?-KW_end, qualified_identifier, simple_statement_ender
  block_statement := compound_statement, simple_statement_ender
  plsql_case_clause := KW_when, WS+, expression, WS+, KW_then, WS+,
        plsql_statement_list
  case_statement := case_header, WS+, plsql_case_clause,
        (WS+, plsql_case_clause)*, WS+,
        (KW_else, WS+, plsql_statement_list, WS+)?, KW_end, WS+, KW_case,
        simple_statement_ender
  pipe_statement := KW_pipe, WS+, expression, simple_statement_ender
  merge_update_clause := KW_when, WS+, KW_matched, WS+, KW_then, WS+,
        KW_update, WS+, KW_set, WS+, update_columns_clause_list,
        (WS+, where_clause)?, (WS+, KW_delete, WS+, where_clause)?
  merge_insert_clause := KW_when, WS+, KW_not, WS+, KW_matched, WS+,
        KW_then, WS+, KW_insert, WS+, columns_list?, values_clause,
        (WS*, where_clause)?
  merge_error_logging_clause := KW_log, WS+, KW_errors,
        (WS+, KW_into, WS+, qualified_identifier)?,
        (WS*, LPAREN, WS*, expression, WS*, RPAREN)?,
        (WS*, KW_reject, WS+, KW_limit, WS+, (KW_unlimited / integer_literal))?
  merge_header := KW_merge, WS+, KW_into, WS+, qualified_identifier, WS+,
        (?-KW_using, identifier, WS+)?, KW_using, WS+,
        (qualified_identifier / subquery), WS+, (?-KW_on, identifier, WS+)?,
        KW_on, WS*, LPAREN, WS*, expression, WS*, RPAREN
  merge_statement := merge_header, (WS*, merge_update_clause)?,
        (WS*, merge_insert_clause)?,
        (WS*, merge_error_logging_clause)?, simple_statement_ender
  plsql_statement := if_statement / for_statement / forall_statement /
      while_statement / loop_statement / plsql_select_statement /
      block_statement / return_statement / execute_immediate_statement /
      case_statement / pipe_statement / assignment_statement /
      insert_statement / update_statement / delete_statement /
      merge_statement / function_call / commit_statement / rollback_statement /
      exit_statement / raise_statement / null_statement / close_statement /
      fetch_statement / open_statement / procedure_call
  plsql_statement_list := plsql_statement, (WS+, plsql_statement)*

  # DML statements
  columns_list := LPAREN, WS*, qualified_identifier_list, WS*, RPAREN, WS*
  expression_columns_list := LPAREN, WS*, expression_list, WS*, RPAREN, WS*
  values_clause := KW_values, WS*,
      (paren_expression_list / qualified_identifier)
  update_columns_clause := qualified_identifier, WS*, '=', WS*, expression
  update_columns_clause_list := update_columns_clause,
      (WS*, COMMA, WS*, update_columns_clause)*
  returning_clause := WS+, KW_returning, WS+, expression_list, WS+, into_clause
  insert_statement := KW_insert, WS+, KW_into, WS+, qualified_identifier, WS+,
      columns_list?, (values_clause / select_statement), returning_clause?,
      simple_statement_ender
  update_statement := KW_update, WS+, qualified_identifier, WS+,
      (?-KW_set, identifier, WS+)?, KW_set, WS+, update_columns_clause_list,
      (WS+, where_clause)?, returning_clause?, simple_statement_ender
  delete_statement := KW_delete, WS+, (KW_from, WS+)?, qualified_identifier,
      (WS+, ?-KW_where, identifier)?, (WS+, where_clause)?,
      returning_clause?, simple_statement_ender
  standalone_select_statement := select_statement, simple_statement_ender

  # privilege manipulation statements
  privilege :=
     (KW_administer, WS+, KW_database, WS+, KW_trigger) /
     (KW_analyze, WS+, KW_any) /
     (KW_alter, WS+, KW_any, WS+, KW_cluster) /
     (KW_alter, WS+, KW_any, WS+, KW_dimension) /
     (KW_alter, WS+, KW_any, WS+, KW_index) /
     (KW_alter, WS+, KW_any, WS+, KW_indextype) /
     (KW_alter, WS+, KW_any, WS+, KW_materialized, WS+, KW_view) /
     (KW_alter, WS+, KW_any, WS+, KW_outline) /
     (KW_alter, WS+, KW_any, WS+, KW_procedure) /
     (KW_alter, WS+, KW_any, WS+, KW_role) /
     (KW_alter, WS+, KW_any, WS+, KW_sequence) /
     (KW_alter, WS+, KW_any, WS+, KW_table) /
     (KW_alter, WS+, KW_any, WS+, KW_trigger) /
     (KW_alter, WS+, KW_any, WS+, KW_type) /
     (KW_alter, WS+, KW_database) /
     (KW_alter, WS+, KW_profile) /
     (KW_alter, WS+, KW_resource, WS+, KW_cost) /
     (KW_alter, WS+, KW_rollback, WS+, KW_segment) /
     (KW_alter, WS+, KW_session) /
     (KW_alter, WS+, KW_system) /
     (KW_alter, WS+, KW_tablespace) /
     (KW_alter, WS+, KW_user) /
     (KW_audit, WS+, KW_any) /
     (KW_audit, WS+, KW_system) /
     (KW_backup, WS+, KW_any, WS+, KW_table) /
     (KW_become, WS+, KW_user) /
     (KW_comment, WS+, KW_any, WS+, KW_table) /
     (KW_create, WS+, KW_any, WS+, KW_cluster) /
     (KW_create, WS+, KW_any, WS+, KW_context) /
     (KW_create, WS+, KW_any, WS+, KW_dimension) /
     (KW_create, WS+, KW_any, WS+, KW_directory) /
     (KW_create, WS+, KW_any, WS+, KW_index) /
     (KW_create, WS+, KW_any, WS+, KW_indextype) /
     (KW_create, WS+, KW_any, WS+, KW_library) /
     (KW_create, WS+, KW_any, WS+, KW_materialized, WS+, KW_view) /
     (KW_create, WS+, KW_any, WS+, KW_operator) /
     (KW_create, WS+, KW_any, WS+, KW_outline) /
     (KW_create, WS+, KW_any, WS+, KW_procedure) /
     (KW_create, WS+, KW_any, WS+, KW_sequence) /
     (KW_create, WS+, KW_any, WS+, KW_synonym) /
     (KW_create, WS+, KW_any, WS+, KW_table) /
     (KW_create, WS+, KW_any, WS+, KW_trigger) /
     (KW_create, WS+, KW_any, WS+, KW_type) /
     (KW_create, WS+, KW_any, WS+, KW_view) /
     (KW_create, WS+, KW_cluster) /
     (KW_create, WS+, KW_database, WS+, KW_link) /
     (KW_create, WS+, KW_dimension) /
     (KW_create, WS+, KW_indextype) /
     (KW_create, WS+, KW_library) /
     (KW_create, WS+, KW_materialized, WS+, KW_view) /
     (KW_create, WS+, KW_operator) /
     (KW_create, WS+, KW_procedure) /
     (KW_create, WS+, KW_profile) /
     (KW_create, WS+, KW_public, WS+, KW_database, WS+, KW_link) /
     (KW_create, WS+, KW_public, WS+, KW_synonym) /
     (KW_create, WS+, KW_role) /
     (KW_create, WS+, KW_rollback, WS+, KW_segment) /
     (KW_create, WS+, KW_sequence) /
     (KW_create, WS+, KW_session) /
     (KW_create, WS+, KW_snapshot) /
     (KW_create, WS+, KW_synonym) /
     (KW_create, WS+, KW_tablespace) /
     (KW_create, WS+, KW_table) /
     (KW_create, WS+, KW_trigger) /
     (KW_create, WS+, KW_type) /
     (KW_create, WS+, KW_user) /
     (KW_create, WS+, KW_view) /
     (KW_debug, WS+, KW_any, WS+, KW_procedure) /
     (KW_debug, WS+, KW_connect, WS+, KW_session) /
     (KW_delete, WS+, KW_any, WS+, KW_table) /
     (KW_drop, WS+, KW_any, WS+, KW_cluster) /
     (KW_drop, WS+, KW_any, WS+, KW_context) /
     (KW_drop, WS+, KW_any, WS+, KW_dimension) /
     (KW_drop, WS+, KW_any, WS+, KW_directory) /
     (KW_drop, WS+, KW_any, WS+, KW_index) /
     (KW_drop, WS+, KW_any, WS+, KW_indextype) /
     (KW_drop, WS+, KW_any, WS+, KW_library) /
     (KW_drop, WS+, KW_any, WS+, KW_materialized, WS+, KW_view) /
     (KW_drop, WS+, KW_any, WS+, KW_operator) /
     (KW_drop, WS+, KW_any, WS+, KW_outline) /
     (KW_drop, WS+, KW_any, WS+, KW_procedure) /
     (KW_drop, WS+, KW_any, WS+, KW_role) /
     (KW_drop, WS+, KW_any, WS+, KW_sequence) /
     (KW_drop, WS+, KW_any, WS+, KW_synonym) /
     (KW_drop, WS+, KW_any, WS+, KW_table) /
     (KW_drop, WS+, KW_any, WS+, KW_trigger) /
     (KW_drop, WS+, KW_any, WS+, KW_type) /
     (KW_drop, WS+, KW_any, WS+, KW_view) /
     (KW_drop, WS+, KW_public, WS+, KW_database, WS+, KW_link) /
     (KW_drop, WS+, KW_public, WS+, KW_synonym) /
     (KW_drop, WS+, KW_profile) /
     (KW_drop, WS+, KW_rollback, WS+, KW_segment) /
     (KW_drop, WS+, KW_tablespace) /
     (KW_drop, WS+, KW_user) /
     (KW_execute, WS+, KW_any, WS+, KW_indextype) /
     (KW_execute, WS+, KW_any, WS+, KW_operator) /
     (KW_execute, WS+, KW_any, WS+, KW_procedure) /
     (KW_execute, WS+, KW_any, WS+, KW_type) /
     (KW_exempt, WS+, KW_access, WS+, KW_policy) /
     (KW_flashback, WS+, KW_any, WS+, KW_table) /
     (KW_force, WS+, KW_any, WS+, KW_transaction) /
     (KW_force, WS+, KW_transaction) /
     (KW_grant, WS+, KW_any, WS+, KW_object, WS+, KW_privileges) /
     (KW_grant, WS+, KW_any, WS+, KW_object, WS+, KW_privilege) /
     (KW_grant, WS+, KW_any, WS+, KW_privilege) /
     (KW_grant, WS+, KW_any, WS+, KW_role) /
     (KW_insert, WS+, KW_any, WS+, KW_table) /
     (KW_lock, WS+, KW_any, WS+, KW_table) /
     (KW_manage, WS+, KW_tablespace) /
     (KW_query, WS+, KW_rewrite) /
     (KW_global, WS+, KW_query, WS+, KW_rewrite) /
     (KW_on, WS+, KW_commit, WS+, KW_refresh) /
     (KW_restricted, WS+, KW_session) /
     KW_resumable /
     (KW_select, WS+, KW_any, WS+, KW_dictionary) /
     (KW_select, WS+, KW_any, WS+, KW_sequence) /
     (KW_select, WS+, KW_any, WS+, KW_table) /
     KW_sysdba /
     KW_sysoper /
     (KW_unlimited, WS+, KW_tablespace) /
     (KW_under, WS+, KW_any, WS+, KW_type) /
     (KW_under, WS+, KW_any, WS+, KW_view) /
     (KW_update, WS+, KW_any, WS+, KW_table) /
     KW_select / KW_insert / KW_update / KW_delete /
     KW_all / KW_alter / KW_debug / KW_execute / KW_flashback / KW_index /
     (KW_on, WS+, KW_commit, WS+, KW_refresh) /
     (KW_query, WS+, KW_rewrite) / KW_read / KW_references / KW_under /
     KW_write / identifier
  privilege_list := privilege, (WS*, COMMA, WS*, privilege)*
  grant_statement := KW_grant, WS+, privilege_list, WS+,
      (KW_on, WS+, qualified_identifier, WS+)?, KW_to, WS+, identifier_list,
      (WS*, KW_with, WS+, (KW_grant / KW_admin), WS+, KW_option, WS*)?,
      simple_statement_ender
  revoke_statement := KW_revoke, WS+, privilege_list, WS+,
      (KW_on, WS+, qualified_identifier, WS+)?, KW_from, WS+, identifier_list,
      simple_statement_ender

  # DDL statements
  create_or_replace_clause := KW_create, WS+, (KW_or, WS+, KW_replace, WS+)?
  create_view_statement := create_or_replace_clause, KW_view, WS+, !,
      identifier, WS+, KW_as, WS+, select_statement, simple_statement_ender
  commit_statement := KW_commit, simple_statement_ender
  rollback_statement := KW_rollback, simple_statement_ender
  exit_statement := KW_exit, (WS+, KW_when, WS+, expression)?,
      simple_statement_ender
  package_init_section := KW_begin, WS+, plsql_statement_list, WS+,
      exception_section?
  create_package_statement := create_or_replace_clause, KW_package, WS+, !,
      (KW_body, WS+)?, identifier, WS+,
      (KW_authid, WS+, (KW_current_user / KW_definer), WS+)?, (KW_is / KW_as),
      WS+, declaration_list, WS+, package_init_section?, KW_end,
      (WS+, identifier)?, complex_statement_ender
  column_clause := identifier, WS+, data_type,
      (WS+, KW_default, WS+, expression)?, (WS+, KW_not, WS+, KW_null)?
  column_clause_list := column_clause,
      (WS*, COMMA, WS*, (embedded_primary_key_constraint / column_clause))*
  global_temp_clause := KW_on, WS+, KW_commit, WS+, (KW_delete / KW_preserve),
      WS+, KW_rows
  storage_clause := (KW_tablespace, WS+, identifier) /
      (KW_disable, WS+, KW_storage, WS+, KW_in, WS+, KW_row) /
      (KW_organization, WS+, KW_index)
  lob_clause := KW_lob, WS*, LPAREN, WS*, identifier, WS*, RPAREN, WS*,
      KW_store, WS+, KW_as, WS*, LPAREN, (WS*, storage_clause)+, WS*, RPAREN
  initially_deferred_option := WS*, KW_initially, WS+, KW_deferred
  indexed_constraint_option := initially_deferred_option /
      (WS*, KW_using, WS+, KW_index, WS+, storage_clause)
  create_table_statement := KW_create, WS+,
      (KW_global, WS+, KW_temporary, WS+)?, KW_table, WS+, identifier, WS*,
      LPAREN, WS*, column_clause_list, WS*, RPAREN,
      (WS*, global_temp_clause / storage_clause / lob_clause)*,
      simple_statement_ender
  constraint_common_clause := KW_alter, WS+, KW_table, WS+, identifier, WS+,
      KW_add, WS+, KW_constraint, WS+, identifier, WS+
  primary_key_constraint := constraint_common_clause, KW_primary, WS+, KW_key,
      WS*, columns_list, indexed_constraint_option*, simple_statement_ender
  embedded_primary_key_constraint := KW_constraint, WS+, identifier, WS+,
      KW_primary, WS+, KW_key, WS+, columns_list, indexed_constraint_option*
  unique_constraint := constraint_common_clause, KW_unique, WS*, columns_list,
      indexed_constraint_option*, simple_statement_ender
  cascade_clause := KW_on, WS+, KW_delete, WS+,
      ( KW_cascade / (KW_set, WS+, KW_null))
  foreign_key_constraint := constraint_common_clause, KW_foreign, WS+, KW_key,
      WS*, columns_list, KW_references, WS+, qualified_identifier, WS*,
      columns_list, cascade_clause?, initially_deferred_option?,
      simple_statement_ender
  check_constraint := constraint_common_clause, KW_check, WS*, LPAREN, WS*,
      expression, WS*, RPAREN, initially_deferred_option?,
      simple_statement_ender
  create_index_statement := KW_create, WS+, (KW_unique, WS+)?, KW_index, WS+,
      identifier, WS+, KW_on, WS+, identifier, WS*, expression_columns_list,
      storage_clause*, simple_statement_ender
  create_sequence_statement := KW_create, WS+, KW_sequence, WS+, identifier,
      ((WS+, KW_cache, WS+, DIGIT+) / (WS+, KW_nocache))?,
      simple_statement_ender
  create_synonym_statement := KW_create, WS+, (KW_public, WS+)?, KW_synonym,
      WS+, identifier, WS+, KW_for, WS+, qualified_identifier,
      simple_statement_ender
  type_object := KW_object, WS*, LPAREN, WS*, column_clause_list, WS*, RPAREN
  type_list := KW_table, WS+, KW_of, WS+, data_type
  create_type_statement := create_or_replace_clause, KW_type, WS+, !,
      identifier, WS+, KW_as, WS+, (type_object / type_list),
      complex_statement_ender
  triggering_op := KW_insert / KW_update / KW_delete
  triggering_op_list := triggering_op, (WS+, KW_or, WS+, triggering_op)*
  create_trigger_statement := create_or_replace_clause, KW_trigger, WS+, !,
      identifier, WS+, KW_instead, WS+, KW_of, WS+, triggering_op_list, WS+,
      KW_on, WS+, identifier, WS+, compound_statement, complex_statement_ender
  default_tablespace_clause := KW_default, WS+, KW_tablespace, WS+, identifier
  temp_tablespace_clause := KW_temporary, WS+, KW_tablespace, WS+, identifier
  create_role_statement := KW_create, WS+, KW_role, WS+, identifier,
      (WS+, KW_identified, WS+, KW_by, WS+, identifier)?,
      simple_statement_ender
  create_user_statement := KW_create, WS+, KW_user, WS+, identifier, WS+,
      KW_identified, WS+, KW_by, WS+, identifier,
      (WS+, default_tablespace_clause)?, (WS+, temp_tablespace_clause)?,
      simple_statement_ender
  context_statement_accessed_option := KW_accessed, WS+, KW_globally
  context_statement_initialized_option := KW_initialized, WS+,
      (KW_externally / KW_globally)
  context_statement_option := context_statement_accessed_option /
      context_statement_initialized_option
  create_context_statement := create_or_replace_clause, KW_context, WS+,
      identifier, WS+, KW_using, WS+, qualified_identifier,
      (WS+, context_statement_option)?, simple_statement_ender
  create_procedure_statement := create_or_replace_clause, procedure_definition,
      procedure_body, complex_statement_ender
  create_function_statement := create_or_replace_clause, function_definition,
      procedure_body, complex_statement_ender

  # SQL statements
  >sql_statement< := insert_statement / update_statement / delete_statement /
      standalone_select_statement / create_table_statement /
      create_view_statement / primary_key_constraint / unique_constraint /
      foreign_key_constraint / check_constraint / create_index_statement /
      create_sequence_statement / revoke_statement / create_synonym_statement /
      grant_statement / commit_statement / rollback_statement /
      create_package_statement / create_user_statement /
      create_role_statement / create_type_statement /
      create_trigger_statement / create_context_statement /
      create_procedure_statement / create_function_statement

  # file
  file := (WS*, sql_statement)*, WS*

"""

