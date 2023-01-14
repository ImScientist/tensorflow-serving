# Monitor deployed tensorflow models with Prometheus and Grafana

### Table of Contents

1. [Create and serve multiple models](#1-Create-and-serve-multiple-models)
2. [Monitoring with Prometheus and Visualization with Grafana using docker-compose](#2-monitoring-with-prometheus-and-visualization-with-grafana-using-docker-compose)
3. [Monitoring with Prometheus and Visualization with Grafana using Kubernetes](#3-monitoring-with-prometheus-and-visualization-with-grafana-using-kubernetes)
4. [References](#4-references)

### 1 Create and serve multiple models

- We have to create and export the models that will be served. They will be stored in the `models` directory:
  ```shell
  python create_models.py
  ```

- We have to use the model server config file in `models/models.config` that specifies the locations of all exposed
  models:
  ```shell
  docker run -t --rm -p 8501:8501 -p 8500:8500\
      --name=serving \
      -v "$(pwd)/models/:/models/" \
      tensorflow/serving:2.11.0 \
      --model_config_file=/models/models.config \
      --allow_version_labels_for_unavailable_models=true \
      --model_config_file_poll_wait_seconds=60
  ```
  The `--model_config_file_poll_wait_seconds=60` option means that the server polls model updates every 60s.


- Test the REST API:
  ```shell
  # model paths  
  # /v1/models/<model name>
  # /v1/models/<model name>/versions/<version number>
  # /v1/models/<model name>/labels/<version label>
  
  MODEL_PATH=half_plus_two/versions/1
  MODEL_PATH=half_plus_ten/labels/stable
  MODEL_PATH=half_plus_ten/labels/canary

  curl -X POST http://localhost:8501/v1/models/${MODEL_PATH}:predict \
      -H 'Content-type: application/json' \
      -d '{"signature_name": "serving_default", "instances": [{"x": [0, 1, 2]}]}'
  ```

### 2 Monitoring with Prometheus and Visualization with Grafana using docker-compose

- We will use the `models/monitoring.config` file that exposes a path that can be scraped by prometheus.


- In addition, we will use the `prometheus_docker_compose.yml` file. The `scrape_configs.metrics_path` matches the path
  exposed
  in `models/monitoring.config`.


- You can start the three services with `docker-compose up`.


- From `docker-compose.yml` you can see that:
    - to read metrics from `/monitoring/prometheus/metrics` we had to set `--rest_api_port=8501`
      and `--monitoring_config_file=/models/monitoring.config`. You can verify that the metrics are exposed by
      visiting `http://localhost:8501/monitoring/prometheus/metrics`.

    - you should be able to access the Prometheus web UI through `localhost:9090`. You can also execute the
      query `:tensorflow:serving:request_count` and see what happens.

    - you should be able to access the Grafana WebUI through `localhost:3000`. The username and password are `admin`
      and `admin`, respectively. In the WebUI you can add a new datasource with the url `http://prometheus:9090`.

    - you can access the models with the same requests that you have used in the previous section.


- You can stop the three services with `docker-compose down`.

### 3 Monitoring with Prometheus and Visualization with Grafana using Kubernetes

- Tensorflow server

    - In the ideal case we have to mount a volume that contains the models into the pod running the tensorflow server.
      In
      order to make local testing easier we will just extend the tensorflow server image by adding to it the models:
      ```shell
      docker build -t tf-server:1.0.0 -f Dockerfile .
  
      # Create the server
      kubectl create namespace tfmodels
      helm install --namespace tfmodels tf-serving-chart helm/tf-serving
      ```

    - From the `values.yaml` in the helm chart for the tensorflow server you can see that:
        - we have enabled only the service component but not the ingress component. This has to be changed at some
          point.
        - we are pulling the locally stored tensorflow server image by setting `pullPolicy: Never`
          in `tf-serving/values.yaml`.

    - Besides `values.yaml`, `Chart.yaml` and `templates/deplyment.yaml` we have not changed the default template.
    - Since we have used a service of type LoadBalancer we can make API calls to the service in the same way as we did before.


- Prometheus
    - Customize Scrape Configurations: the possible options are explained in detail in
      the [official documentation](https://docs.bitnami.com/kubernetes/apps/prometheus-operator/configuration/customize-scrape-configurations/). We will define the scrape configurations to be managed by the prometheus Helm chart. The
      settings can be found in `prometheus_helm.yaml`. We are using the prometheus service
      discovery `kubernetes_sd_configs` to monitor the tensorflow server pods. More information how this works can be
      found in this [blog post](https://blog.krudewig-online.de/2021/02/22/Multicluster-Monitoring-with-Prometheus.html)
      .

    - Launch prometheus with:
      ```shell
      kubectl create namespace monitoring
      helm install --namespace monitoring \
        -f prometheus_helm.yaml \
        prometheus-chart bitnami/kube-prometheus
      ```
      You should get a message telling you under which DNS from within the cluster Prometheus can be accessed. 
      ```shell
      Prometheus can be accessed via port "9090" on the following DNS name from within your cluster:
      
        prometheus-chart-kube-prom-prometheus.monitoring.svc.cluster.local
      ```
      To access Prometheus from outside the cluster execute the following command:
      ```shell
      kubectl -n monitoring port-forward svc/prometheus-chart-kube-prom-prometheus 9090:9090
      # Browse to http://127.0.0.1:9090"
      ```


- Grafana
  - Launch Grafana with:
    ```shell
    helm install --namespace monitoring \
      grafana-chart bitnami/grafana
    ```
    To access Grafana from outside the cluster execute the following command:
    ```shell
    kubectl -n monitoring port-forward svc/grafana-chart 8081:3000 &
    # Browse to http://127.0.0.1:8081" to access the service
    ```
  - You can add Prometheus as a datasource by using the previously obtained prometheus DNS name as a datasource URL: `http://prometheus-chart-kube-prom-prometheus.monitoring.svc.cluster.local:9090`.


- Remove all services:
  ```shell
  helm uninstall --namespace tfmodels tf-serving-chart
  helm uninstall --namespace monitoring prometheus-chart
  helm uninstall --namespace monitoring grafana-cahrt
  ```

### 4 References


$$
\Gamma(z) = \int_0^\infty t^{z-1}e^{-t}dt\,.
$$



- https://github.com/thisisclement/Prometheus-TF-Serving
- https://github.com/bitnami/charts/tree/main/bitnami/mongodb
- https://www.youtube.com/watch?v=JGtJj_nAA2s
- https://www.youtube.com/watch?v=A-3RESuvjxo
- https://www.iguazio.com/blog/introduction-to-tf-serving/
- https://github.com/bentoml/Yatai
- https://medium.com/fourthline-tech/how-to-visualize-tensorflow-metrics-in-kibana-761268353ca3
- https://blog.krudewig-online.de/2021/02/22/Multicluster-Monitoring-with-Prometheus.html
- https://github.com/bitnami/charts/tree/main/bitnami/kube-prometheus
- https://docs.bitnami.com/tutorials/create-multi-cluster-monitoring-dashboard-thanos-grafana-prometheus/
- https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/
