from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess

def run_try():
    subprocess.run(["python", "/opt/airflow/dags/try.py"])

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 2, 13, 13, 50),  # Starting from 13:50
    'end_date': datetime(2025, 2, 13, 13, 55),    # Ending at 13:55
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG('run_try_dag', default_args=default_args, schedule_interval='* * 13 2 13', catchup=False) as dag:
    run_try_task = PythonOperator(
        task_id='run_try_task',
        python_callable=run_try
    )
