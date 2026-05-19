from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

import yaml
from utils.logging import get_logger
from ingestion.pipelines.openweathermap import run as openweathermap_run


def run_openweathermap():
    with open("pipelines_config/openweathermap.yaml", "r") as f:
        config = yaml.safe_load(f)

    logger = get_logger(config["pipeline_name"])
    openweathermap_run(config)


with DAG(
    dag_id='openweathermap_ingestion',
    schedule='/15 * * * *',
    start_date=datetime(2026, 5, 18),
    catchup=False,
    default_args={
        'retries': 1,
        'retry_delay': timedelta(minutes=1),
    }
) as dag:
    PythonOperator(
        task_id='run_openweathermap',
        python_callable=run_openweathermap,
    )
