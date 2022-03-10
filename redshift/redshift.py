from datetime import datetime
import sys

class Redshift:
    __slots__ = ["__conn"]
    def __init__(self):
        self.__conn = None

    def connect(self, dbname, dbhost, dbuser, dbpassword, dbport = 5432):
        """
            Function to connect to the database. 
        """
        import psycopg2
        import json

        try:
            self.__conn = psycopg2.connect(dbname = dbname, host = dbhost, port = dbport, user = dbuser, password = dbpassword)
            return self.__conn
        except Exception as e:
            raise e
    
    def execute(self, sql):
        """
            Function to run raw SQL queries.
            Parameters:
                - sql [string]: SQL instruction
        """

        try:
            cursor = self.__conn.cursor()
            with self.__conn.cursor() as curs:
                curs.execute(sql)
                self.__conn.commit() # Not necessary if we run a query
                return curs.fetchall()
        except Exception as e:
            raise e

    def prepare_keys_values_for_insert(self, data):
        """
            This functions takes the data dictionary and loops through the keys and their values.
            Strings in the dictionary must be wrapped in quotes
            It puts them in a string form ready to be appended on the sql query we will use later.
            Takes and reuturns no arguments
        """
        keys='('
        values_string='('
        values = []
        counter = 0
        for key in data:
            values.append(data[key])
            if counter == 0:
                keys = keys + str(key)
                values_string = values_string + str(data[key])
            else:
                keys = keys + ',' + str(key)
                values_string = values_string + ',' + str(data[key])
            counter += 1
        keys = keys + ')'
        values_string = values_string + ')'
        return(keys, values_string)

    def prepare_keys_values_for_update(self, data):
        """
            Takes disctionary and creates an sql formatted string ready to be used with the update sql query
            Strings in the dictionary must be wrapped in quotes
            The condition and new data parameters must be valid sql formatted strings
            Returns an sql formatted string
        """
        sql_string = ''
        counter = 0
        for key in data:
            if counter != 0:
                sql_string = sql_string + ', '
            sql_string = sql_string + str(key) + ' = ' + str(data[key])
            counter = counter + 1
        return(sql_string)
        
    def insert_data(self, schema_name, table_name, keys, values_string):
        """
            Puts together the sql query for inserting the data in the database, executed the query and commits the changes
            Takes no arguments and returns a message based on result
        """
        try:
            sql =  "INSERT INTO " + schema_name + "." + table_name + ' ' + keys + ' VALUES ' + values_string + ';'

            cursor = self.__conn.cursor()
            cursor.execute(sql)
            self.__conn.commit()
            return("Successfully inserted data")
        except Exception as e:
            raise e

    def create_table(self, schema_name, table_name, structure):
        """
            Creates a new table with the specified name under the given schema.
            All parameters are expected to be correctly structured strings.
            Returns message based on result.
        """
        try:
            sql = "CREATE TABLE IF NOT EXISTS " + schema_name + "." + table_name + " (" + structure + ")"
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            self.__conn.commit()
            return("Table created successfuly")
        except Exception as e:
            raise e

    def delete_table(self, schema_name, table_name):
        """
            Deleted table gives the table's details.
            schema_name and table_name are strings.
            Returns message based on result
        """
        try:
            sql = "DROP TABLE IF EXISTS " + schema_name + "." + table_name
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            self.__conn.commit()
            return("Table deleted successfuly")
        except Exception as e:
            raise e
    
    def edit_record(self, schema_name, table_name, condition, new_data):
        """
            Edits record on the provided table given the condition.
            The condition and new data parameters must be valid sql formatted strings
            Returns message based on result
        """
        try:
            sql = "UPDATE " + schema_name + "." + table_name + " SET " + new_data + "WHERE " + condition
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            self.__conn.commit()
            return('Record edited successfully')
        except Exception as e:
            raise e

    def delete_data(self, schema_name, table_name, condition = ''):
        """
            Deleted record on the provided table given the condition.
            The condition parameter must be valid sql formatted strings
            Returns message based on result
        """
        try:
            if condition == '':
                sql = "DELETE FROM " + schema_name + "." + table_name
            else:
                sql = "DELETE FROM " + schema_name + "." + table_name + " WHERE " + condition
            print(sql)
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            self.__conn.commit()
            return('Record deleted successfully')
        except Exception as e:
            raise e

if __name__ == '__main__':
    pass