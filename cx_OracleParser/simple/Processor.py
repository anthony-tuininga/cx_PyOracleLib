"""Module for processing dependencies in SQL."""

import cx_Parser

import Statements

__all__ = [ "Processor" ]

class Processor(cx_Parser.DispatchProcessor):
    AlterObjectStatement = Statements.AlterObjectStatement
    AnonymousPlsqlBlock = Statements.AnonymousPlsqlBlock
    CommentStatement = Statements.CommentStatement
    CommitStatement = Statements.CommitStatement
    ConnectStatement = Statements.ConnectStatement
    CreateConstraintStatement = Statements.CreateConstraintStatement
    CreateObjectStatement = Statements.CreateObjectStatement
    DeleteStatement = Statements.DeleteStatement
    DropObjectStatement = Statements.DropObjectStatement
    GrantStatement = Statements.GrantStatement
    InsertStatement = Statements.InsertStatement
    RenameObjectStatement = Statements.RenameObjectStatement
    RevokeStatement = Statements.RevokeStatement
    RollbackStatement = Statements.RollbackStatement
    TruncateObjectStatement = Statements.TruncateObjectStatement
    UpdateStatement = Statements.UpdateStatement

    def __init__(self, initialOwner = None):
        self.owner = initialOwner

    def _merge_keywords(self, children):
        keywords = [t[3:] for t, st, e, c in children]
        return " ".join(keywords)

    def anonymous_plsql_block(self, sql, tag, start, end, children):
        return self.AnonymousPlsqlBlock(sql[start:end])

    def comment_statement(self, sql, tag, start, end, children):
        return self.CommentStatement(sql[start:end])

    def commit_statement(self, sql, tag, start, end, children):
        return self.CommitStatement(sql[start:end])

    def complex_object_type(self, sql, tag, start, end, children):
        return self._merge_keywords(children)

    def connect_statement(self, sql, tag, start, end, children):
        parts = self.DispatchList(sql, children)
        return self.ConnectStatement(*parts)

    def constraint_type(self, sql, tag, start, end, children):
        return self._merge_keywords(children)

    def create_constraint_statement(self, sql, tag, start, end, children):
        owner, tableName = self.Dispatch(sql, children[1])
        name = self.Dispatch(sql, children[2])
        type = self.Dispatch(sql, children[3])
        if " " not in type:
            type += " constraint"
        return self.CreateConstraintStatement(sql[start:end], type, owner,
                name, tableName)

    def alter_object_statement(self, sql, tag, start, end, children):
        type = self.Dispatch(sql, children[0])
        owner, name = self.Dispatch(sql, children[1])
        return self.AlterObjectStatement(sql[start:end], type, name, owner)

    def create_object_statement(self, sql, tag, start, end, children):
        type = self.Dispatch(sql, children[0])
        owner, name = self.Dispatch(sql, children[1])
        return self.CreateObjectStatement(sql[start:end], type, name, owner)

    def delete_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.DeleteStatement(sql[start:end], owner, name)

    def drop_object_statement(self, sql, tag, start, end, children):
        type = self.Dispatch(sql, children[0])
        owner, name = self.Dispatch(sql, children[1])
        return self.DropObjectStatement(sql[start:end], type, name, owner)

    def grant_statement(self, sql, tag, start, end, children):
        return self.GrantStatement(sql[start:end])

    def insert_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.InsertStatement(sql[start:end], owner, name)

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

    def rename_statement(self, sql, tag, start, end, children):
        name = self.Dispatch(sql, children[0])
        return self.RenameObjectStatement(sql[start:end], name)

    def revoke_statement(self, sql, tag, start, end, children):
        return self.RevokeStatement(sql[start:end])

    def rollback_statement(self, sql, tag, start, end, children):
        return self.RollbackStatement(sql[start:end])

    def simple_object_type(self, sql, tag, start, end, children):
        return self._merge_keywords(children)

    def truncate_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[1])
        return self.TruncateObjectStatement(sql[start:end], owner, name)

    def unquoted_identifier(self, sql, tag, start, end, children):
        return sql[start:end].upper()

    def update_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.UpdateStatement(sql[start:end], owner, name)

