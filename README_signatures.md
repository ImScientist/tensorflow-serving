
## Test the 3 models separately

- `fashion_mnist_prob` model:
  ```shell
  saved_model_cli show --dir models/fashion_mnist_prob/1
  # The given SavedModel contains the following tag-sets: 'serve'
  
  saved_model_cli show --dir models/fashion_mnist_prob/1 --tag_set serve
  # The given SavedModel MetaGraphDef contains SignatureDefs with the following keys:
  # SignatureDef key: "__saved_model_init_op"
  # SignatureDef key: "serving_default"
  
  saved_model_cli show --dir models/fashion_mnist_prob/1 --tag_set serve --signature_def serving_default
  # The given SavedModel SignatureDef contains the following input(s):
  #   inputs['sequential_2_input'] tensor_info:
  #       dtype: DT_FLOAT
  #       shape: (-1, 28, 28)
  #       name: serving_default_sequential_2_input:0
  # The given SavedModel SignatureDef contains the following output(s):
  #   outputs['softmax_1'] tensor_info:
  #       dtype: DT_FLOAT
  #       shape: (-1, 10)
  #       name: StatefulPartitionedCall:0
  # Method name is: tensorflow/serving/predict
  
  docker run -t --rm -p 8501:8501 \
      --name=serving \
      -v $(pwd)/models/fashion_mnist_prob/1:/models/fashion_mnist_prob/1 \
      -e MODEL_NAME=fashion_mnist_prob \
      tensorflow/serving
  ```

- `half_plus_two_cpu` model:
    ```shell
    saved_model_cli show --dir models/half_plus_two_cpu/1
    # The given SavedModel contains the following tag-sets: 'serve'
    
    saved_model_cli show --dir models/half_plus_two_cpu/1 --tag_set serve
    # The given SavedModel MetaGraphDef contains SignatureDefs with the following keys:
    # SignatureDef key: "classify_x_to_y"
    # SignatureDef key: "regress_x2_to_y3"
    # SignatureDef key: "regress_x_to_y"
    # SignatureDef key: "regress_x_to_y2"
    # SignatureDef key: "serving_default"
    
    saved_model_cli show --dir models/half_plus_two_cpu/1 --tag_set serve --signature_def serving_default
    # The given SavedModel SignatureDef contains the following input(s):
    #   inputs['x'] tensor_info:
    #       dtype: DT_FLOAT
    #       shape: (-1, 1)
    #       name: x:0
    # The given SavedModel SignatureDef contains the following output(s):
    #   outputs['y'] tensor_info:
    #       dtype: DT_FLOAT
    #       shape: (-1, 1)
    #       name: y:0
    # Method name is: tensorflow/serving/predict
    
    docker run -t --rm -p 8501:8501 \
        --name=serving \
        -v $(pwd)/models/half_plus_two_cpu/1:/models/half_plus_two_cpu/1 \
        -e MODEL_NAME=half_plus_two_cpu \
        tensorflow/serving
    
    curl -X POST http://localhost:8501/v1/models/half_plus_two_cpu:predict \
         -H 'Content-type: application/json' \
         -d '{"signature_name": "serving_default", "instances": [{"x": [0, 1, 2]}]}'
    ```

- `half_plus_three` model:
    ```shell
    saved_model_cli show --dir models/half_plus_three/1
    # The given SavedModel contains the following tag-sets: 'serve'
    
    saved_model_cli show --dir models/half_plus_three/1 --tag_set serve
    # The given SavedModel MetaGraphDef contains SignatureDefs with the following keys:
    # SignatureDef key: "serving_default"
    # SignatureDef key: "tensorflow/serving/regress"
    
    saved_model_cli show --dir models/half_plus_three/1 --tag_set serve --signature_def serving_default
    # The given SavedModel SignatureDef contains the following input(s):
    #   inputs['x'] tensor_info:
    #       dtype: DT_FLOAT
    #       shape: ()
    #       name: x:0
    # The given SavedModel SignatureDef contains the following output(s):
    #   outputs['y'] tensor_info:
    #       dtype: DT_FLOAT
    #       shape: ()
    #       name: y:0
    # Method name is: tensorflow/serving/predict

    docker run -t --rm -p 8501:8501 \
        --name=serving \
        -v $(pwd)/models/half_plus_three/1:/models/half_plus_three/1 \
        -e MODEL_NAME=half_plus_three \
        tensorflow/serving
    
    curl -X POST http://localhost:8501/v1/models/half_plus_three:predict \
         -H 'Content-type: application/json' \
         -d '{"signature_name": "serving_default", "instances": [{"x": [0, 1, 2]}]}'
    ```

