# -*- coding: utf-8 -*-
import sqlite3
import traceback


class SqLite:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()

    def execute(self, sql, *args):
        try:
            self.cur.execute(sql, *args)
            self.conn.commit()
            return True
        except Exception as e:
            traceback.print_exc()
        finally:
            self.conn.commit()

    def drop_table(self, table_name):
        """delete table {table_name} if it exist"""
        return self.execute('DROP TABLE IF EXISTS {table_name}'.format(table_name=table_name))

    def create_table(self, table_name, table_schema, **kwargs):
        """create table in db
        {table_name} is for name
        {table_schema} is for dict like {'column_name': 'column_type'}
        {if_exists} is for drop table if exist or do nothing
        {primary_key} is for list of primary keys
        """
        primary_key, if_exist = kwargs.get('primary_key'), kwargs.get('if_exist')
        if if_exist:
            self.drop_table(table_name)
        sql = """CREATE TABLE {table_name}\n({columns})"""\
            .format(table_name=table_name,
                    columns=', '.join(['{c_name} {c_type}{primary_key}'.format(c_name=c_name,
                                                                               c_type=c_type,
                                                                               primary_key=' PRIMARY KEY'
                                                                               if c_name == primary_key else '')
                                           for c_name, c_type in table_schema.items()]))
        return self.execute(sql)

    def insert_row(self, table_name, data, **kwargs):
        """write row in db
        {table_name} is for name
        {if_exist} is for replace row if such primary key already exist
        {data} is for dict like {'column_name': 'value'}"""
        if_exist = kwargs.get('if_exist')
        sql = """INSERT {if_exist}INTO {table_name} {columns} VALUES ({values})"""\
            .format(if_exist='OR REPLACE ' if if_exist else '',
                    table_name=table_name,
                    columns=str(tuple(data.keys())),
                    values=', '.join(['?']*len(data.keys())))
        return self.execute(sql, tuple(data.values()))

    def insert_table(self, table_name, data, **kwargs):
        """write whole table
        {table_name} is for name
        {data} is for pd.DataFrame
        {if_exist} is for insert row logic:
                True is for update by primary key,
                False is for insert anyway (works only if not primary_key in table, else constraint violation occurs)"""
        if_exist = kwargs.get('if_exist')
        try:
            for row in data:
                if not self.insert_row(table_name=table_name, data=row, if_exist=if_exist):
                    break
        except Exception as e:
            traceback.print_exc()

    def update_row(self, table_name, data, **kwargs):
        """update table row if exsits
        {table_name} is for name
        {data} is for new data set dict like {'column_name': 'value'}
        {condition} is for condition by what to update dict like {'column_name': 'value'}"""
        condition = kwargs.get('condition')
        sql = """UPDATE {table_name} SET {data}{condition}"""\
            .format(table_name=table_name,
                    data=', '.join(['{c_name} = ?'.format(c_name=c_name) for c_name in data.keys()]),
                    condition=' WHERE {cond}'.format(cond=', '.join(['{c_name} = ?'
                                                                    .format(c_name=c_name)
                                                                     for c_name in condition.keys()]))
                    if condition else '')
        return self.execute(sql, tuple([*data.values(), *condition.values()]))

    def delete_row(self, table_name, **kwargs):
        """delete row
        {table_name} is for name
        {condition} is for filter, dict like {'column_name': 'value'}"""
        condition = kwargs.get('condition')
        sql = """DELETE FROM {table_name}{condition}""".format(table_name=table_name,
                                                               condition=' WHERE {cond}'.format(
                                                                   cond=', '.join(['{c_name} = ?'
                                                                                  .format(c_name=c_name)
                                                                                   for c_name in condition.keys()])))
        return self.execute(sql, tuple(condition.values()))

    def select_data(self, table_name, **kwargs):
        """gain data from table
        {table_name} is for name
        {columns} is for columns to gain, list
        {distinct} is for distinct select, True/False
        {condition} is for filter, dict like {'column_name': 'value'}
        {order} is for order by, dict like {'column_name': {desc}} where {desc} like asc/desc
        {random} is for random rows, True/False
        {limit} is for limit filter, Integer
        """
        columns, distinct, condition, order, random, desc, limit = [kwargs.get(i) for i in ('columns',
                                                                                            'distinct',
                                                                                            'condition',
                                                                                            'order',
                                                                                            'random',
                                                                                            'desc',
                                                                                            'limit')]
        sql = """SELECT {distinct}{columns}\nFROM {table_name}{condition}{order}{random}{limit}"""\
            .format(distinct='DISTINCT ' if distinct else '',
                    columns=', '.join([column for column in columns]) if columns else '*',
                    table_name=table_name,
                    condition='\n WHERE {cond}'.format(cond=', '.join(['{c_name} = ?'
                                                                      .format(c_name=c_name)
                                                                       for c_name in condition.keys()]))
                    if condition else '',
                    order='\n ORDER BY {cond}'
                    .format(cond=', '.join(['{c_name} {desc}'.format(c_name=c_name,
                                                                     desc=desc)
                                            for c_name, desc in order.items()])) if order else '',
                    random=' random() ' if random else '',
                    limit='\n LIMIT {limit}'.format(limit=limit) if limit else '')

        self.execute(sql, tuple(condition.values()) if condition else '')
        if limit and limit == 1:
            return dict(self.cur.fetchone())
        else:
            return [dict(row) for row in self.cur.fetchall()]





