"""Define statements for retrieving the data for each of the types."""

CONSTRAINTS = """
        select
          o.owner,
          o.constraint_name,
          o.constraint_type,
          o.table_name,
          o.search_condition,
          o.r_owner,
          o.r_constraint_name,
          o.delete_rule,
          o.deferred,
          o.deferrable
        from %(p_ViewPrefix)s_constraints o
        %(p_WhereClause)s
          and exists
            ( select 1
              from %(p_ViewPrefix)s_tables
              where owner = o.owner
                and table_name = o.table_name
            )
          and (o.generated = 'USER NAME' or o.constraint_type in ('P', 'U'))
        order by decode(o.constraint_type, 'P', 1, 'U', 2, 'R', 3, 'C', 4),
            o.owner, o.constraint_name"""

CONTEXTS = """
        select
          namespace,
          schema,
          package,
          type
        from dba_context o
        %(p_WhereClause)s
        order by namespace"""

INDEXES_ANY = """
        select
          o.owner,
          o.index_name,
          o.table_name,
          o.tablespace_name,
          o.uniqueness,
          o.initial_extent,
          o.next_extent,
          o.min_extents,
          o.max_extents,
          o.pct_increase,
          o.index_type,
          o.partitioned,
          o.temporary,
          o.compression,
          o.prefix_length,
          o.ityp_owner,
          o.ityp_name,
          o.parameters
        from %(p_ViewPrefix)s_indexes o
        %(p_WhereClause)s
          and o.index_type in ('NORMAL', 'NORMAL/REV', 'IOT - TOP', 'BITMAP',
              'FUNCTION-BASED NORMAL', 'FUNCTION-BASED NORMAL/REV',
              'DOMAIN')"""

INDEXES = INDEXES_ANY + """
        and not exists
          ( select 1
            from %(p_ViewPrefix)s_constraints
            where owner = o.owner
              and constraint_name = o.index_name
          )
        order by o.owner, o.index_name"""

INDEX_PARTITIONS = """
        select
          o.index_owner,
          o.partition_name,
          o.high_value,
          o.tablespace_name,
          o.initial_extent,
          o.next_extent,
          o.min_extent,
          o.max_extent,
          o.pct_increase
        from %(p_ViewPrefix)s_ind_partitions o
        %(p_WhereClause)s
        order by o.partition_position"""

LIBRARIES = """
        select
          o.owner,
          o.library_name,
          o.file_spec
        from %(p_ViewPrefix)s_libraries o
        %(p_WhereClause)s
        order by o.owner, o.library_name"""

LOBS = """
        select
          o.owner,
          o.column_name,
          o.table_name,
          o.segment_name,
          o.in_row
        from %(p_ViewPrefix)s_lobs o
        %(p_WhereClause)s
        order by o.column_name"""

ROLES = """
        select
          o.role,
          o.password_required
        from dba_roles o
        %(p_WhereClause)s
        order by o.role"""

SEQUENCES = """
        select
          o.sequence_owner,
          o.sequence_name,
          to_char(min_value),
          to_char(max_value),
          to_char(increment_by),
          cycle_flag,
          order_flag,
          to_char(cache_size),
          to_char(last_number)
        from %(p_ViewPrefix)s_sequences o
        %(p_WhereClause)s
        order by o.sequence_owner, o.sequence_name"""

SYNONYMS = """
        select
          o.owner,
          o.synonym_name,
          o.table_owner,
          o.table_name,
          o.db_link
        from %(p_ViewPrefix)s_synonyms o
        %(p_WhereClause)s
        order by decode(o.owner, 'PUBLIC', 0, 1), o.owner, o.synonym_name"""

TABLES = """
        select
          o.owner,
          o.table_name,
          o.tablespace_name,
          o.initial_extent,
          o.next_extent,
          o.min_extents,
          o.max_extents,
          o.pct_increase,
          o.temporary,
          o.partitioned,
          o.duration,
          o.iot_type
        from %(p_ViewPrefix)s_tables o
        %(p_WhereClause)s
          and secondary = 'N'
        order by o.owner, o.table_name"""

TABLE_PARTITIONS = """
        select
          o.table_owner,
          o.partition_name,
          o.high_value,
          o.tablespace_name,
          o.initial_extent,
          o.next_extent,
          o.min_extent,
          o.max_extent,
          o.pct_increase
        from %(p_ViewPrefix)s_tab_partitions o
        %(p_WhereClause)s
        order by o.partition_position"""

TRIGGERS = """
        select
          o.owner,
          o.trigger_name,
          o.table_name,
          o.description,
          o.when_clause,
          o.action_type,
          o.trigger_body
        from %(p_ViewPrefix)s_triggers o
        %(p_WhereClause)s
        order by o.owner, o.trigger_name"""

USERS = """
        select
          o.username,
          o.default_tablespace,
          o.temporary_tablespace
        from dba_users o
        %(p_WhereClause)s
        order by o.username"""

VIEWS = """
        select
          o.owner,
          o.view_name,
          o.text
        from %(p_ViewPrefix)s_views o
        %(p_WhereClause)s
        order by o.owner, o.view_name"""

