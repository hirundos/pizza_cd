from airflow import DAG
from datetime import datetime
from airflow.providers.apache.spark.operators.spark_kubernetes import SparkKubernetesOperator

default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 1, 1),
}

with DAG(
    dag_id="spark_etl_pipeline_k8s",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    bronze_yaml_path = "spark-apps/bronze.yaml" 
    silver_yaml_path = "spark-apps/silver.yaml"
    gold_yaml_path = "spark-apps/gold.yaml"

    bronze = SparkKubernetesOperator(
        task_id="spark_bronze",
        namespace="airflow", 
        application_file=bronze_yaml_path, 
        do_xcom_push=True, 
    )

    silver = SparkKubernetesOperator(
        task_id="spark_silver",
        namespace="airflow",
        application_file=silver_yaml_path,
        do_xcom_push=True,
    )

    gold = SparkKubernetesOperator(
        task_id="spark_gold",
        namespace="airflow",
        application_file=gold_yaml_path,
        do_xcom_push=True,
    )

    bronze >> silver >> gold