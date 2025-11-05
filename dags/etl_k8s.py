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

k8s_volume = k8s.V1Volume(
    name='git-sync-volume', 
    empty_dir=k8s.V1EmptyDirVolumeSource()
)
k8s_volume_mount = k8s.V1VolumeMount(
    name='git-sync-volume',    
    mount_path='/opt/dags' 
)

git_sync_init_container = k8s.V1Container(
    name='git-sync',
    image='k8s.gcr.io/git-sync/git-sync:v3.6.3', 
    security_context=k8s.V1SecurityContext(
        run_as_user=0
    ),
    volume_mounts=[k8s_volume_mount],
    env=[
        k8s.V1EnvVar(name='GIT_SYNC_REPO', value='https://github.com/hirundos/pizza_cd.git'),
        k8s.V1EnvVar(name='GIT_SYNC_BRANCH', value='main'),
        k8s.V1EnvVar(name='GIT_SYNC_ROOT', value='/opt/dags'), 
        k8s.V1EnvVar(name='GIT_SYNC_DEST', value=''),          
        k8s.V1EnvVar(name='GIT_SYNC_SUBPATH', value='dags'),   
        k8s.V1EnvVar(name='GIT_SYNC_ONE_TIME', value='true'),
        k8s.V1EnvVar(name='GIT_SYNC_DEST', value='repo'),
        k8s.V1EnvVar(
            name='GIT_SYNC_USERNAME', 
            value_from=k8s.V1EnvVarSource(
                secret_key_ref=k8s.V1SecretKeySelector(name='git-https-pat', key='username')
            )
        ),
        k8s.V1EnvVar(
            name='GIT_SYNC_PASSWORD', 
            value_from=k8s.V1EnvVarSource(
                secret_key_ref=k8s.V1SecretKeySelector(name='git-https-pat', key='token')
            )
        )
    ]
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
        namespace="default", 
        security_context=k8s.V1SecurityContext(
            run_as_user=0
        ),
        image="bitnami/kubectl:latest", 
        cmds=["sh", "-c"],
        arguments=["kubectl apply -f /opt/dags/repo/dags/spark-apps/bronze.yaml"],
        service_account_name="pizza-airflow",
        get_logs=False,   
        is_delete_operator_pod=False,
        init_containers=[git_sync_init_container],
        volumes=[k8s_volume],
        volume_mounts=[k8s_volume_mount]
    )

    silver = KubernetesPodOperator(
        task_id="spark_silver",
        name="spark-silver",
        namespace="default",
        security_context=k8s.V1SecurityContext(
            run_as_user=0
        ),
        image="bitnami/kubectl:latest",
        cmds=["sh", "-c"],
        arguments=["kubectl apply -f /opt/dags/repo/dags/spark-apps/silver.yaml"],
        get_logs=False,
        is_delete_operator_pod=True,
        service_account_name="pizza-airflow",
        
        init_containers=[git_sync_init_container],
        volumes=[k8s_volume],
        volume_mounts=[k8s_volume_mount]
    )

    gold = KubernetesPodOperator(
        task_id="spark_gold",
        name="spark-gold",
        namespace="default",
        security_context=k8s.V1SecurityContext(
            run_as_user=0
        ),
        image="bitnami/kubectl:latest",
        cmds=["sh", "-c"],
        arguments=["kubectl apply -f /opt/dags/repo/dags/spark-apps/gold.yaml"],
        get_logs=False,
        is_delete_operator_pod=True,
        service_account_name="pizza-airflow",

        init_containers=[git_sync_init_container],
        volumes=[k8s_volume],
        volume_mounts=[k8s_volume_mount]
    )

    bronze >> silver >> gold