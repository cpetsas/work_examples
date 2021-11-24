import schedule
import os
import pymysql
import time
import datetime
import pytz


def archive():
    # connection = pymysql.connect(host='localhost',
    #                              user='root',
    #                              password='',
    #                              db='rhea', )
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='new_repo'
    )
    # get all entried that are not archived
    query = "SELECT * FROM repo WHERE archieved = %s"
    cursor = connection.cursor()
    cursor.execute(query, 0)
    files = cursor.fetchall()
    cursor.close()
    # go through the files in the directory and compare the modified datetimes
    # if difference is more than 5 days, update record and set archived to 1
    for file in files:
        current = datetime.datetime.now()
        current = current.astimezone(pytz.timezone('Europe/London')).strftime('%Y-%m-%d %H:%M:%S')
        current = datetime.datetime.strptime(current, '%Y-%m-%d %H:%M:%S')
        file_date = file[3]
        difference = current - file_date
        if difference.days >= 5:
            query = "UPDATE repo set archieved = 1 where path = %s"
            cursor = connection.cursor()
            cursor.execute(query, file[1])
            connection.commit()
            cursor.close()
    print('Archiving completed')


def update():
    # this is the same as in the app.py file, check there for explanation
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='new_repo'
        )
        file_paths = []
        file = open("repo_path.txt", 'r')
        full_path = file.read()
        if not os.path.exists(full_path):
            print ('Path does not exist, upload has failed ')
        for root, directories, filenames in os.walk(full_path):
            for filename in filenames:
                cursor = connection.cursor()
                final_path = os.path.join(root, filename).replace('\\', '/')
                time_modified = datetime.datetime.fromtimestamp(os.path.getmtime(final_path))
                uk_time_modified = time_modified.astimezone(pytz.timezone('Europe/London')).strftime('%Y-%m-%d %H:%M:%S')
                uk_time_modified = datetime.datetime.strptime(uk_time_modified,'%Y-%m-%d %H:%M:%S')
                time_created = datetime.datetime.fromtimestamp(os.path.getctime(final_path))
                uk_time_created = time_created.astimezone(pytz.timezone('Europe/London')).strftime('%Y-%m-%d %H:%M:%S')
                uk_time_created = datetime.datetime.strptime(uk_time_created,'%Y-%m-%d %H:%M:%S')
                size = os.path.getsize(final_path)
                file_paths.append(final_path)
                data_to_be_inserted = (filename, final_path, uk_time_created, uk_time_modified, size)
                query = "SELECT * FROM repo WHERE path=%s"
                cursor.execute(query, final_path)
                result = cursor.fetchone()
                cursor.close()
                if result is None:
                    query = "INSERT INTO repo (name, path, created_at, updated_at, size) VALUES(%s, %s, %s, %s ,%s);"
                    cursor = connection.cursor()
                    cursor.execute(query, data_to_be_inserted)
                    connection.commit()
                    cursor.close()
                else:
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
        print('Update successful')
    except:
        print('Something went wrong, upload has failed')


# archive every 50 seconds, update every 30 seconds
schedule.every(50).seconds.do(archive)
schedule.every(30).seconds.do(update)

while 1:
    schedule.run_pending()
    time.sleep(1)
