from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

import yaml
from utils.logger import get_logger
from ingestion.pipelines.postos_abastecimento import run as postos_abastecimento_run


def run_postos_abastecimento():
    with open("pipelines_config/postos_abastecimento.yaml", "r") as f:
        config = yaml.safe_load(f)

    logger = get_logger(config["pipeline_name"])
    postos_abastecimento_run(config)


with DAG(
    dag_id='postos_abastecimento_ingestion',
    schedule='0 0 1 * *',
    start_date=datetime(2026, 5, 18),
    catchup=False,
    default_args={
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }
) as dag:
    PythonOperator(
        task_id='run_postos_abastecimento',
        python_callable=run_postos_abastecimento,
    )
