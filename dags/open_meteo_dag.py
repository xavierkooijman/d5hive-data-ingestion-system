from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

import yaml
from utils.logging import get_logger
from ingestion.pipelines.open_meteo import run as open_meteo_run


def run_open_meteo():
    with open("pipelines_config/open_meteo.yaml", "r") as f:
        config = yaml.safe_load(f)

    logger = get_logger(config["pipeline_name"])
    open_meteo_run(config)


with DAG(
    dag_id='open_meteo_ingestion',
    schedule='*/15 * * * *',
    start_date=datetime(2026, 5, 18),
    catchup=False,
    default_args={
        'retries': 1,
        'retry_delay': timedelta(minutes=1),
    }
) as dag:
    PythonOperator(
        task_id='run_open_meteo',
        python_callable=run_open_meteo,
    )
