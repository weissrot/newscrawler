from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import subprocess

# Define the scraping function
def run_scraping_script():
    subprocess.run(["python", "/path/to/your/script/try111.py"])

# Define default_args for the DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'scraping_dag',
    default_args=default_args,
    description='Run the web scraping script at 13:10, 13:11, and 13:12 every day',
    schedule_interval="10,11,12 13 * * *",  # Run at 13:10, 13:11, and 13:12
    start_date=datetime(2025, 2, 13),  # Set your start date here
    catchup=False,
)


scraping_task = PythonOperator(
    task_id='scraping_task',
    python_callable=run_scraping_script,
    dag=dag,
)

scraping_task
