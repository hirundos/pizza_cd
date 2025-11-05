from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from kubernetes.client import models as k8s
from datetime import datetime

pod_security_context = k8s.V1PodSecurityContext(
    fs_group=65533
)

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 1, 1),
    "retries": 1,
}

with DAG(
    dag_id="spark_etl_pipeline_k8s",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    bronze = KubernetesPodOperator(
        task_id="spark_bronze",
        name="spark-bronze",
        namespace="default",
        security_context=pod_security_context, 
        image="bitnami/kubectl:latest", 
        cmds=["sh", "-c"],
        arguments=["kubectl apply -f /opt/dags/spark-apps/bronze.yaml"],
        service_account_name="pizza-airflow",
        get_logs=False,
        is_delete_operator_pod=True,
        
        git_sync_repo="git@github.com:hirundos/pizza_cd.git",
        git_sync_branch="main",
        git_sync_subpath="dags",
        git_sync_one_time=True,
        git_sync_ssh_key_secret_name="git-ssh-key",
        git_sync_known_hosts=False                   
    )

    silver = KubernetesPodOperator(
        task_id="spark_silver",
        name="spark-silver",
        namespace="default",
        security_context=pod_security_context,
        image="bitnami/kubectl:latest",
        cmds=["sh", "-c"],
        arguments=["kubectl apply -f /opt/dags/spark-apps/silver.yaml"],
        get_logs=False,
        is_delete_operator_pod=True,
        service_account_name="pizza-airflow",
        
        git_sync_repo="git@github.com:hirundos/pizza_cd.git",
        git_sync_branch="main",
        git_sync_subpath="dags",
        git_sync_one_time=True,
        git_sync_ssh_key_secret_name="git-ssh-key",
        git_sync_known_hosts=False
    )

    gold = KubernetesPodOperator(
        task_id="spark_gold",
        name="spark-gold",
        namespace="default",
        security_context=pod_security_context, 
        image="bitnami/kubectl:latest",
        cmds=["sh", "-c"],
        arguments=["kubectl apply -f /opt/dags/spark-apps/gold.yaml"],
        get_logs=False,
        is_delete_operator_pod=True,
        service_account_name="pizza-airflow",
        
        git_sync_repo="git@github.com:hirundos/pizza_cd.git",
        git_sync_branch="main",
        git_sync_subpath="dags",
        git_sync_one_time=True,
        git_sync_ssh_key_secret_name="git-ssh-key",
        git_sync_known_hosts=False
    )

    bronze >> silver >> gold