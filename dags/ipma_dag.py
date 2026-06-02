from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

import yaml
from utils.logger import get_logger
from ingestion.pipelines.ipma import IPMAPipeline


def run_ipma():
    with open("pipelines_config/ipma.yaml", "r") as f:
        config = yaml.safe_load(f)

    get_logger()
    IPMAPipeline(config).run()


with DAG(
    dag_id='ipma_ingestion',
    schedule='0 */3 * * *',
    start_date=datetime(2026, 5, 18),
    catchup=False,
    default_args={
        'retries': 1,
        'retry_delay': timedelta(minutes=1),
    }
)as dag:
    PythonOperator(
        task_id='run_ipma',
        python_callable=run_ipma,
    )
