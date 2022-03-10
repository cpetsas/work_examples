from redshift_management import redshift
import json
from datetime import timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable

import requests

args = {
    'owner': '',
}

dag = DAG(
    dag_id='airtable_migration',
    default_args=args,
    schedule_interval='0 * * * *',
    start_date=days_ago(1),
    dagrun_timeout=timedelta(minutes=60),
)

AIRTABLE_ENDPOINT = json.loads(Variable.get("AIRTABLE_ENDPOINT"))
BEARER_TOKEN = Variable.get("BEARER_TOKEN")
REDSHIFT_HOST = Variable.get("REDSHIFT_HOST")
REDSHIFT_DBNAME = Variable.get("REDSHIFT_DBNAME")
REDSHIFT_DBUSER = Variable.get("REDSHIFT_DBUSER")
REDSHIFT_DBPASSWORD = Variable.get("REDSHIFT_DBPASSWORD")
REDSHIFT_PORT = Variable.get("REDSHIFT_PORT")


def delete_old(table_name):
    red = redshift.Redshift()
    red.connect(dbname=REDSHIFT_DBNAME, dbhost=REDSHIFT_HOST,dbuser=REDSHIFT_DBUSER,dbpassword=REDSHIFT_DBPASSWORD,dbport = REDSHIFT_PORT)
    print(red.delete_data('public', table_name))


def airtable_to_redshift(table_name, airtable_name):
    headers = {"Authorization": BEARER_TOKEN}
    response = requests.get(airtable_name, headers=headers)
    red = redshift.Redshift()
    red.connect(dbname=REDSHIFT_DBNAME, dbhost=REDSHIFT_HOST,dbuser=REDSHIFT_DBUSER,dbpassword=REDSHIFT_DBPASSWORD,dbport = REDSHIFT_PORT)
    body = response.json()['records']
    for record in body:
        if record['fields'] != {}:
            for key in record['fields']:
                if isinstance(record['fields'][key], str):
                    record['fields'][key] = "'" + record['fields'][key] + "'"
            keys, values = red.prepare_keys_values_for_insert(record['fields'])
            print(red.insert_data('public', table_name, keys, values))

for table in AIRTABLE_ENDPOINT:

    delete_old_task = PythonOperator(
            task_id = 'delete_old'+'_'+str(table),
            provide_context = True,
            python_callable = delete_old,
            op_args = [table],
            dag = dag
        )

    airtable_to_redshift_task = PythonOperator(
            task_id = 'airtable_to_redshift'+'_'+str(table),
            provide_context = True,
            python_callable = airtable_to_redshift,
            op_args = [table, AIRTABLE_ENDPOINT[table]],
            dag = dag
        )

    delete_old_task >> airtable_to_redshift_task