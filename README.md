
GitOps 저장소 (ArgoCD)
이 리포지토리는 ArgoCD의 'App of Apps' 패턴을 사용하여 [pizza 시리즈]의 모든 마이크로서비스와 인프라 구성 요소를 Kubernetes 클러스터에 배포하기 위한 중앙 GitOps 저장소입니다.

📁 리포지토리 구조 및 구성 요소
이 리포지토리는 다음과 같은 디렉토리 구조를 가집니다. 각 디렉토리는 하나의 독립적인 구성 요소(ArgoCD Application)에 해당합니다.

Bash
```
├── airflow/        # Apache Airflow 
├── cloudsql-proxy/ # Google Cloud SQL Proxy 
├── dags/           # Airflow DAGs (Git-Sync로 Airflow에 마운트됨)
├── login/          # 'login' 마이크로서비스 
├── menu/           # 'menu' 마이크로서비스
├── monitoring/     # 모니터링 스택 
├── order/          # 'order' 마이크로서비스
├── spark/          #  Spark Operator 관련 리소스
├── web/            # 'web' 프론트엔드 

```

