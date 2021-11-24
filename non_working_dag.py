for f in files:
        try:
            path = os.path.join(AIRTABLE_MIGRATION_TMP_PATH, f)
            if os.path.exists(path):
                with open(path, 'r') as config:
                    data = config.read()
                    airtable_db = json.loads(data)

                    db_endpoint = airtable_db['endpoint']
                    name = airtable_db['name']
                    order = airtable_db['config']['order']
                    with TaskGroup(name.replace(" ","_").lower(), tooltip="Task group to integrate database data into Airtable {} in Redshift.".format(name)) as dw_data_integration_airtable_db:
                        previous_task_group = None
                        for table in order:
                            redshift_table_name = airtable_db['config'][table]['dw_table_name']

                            with TaskGroup(redshift_table_name, tooltip="Task group to integrate the data from the Airtable table {} into Redshift.".format(redshift_table_name)) as dw_data_integration_table:
                                table_endpoint = db_endpoint + table
                                columns = airtable_db['config'][table]['columns']

                                create_table_task = PythonOperator(
                                    task_id = 'create_table',
                                    python_callable = create_table_if_not_exists,
                                    op_args = [redshift_table_name, columns],
                                    dag = dag
                                )
                                delete_old_task = PythonOperator(
                                        task_id = 'delete_old',
                                        python_callable = delete_old,
                                        op_args = [redshift_table_name],
                                        dag = dag
                                    )

                                airtable_to_redshift_task = PythonOperator(
                                        task_id = 'airtable_to_redshift',
                                        python_callable = airtable_to_redshift,
                                        op_args = [redshift_table_name, table_endpoint, columns, db_endpoint],
                                        dag = dag
                                    )
                                create_table_task >> delete_old_task
                                delete_old_task >> airtable_to_redshift_task
                            if previous_task_group != None:
                                previous_task_group >> dw_data_integration_table
                                previous_task_group = dw_data_integration_table
                            else:
                                previous_task_group = dw_data_integration_table
