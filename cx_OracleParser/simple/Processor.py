"""Module for processing dependencies in SQL."""

import cx_Parser

import Statements

__all__ = [ "Processor" ]

class Processor(cx_Parser.DispatchProcessor):
    CommentStatement = Statements.CommentStatement
    CommitStatement = Statements.CommitStatement
    ConnectStatement = Statements.ConnectStatement
    CreateCheckConstraintStatement = Statements.CreateCheckConstraintStatement
    CreateForeignKeyStatement = Statements.CreateForeignKeyStatement
    CreateIndexStatement = Statements.CreateIndexStatement
    CreatePackageStatement = Statements.CreatePackageStatement
    CreatePackageBodyStatement = Statements.CreatePackageBodyStatement
    CreatePrimaryKeyStatement = Statements.CreatePrimaryKeyStatement
    CreatePublicSynonymStatement = Statements.CreatePublicSynonymStatement
    CreateRoleStatement = Statements.CreateRoleStatement
    CreateSequenceStatement = Statements.CreateSequenceStatement
    CreateSynonymStatement = Statements.CreateSynonymStatement
    CreateTableStatement = Statements.CreateTableStatement
    CreateTriggerStatement = Statements.CreateTriggerStatement
    CreateTypeStatement = Statements.CreateTypeStatement
    CreateTypeBodyStatement = Statements.CreateTypeBodyStatement
    CreateUniqueConstraintStatement = \
            Statements.CreateUniqueConstraintStatement
    CreateUserStatement = Statements.CreateUserStatement
    CreateViewStatement = Statements.CreateViewStatement
    GrantStatement = Statements.GrantStatement
    DeleteStatement = Statements.DeleteStatement
    InsertStatement = Statements.InsertStatement
    RevokeStatement = Statements.RevokeStatement
    RollbackStatement = Statements.RollbackStatement
    UpdateStatement = Statements.UpdateStatement

    def __init__(self, initialOwner = None):
        self.owner = initialOwner

    def _ConstraintStatement(self, cls, sql, start, end, children):
        owner, tableName = self.Dispatch(sql, children[0])
        name = self.Dispatch(sql, children[1])
        return cls(sql[start:end], owner, name)

    def check_constraint(self, sql, tag, start, end, children):
        return self._ConstraintStatement(self.CreateCheckConstraintStatement,
                sql, start, end, children)

    def comment_statement(self, sql, tag, start, end, children):
        return self.CommentStatement(sql[start:end])

    def commit_statement(self, sql, tag, start, end, children):
        return self.CommitStatement(sql[start:end])

    def connect_statement(self, sql, tag, start, end, children):
        parts = self.DispatchList(sql, children)
        return self.ConnectStatement(*parts)

    def create_index_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.CreateIndexStatement(sql[start:end], owner, name)

    def create_package_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.CreatePackageStatement(sql[start:end], owner, name)

    def create_package_body_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.CreatePackageBodyStatement(sql[start:end], owner, name)

    def create_public_synonym_statement(self, sql, tag, start, end, children):
        name = self.Dispatch(sql, children[0])
        return self.CreatePublicSynonymStatement(sql[start:end], name)

    def create_role_statement(self, sql, tag, start, end, children):
        name = self.Dispatch(sql, children[0])
        return self.CreateRoleStatement(sql[start:end], name)

    def create_sequence_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.CreateSequenceStatement(sql[start:end], owner, name)

    def create_synonym_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.CreateSynonymStatement(sql[start:end], owner, name)

    def create_table_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.CreateTableStatement(sql[start:end], owner, name)

    def create_trigger_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.CreateTriggerStatement(sql[start:end], owner, name)

    def create_type_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.CreateTypeStatement(sql[start:end], owner, name)

    def create_type_body_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.CreateTypeBodyStatement(sql[start:end], owner, name)

    def create_user_statement(self, sql, tag, start, end, children):
        name = self.Dispatch(sql, children[0])
        return self.CreateUserStatement(sql[start:end], name)

    def create_view_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.CreateViewStatement(sql[start:end], owner, name)

    def delete_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.DeleteStatement(sql[start:end], owner, name)

    def foreign_key_constraint(self, sql, tag, start, end, children):
        return self._ConstraintStatement(self.CreateForeignKeyStatement,
                sql, start, end, children)

    def grant_statement(self, sql, tag, start, end, children):
        return self.GrantStatement(sql[start:end])

    def insert_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.InsertStatement(sql[start:end], owner, name)

    def primary_key_constraint(self, sql, tag, start, end, children):
        return self._ConstraintStatement(self.CreatePrimaryKeyStatement,
                sql, start, end, children)

    def qualified_identifier(self, sql, tag, start, end, children):
        identifiers = self.DispatchList(sql, children)
        if len(identifiers) == 2:
            owner, name = identifiers
        else:
            owner = self.owner
            name, = identifiers
        return (owner, name)

    def quoted_identifier(self, sql, tag, start, end, children):
        return sql[start + 1:end - 1]

    def revoke_statement(self, sql, tag, start, end, children):
        return self.RevokeStatement(sql[start:end])

    def rollback_statement(self, sql, tag, start, end, children):
        return self.RollbackStatement(sql[start:end])

    def unique_constraint(self, sql, tag, start, end, children):
        return self._ConstraintStatement(self.CreateUniqueConstraintStatement,
                sql, start, end, children)

    def unquoted_identifier(self, sql, tag, start, end, children):
        return sql[start:end].upper()

    def update_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.UpdateStatement(sql[start:end], owner, name)

