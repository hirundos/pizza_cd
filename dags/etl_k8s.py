from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from datetime import datetime

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


    GIT_REPO = "https://github.com/hirundos/pizza_cd.git"
    GIT_BRANCH = "main"
    GIT_SUBPATH = "dags" 
    MOUNT_PATH = "/opt/dags"

    bronze = KubernetesPodOperator(
        task_id="spark_bronze",
        name="spark-bronze",
        namespace="airflow", 
        image="bitnami/kubectl:latest", 
        cmds=["sh", "-c"],
        arguments=["kubectl apply -f /opt/dags/spark-apps/bronze.yaml"],
        get_logs=True,
        service_account_name="spark-app-runner",
        git_sync_repo=GIT_REPO,
        git_sync_branch=GIT_BRANCH,
        git_sync_subpath=GIT_SUBPATH,
        git_sync_mount_path=MOUNT_PATH
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
        git_sync_repo=GIT_REPO,
        git_sync_branch=GIT_BRANCH,
        git_sync_subpath=GIT_SUBPATH,
        git_sync_mount_path=MOUNT_PATH
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
        git_sync_repo=GIT_REPO,
        git_sync_branch=GIT_BRANCH,
        git_sync_subpath=GIT_SUBPATH,
        git_sync_mount_path=MOUNT_PATH
    )

    bronze >> silver >> gold
