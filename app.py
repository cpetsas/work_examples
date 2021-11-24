import flask
import os
import pytz
import pymysql
import datetime

app = flask.Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def index():
    db = pymysql.connect(
        host = 'localhost',
        user = 'root',
        password = ''
    )
    cursor = db.cursor()
    # when this is ran the first time it creates a db and a table in the db. Running it again has no effect because db and table already
    # exist and code is enclosed in try except
    try:
        # creates the database on localhost
        cursor.execute("CREATE DATABASE new_repo")
        cursor.close()
        db = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database = 'new_repo'
        )
        cursor = db.cursor()
        # create table
        cursor.execute("CREATE TABLE repo (name varchar(100) DEFAULT NULL, path varchar(300) DEFAULT NULL, created_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at datetime DEFAULT NULL, size mediumint(8) UNSIGNED DEFAULT NULL, archieved tinyint(1) DEFAULT 0)")
        cursor.close()
    except:
        pass
    # render index view
    return flask.render_template('index.html')


@app.route('/narchived', methods=['GET'])
def narchived():
    # Get all files that are not archived
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='new_repo'
    )
    query = "SELECT * FROM repo WHERE archieved = %s"
    cursor = connection.cursor()
    cursor.execute(query, 0)
    files = cursor.fetchall()
    # and pass non archived files in view
    return flask.render_template('non_archived.html', files=files)


@app.route('/archived', methods=['GET'])
def archived():
    # get archived files
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='new_repo'
    )
    query = "SELECT * FROM repo WHERE archieved = %s"
    cursor = connection.cursor()
    cursor.execute(query, 1)
    files = cursor.fetchall()
    #pass archived files in view
    return flask.render_template('archived.html', files=files)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    try:
        # upload all files in the directory to the database
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='new_repo'
        )
        file_paths = []
        # get path from form submitted
        full_path = flask.request.form['repo_path']
        # check if path provided exists
        if not os.path.exists(full_path):
            message = 'Path does not exist, upload has failed :('
            return flask.render_template('upload.html', message=message)
        # if file doesnt exist, create it and write in it the path so the jobs.py file knows where to check for updates
        # if file exists just overwrite the path
        file = open('repo_path.txt', 'w')
        file.write(full_path)
        # get all files in path
        for root, directories, filenames in os.walk(full_path):
            for filename in filenames:
                cursor = connection.cursor()
                final_path = os.path.join(root, filename).replace('\\', '/')
                # im turning all times to a specific timezone to fix the problem of 'what happens if pc changes time'
                # which could introduce a bug when trying to archive files
                time_modified = datetime.datetime.fromtimestamp(os.path.getmtime(final_path))
                uk_time_modified = time_modified.astimezone(pytz.timezone('Europe/London')).strftime('%Y-%m-%d %H:%M:%S')
                uk_time_modified = datetime.datetime.strptime(uk_time_modified,'%Y-%m-%d %H:%M:%S')
                time_created = datetime.datetime.fromtimestamp(os.path.getctime(final_path))
                uk_time_created = time_created.astimezone(pytz.timezone('Europe/London')).strftime('%Y-%m-%d %H:%M:%S')
                uk_time_created = datetime.datetime.strptime(uk_time_created,'%Y-%m-%d %H:%M:%S')
                size = os.path.getsize(final_path)
                file_paths.append(final_path)
                data_to_be_inserted = (filename, final_path, uk_time_created, uk_time_modified, size)
                # query to check if there is already an entry with the same path
                query = "SELECT * FROM repo WHERE path=%s"
                cursor.execute(query, final_path)
                result = cursor.fetchone()
                cursor.close()
                # if there is no other file with the same path that means this file is a new file, so  insert it in db
                if result is None:
                    query = "INSERT INTO repo (name, path, created_at, updated_at, size) VALUES(%s, %s, %s, %s ,%s);"
                    cursor = connection.cursor()
                    cursor.execute(query, data_to_be_inserted)
                    connection.commit()
                    cursor.close()
                else:
                    # if file already exists I update the details
                    data_to_be_inserted = (filename, final_path, uk_time_created, uk_time_modified, size, final_path)
                    query = "UPDATE repo SET name=%s, path=%s, created_at=%s, updated_at=%s, size=%s WHERE path=%s"
                    cursor = connection.cursor()
                    cursor.execute(query, data_to_be_inserted)
                    connection.commit()
                    cursor.close()
        query = "SELECT path FROM repo"
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        # query has all paths in db. This loop checks to see if there is a path in the db that is not in the paths
        # that we are adding from the directory. If directory does not contain a path that exists in db that means
        # that file was deleted or moved, so we delete the entry from the db
        for db_path in result:
            db_path = list(db_path)
            db_path = db_path[0]
            if db_path not in file_paths:
                cursor = connection.cursor()
                query = "delete FROM repo WHERE path= %s"
                cursor.execute(query, db_path)
                connection.commit()
                cursor.close()
        cursor.close()
        connection.close()
        message = 'Upload successful'
        return flask.render_template('upload.html', message = message)
    except:
        message = 'Something went wrong, upload has failed :('
        return flask.render_template('upload.html', message = message)
