# tensorflow-serving

## Test the 3 models separately

- `half_plus_two` model:
    ```shell
    docker run -t --rm -p 8501:8501 \
        --name=serving \
        -v $(pwd)/models/half_plus_two/1:/models/half_plus_two/1 \
        -e MODEL_NAME=half_plus_two \
        tensorflow/serving
    
    curl -X POST http://localhost:8501/v1/models/half_plus_two:predict \
         -H 'Content-type: application/json' \
         -d '{"signature_name": "serving_default", "instances": [{"x": [0, 1, 2]}]}'
    ```

- `half_plus_ten` model (v1):
    ```shell
    docker run -t --rm -p 8501:8501 \
        --name=serving \
        -v $(pwd)/models/half_plus_ten/1:/models/half_plus_ten/1 \
        -e MODEL_NAME=half_plus_ten \
        tensorflow/serving

    curl -X POST http://localhost:8501/v1/models/half_plus_ten:predict \
         -H 'Content-type: application/json' \
         -d '{"signature_name": "serving_default", "instances": [{"x": [0, 1, 2]}]}'
    ```

## Serve multiple models

- We have to use the model server config file in `models/models.config` that specifies the locations of all exposed
  models:
  ```shell
    # periodically poll for updated versions
  docker run -t --rm -p 8501:8501 -p 8500:8500\
      --name=serving \
      -v "$(pwd)/models/:/models/" \
      tensorflow/serving \
      --model_config_file=/models/models.config \
      --allow_version_labels_for_unavailable_models=true \
      --model_config_file_poll_wait_seconds=60
  ```
  The `--model_config_file_poll_wait_seconds=60` option means that the server polls model updates every 60s.


- test the REST API:
  ```shell
  # /v1/models/<model name>
  # /v1/models/<model name>/versions/<version number>
  # /v1/models/<model name>/labels/<version label>.

  curl -X POST http://localhost:8501/v1/models/half_plus_two:predict \
      -H 'Content-type: application/json' \
      -d '{"signature_name": "serving_default", "instances": [{"x": [0, 1, 2]}]}'

  curl -X POST http://localhost:8501/v1/models/half_plus_ten/versions/2:predict \
      -H 'Content-type: application/json' \
      -d '{"signature_name": "serving_default", "instances": [{"x": [0, 1, 2]}]}'

  curl -X POST http://localhost:8501/v1/models/half_plus_ten/labels/stable:predict \
      -H 'Content-type: application/json' \
      -d '{"signature_name": "serving_default", "instances": [{"x": [0, 1, 2]}]}'
  ```

## Monitoring with Prometheus and Visualization with Grafana (docker-compose)

- Create a `models/monitoring.config` file with the following content:
  ```
  prometheus_config {
    enable: true,
    path: "/monitoring/prometheus/metrics"
  }
  ```


- Create a `promeheus.yml` file. The `scrape_configs.metrics_path` matches the endpoint exposed
  in `models/monitoring.config`.


- Use docker-compose to allow all services to communicate with each other:
  ```shell
  docker-compose up
  ```


- From `docker-compose.yml` you can see that:
    - to read metrics from the `/monitoring/prometheus/metrics` we have enabled the HTTP server by
      setting `--rest_api_port=8501` and `--monitoring_config_file=/models/monitoring.config`. You can verify that the
      metrics are exposed by visiting `http://localhost:8501/monitoring/prometheus/metrics`.

    - you should be able to access the Prometheus web UI through `localhost:9090`. You can also execute the
      query `:tensorflow:serving:request_count`.

    - you should be able to access the Grafana WebUI through `localhost:3000`. The username and password are `admin`
      and `admin`, respectively. In the WebUI you can add a new datasource with the url `http://prometheus:9090`

## Monitoring with Prometheus and Visualization with Grafana (Kubernetes)

- In the ideal case we have to mount a volume that contains the models into the pod running the tensorflow server. In
  order to make local testing easier we will just extend the tensorflow server image by adding to it the models:
  ```shell
  docker build -t tf-server:1.0.0 -f kubernetes/Dockerfile .
  
  DOCKER_HUB_USR=''
  $DOCKER_HUB_PWD=''
  docker login -u "$DOCKER_HUB_USR" -p "$DOCKER_HUB_PWD"
  docker tag tf-server:1.0.0 $DOCKER_HUB_USR/tf-server:1.0.0
  docker push docker.io/$DOCKER_HUB_USR/tf-server:1.0.0
  
  # test
  docker run -t --rm -p 8501:8501 -p 8500:8500\
      --name=serving \
      tf-server:custom \
      --model_config_file=/models/models.config \
      --allow_version_labels_for_unavailable_models=true \
      --model_config_file_poll_wait_seconds=60
  
  kubectl apply -f kubernetes/tf-server.yaml
  ```

- Setup Prometheus
    - A: Customize Scrape Configurations. It is possible to inject externally managed scrape configurations via a Secret
      by setting:
        - `prometheus.additionalScrapeConfigs.enabled`: true
        - `prometheus.additionalScrapeConfigs.type`: external

      The secret must exist in the same namespace which the kube-prometheus will be deployed into. Set the secret name
      and the key containing the additional scrape configuration using the parameters:
        - `prometheus.additionalScrapeConfigs.external.name`
        - `prometheus.additionalScrapeConfigs.external.key`
    - Example:
      ```
      prometheus.additionalScrapeConfigs.enabled=true
      prometheus.additionalScrapeConfigs.type=external
      prometheus.additionalScrapeConfigs.external.name=kube-prometheus-prometheus-scrape-config
      prometheus.additionalScrapeConfigs.external.key=additional-scrape-configs.yaml
      ``` 
    - B: Define scrape configurations to be managed by the Helm chart. Set:
        - `prometheus.additionalScrapeConfigs.enabled`: true
        - `prometheus.additionalScrapeConfigs.type`: internal
        - use `prometheus.additionalScrapeConfigs.internal.jobList` to define a list of additional scrape jobs for
          Prometheus
    - Example:
      ```
      prometheus.additionalScrapeConfigs.enabled=true
      prometheus.additionalScrapeConfigs.type=internal
      prometheus.additionalScrapeConfigs.internal.jobList=
          - job_name: 'opentelemetry-collector'
            # metrics_path defaults to '/metrics'
            # scheme defaults to 'http'.
            static_configs:
              - targets: ['opentelemetry-collector:8889']
      ``` 

- Setup Prometheus and Grafana
  ```shell
  kubectl create namespace monitoring
  kubectl create namespace tfmodels

  helm install --namespace tfmodels \
      tf-serving-chart tf-serving
  helm install --namespace monitoring -f values_prometheus.yaml \
      prometheus-chart bitnami/kube-prometheus

  helm uninstall --namespace tfmodels tf-serving-chart
  helm uninstall --namespace monitoring prometheus-chart
  ```


## References

- https://github.com/thisisclement/Prometheus-TF-Serving
- https://github.com/bitnami/charts/tree/main/bitnami/mongodb
- https://www.youtube.com/watch?v=JGtJj_nAA2s
- https://www.youtube.com/watch?v=A-3RESuvjxo
- https://www.iguazio.com/blog/introduction-to-tf-serving/
- https://github.com/bentoml/Yatai
- https://medium.com/fourthline-tech/how-to-visualize-tensorflow-metrics-in-kibana-761268353ca3
- https://blog.krudewig-online.de/2021/02/22/Multicluster-Monitoring-with-Prometheus.html
- https://github.com/bitnami/charts/tree/main/bitnami/kube-prometheus