- `half_plus_ten` model:
    ```shell
    saved_model_cli show --dir models/half_plus_ten/1
    # The given SavedModel contains the following tag-sets: 'serve'
    
    saved_model_cli show --dir models/half_plus_ten/1 --tag_set serve
    # The given SavedModel MetaGraphDef contains SignatureDefs with the following keys:
    # SignatureDef key: "__saved_model_init_op"
    # SignatureDef key: "serving_default"

    saved_model_cli show --dir models/half_plus_ten/1 --tag_set serve --signature_def serving_default
    # The given SavedModel SignatureDef contains the following input(s):
    #   inputs['x'] tensor_info:
    #       dtype: DT_FLOAT
    #       shape: (-1)
    #       name: serving_default_x:0
    # The given SavedModel SignatureDef contains the following output(s):
    #   outputs['y'] tensor_info:
    #       dtype: DT_FLOAT
    #       shape: (-1)
    #       name: PartitionedCall:0
    # Method name is: tensorflow/serving/predict

    docker run -t --rm -p 8501:8501 \
        --name=serving \
        -v $(pwd)/models/half_plus_ten/1:/models/half_plus_ten/1 \
        -e MODEL_NAME=half_plus_ten \
        tensorflow/serving

    curl -X POST http://localhost:8501/v1/models/half_plus_ten:predict \
         -H 'Content-type: application/json' \
         -d '{"signature_name": "serving_default", "instances": [{"x": [0, 1, 2]}]}'
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

  helm lint tf-serving
  helm install tf-serving-chart --debug --dry-run --namespace tfmodels tf-serving  
  
  kubectl --namespace monitoring port-forward $POD_NAME 8501:$CONTAINER_PORT
  # kubectl port-forward svc/...

    
  helm install -n monitoring --debug --dry-run prometheus-chart bitnami/kube-prometheus
   
  helm install -f values_prometheus.yaml -n monitoring \
      --debug --dry-run prometheus-chart bitnami/kube-prometheus
  
  helm install -f values_prometheus.yaml -n monitoring prometheus-chart bitnami/kube-prometheus
  helm uninstall -n monitoring prometheus-chart
  
  helm install -n monitoring my-prometheus bitnami/kube-prometheus
  helm uninstall -n monitoring my-prometheus
  
  helm install my-prometheus bitnami/kube-prometheus

  kubectl get deploy -w --namespace monitoring -l app.kubernetes.io/name=kube-prometheus-operator,app.kubernetes.io/instance=my-prometheus
  kubectl get sts -w --namespace monitoring -l app.kubernetes.io/name=kube-prometheus-prometheus,app.kubernetes.io/instance=my-prometheus
  kubectl get sts -w --namespace monitoring -l app.kubernetes.io/name=kube-prometheus-alertmanager,app.kubernetes.io/instance=my-prometheus
  
  # Prometheus can be accessed via port "9090" on the following DNS name from within your cluster:
  # my-prometheus-kube-prometh-prometheus.monitoring.svc.cluster.local
  # kubectl port-forward --namespace monitoring svc/my-prometheus-kube-prometh-prometheus 9090:9090
  # http://127.0.0.1:9090/

  Alertmanager can be accessed via port "9093" on the following DNS name from within your cluster:
  
      my-prometheus-kube-prometh-alertmanager.monitoring.svc.cluster.local
  
  To access Alertmanager from outside the cluster execute the following commands:
  
      echo "Alertmanager URL: http://127.0.0.1:9093/"
      kubectl port-forward --namespace monitoring svc/my-prometheus-kube-prometh-alertmanager 9093:9093

  
  
  kubectl -n monitoring get deploy/sts
  
  ```
  - prometheus:
    - server
    - alertmanager
    - deployments: prom operator (created prometheus and alertmanager stateful sets)
  - grafana
  - kubestate metrics
  - Daemonset: node exporter (runs on every worker node); connects to serevr; translates Worker node metrics to Prometheus metrics
  - use `kubectrl describe deployment <depl name> > file.yaml`
    `...-oper-prometheus`, `...-oper-alertmanager`, `...-oper-operator`



## Try stuff with Docker volumes and persistent volumes and persistent volume claims

- Docker volume: Copy all models that will be deployed to a separate docker volume:
  ```shell
  docker volume create --name tf_models
  
  docker container create --name dummy -v tf_models:/root/models hello-world
  docker cp ./models/ dummy:/root/
  docker rm dummy
  
  # Check if the models were copied in the tf_models volume 
  docker run -it --rm --name temp -v tf_models:/root/models alpine /bin/sh
  ls root/models/
  exit
  ```

- Test that you can mount the container:
  ```shell
    
  # -v "$(pwd)/models/:/models/"
  
  docker run -t --rm -p 8501:8501 -p 8500:8500\
      --name=serving \
      -v tf_models:/models \
      tensorflow/serving \
      --model_config_file=/models/models.config \
      --allow_version_labels_for_unavailable_models=true \
      --model_config_file_poll_wait_seconds=60
  ```

- K8 persistent volume: create a Docker container that contains the models:
  ```shell
  # Create a container with the content that we, eventually, will to move to a pv
  docker build -t nginx_data:latest -f k8_volume/Dockerfile .
  
  # check if everything is there
  docker run -it --rm --name=delete_me nginx_data:latest /bin/sh 
  
  # Create a persistent volume and a persistent volume claim
  kubectl apply -f k8_volume/volume.yml
  
  # Copy the models from the container to the pv
  kubectl apply -f k8_volume/pod.yml
  
  # 
  docker build -t delete_me:lalala -f k8_volume/Dockerfile_again .
  
  # .....
  docker run -t --rm -p 8501:8501 -p 8500:8500\
      --name=serving \
      delete_me:lalala \
      --model_config_file=/models/models.config \
      --allow_version_labels_for_unavailable_models=true \
      --model_config_file_poll_wait_seconds=60
  ```
