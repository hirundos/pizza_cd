from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from kubernetes.client import models as k8s
from datetime import datetime

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 1, 1),
    "retries": 1,
}

k8s_volume_mount = k8s.V1VolumeMount(
    name='dags-volume',         
    mount_path='/opt/dags',    
    read_only=True             
)

k8s_volume = k8s.V1Volume(
    name='dags-volume',         
    persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(
        claim_name='airflow-dags-pvc'
    )
)


with DAG(
    dag_id="spark_etl_pipeline_k8s",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    bronze = KubernetesPodOperator(
        task_id="spark_bronze",
        name="spark-bronze",
        namespace="airflow", 
        image="bitnami/kubectl:latest", 
        cmds=["sh", "-c"],
        arguments=["kubectl apply -f /opt/dags/spark-apps/bronze.yaml"],
        get_logs=True,
        service_account_name="spark-app-runner",
        volumes=[k8s_volume],
        volume_mounts=[k8s_volume_mount]
    )

    silver = KubernetesPodOperator(
        task_id="spark_silver",
        name="spark-silver",
        namespace="airflow",
        image="bitnami/kubectl:latest",
        cmds=["sh", "-c"],
        arguments=["kubectl apply -f /opt/dags/spark-apps/silver.yaml"],
        get_logs=True,
        service_account_name="spark-app-runner",
        volumes=[k8s_volume],
        volume_mounts=[k8s_volume_mount]
    )

    gold = KubernetesPodOperator(
        task_id="spark_gold",
        name="spark-gold",
        namespace="airflow",
        image="bitnami/kubectl:latest",
        cmds=["sh", "-c"],
        arguments=["kubectl apply -f /opt/dags/spark-apps/gold.yaml"],
        get_logs=True,
        service_account_name="spark-app-runner",
        volumes=[k8s_volume],
        volume_mounts=[k8s_volume_mount]    
    )

    bronze >> silver >> gold
