# Pushgateway and alerts

- Pushgateway:  
  If you are running jobs with short lifespan, instead of exposing a `/metrics` endpoint, you can actively push
  all the metrics to a Pushgateway that will live even after the jobs exits, and will be scraped by Prometheus.
    - Create a Pushgateway as follows:
      ```shell
      # helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
      
      helm install --namespace default -f helm/pushgateway/values.yaml \
          pushgateway-chart prometheus-community/prometheus-pushgateway
      ```
    - To access the Pushgateway from outside the cluster execute the following command:
      ```shell
      kubectl -n default port-forward svc/pushgateway-chart-prometheus-pushgateway 9091:9091
      # Browse to http://127.0.0.1:9091/
      ```
    - You can test sending metrics to the Pushgateway by running the following script:
      ```shell
      # There has to be a proxy of the pushgateway service
      python pushgateway_export_metrics.py
      ```
      Check the Pushgateway UI or `http://127.0.0.1:9091/metrics` to see the results.
    - To make the metrics stored in the Pushgateway accessible by Prometheus, we have to
      let Prometheus discover the new service by creating a new ServiceMonitor component:
      ```shell
      kubectl apply -f helm/prometheus/servicemonitor_pushgateway.yaml
      ```

- Alertmanager:  
  Try to create an alert rule:
  ```shell
  kubectl apply -f helm/prometheus/alerts.yaml
  
  # Browse http://127.0.0.1:9090/alerts
  ```
  If you have stopped executing `pushgateway_export_metrics.py` then the alert should be triggered.
