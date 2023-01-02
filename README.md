# tensorflow-serving

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

## Serve multiple models

- We have to create a Model Server config file (in `$(pwd)/models/models.config`):
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
- REST API:
  ```shell
  # /v1/models/<model name>
  # /v1/models/<model name>/versions/<version number>
  # /v1/models/<model name>/labels/<version label>.
  
  curl -X POST http://localhost:8501/v1/models/half_plus_three:predict \
       -H 'Content-type: application/json' \
       -d '{"signature_name": "serving_default", "instances": [{"x": [0, 1, 2]}]}'

  curl -X POST http://localhost:8501/v1/models/half_plus_two_cpu:predict \
       -H 'Content-type: application/json' \
       -d '{"signature_name": "serving_default", "instances": [{"x": [0, 1, 2]}]}'
  
  curl -X POST http://localhost:8501/v1/models/half_plus_ten/versions/2:predict \
       -H 'Content-type: application/json' \
       -d '{"signature_name": "serving_default", "instances": [{"x": [0, 1, 2]}]}'
  
  curl -X POST http://localhost:8501/v1/models/half_plus_ten/labels/canary:predict \
       -H 'Content-type: application/json' \
       -d '{"signature_name": "serving_default", "instances": [{"x": [0, 1, 2]}]}'
  ```

## Monitoring with Prometheus and Visualization with Grafana

- Create a `models/monitoring.config` file with the following content:
  ```
  prometheus_config {
    enable: true,
    path: "/monitoring/prometheus/metrics"
  }
  ```


- Create a `promeheus.yml` file. The `scrape_configs.metrics_path` matches the endpoint exposed in `models/monitoring.config`.


- Use docker-compose to allow all services to communicate with each other:
  ```shell
  docker-compose up
  ```


- From `docker-compose.yml` you can see that:
  - to read metrics from the `/monitoring/prometheus/metrics` we have enabled the HTTP server by setting `--rest_api_port=8501` and `--monitoring_config_file=/models/monitoring.config`. You can verify that the metrics are exposed by visiting `http://localhost:8501/monitoring/prometheus/metrics`.
  
  - you should be able to access the Prometheus web UI through `localhost:9090`.
 
  - you should be able to access the Grafana WebUI through `localhost:3000`. The username and password are `admin` and `admin`, respectively. In the WebUI you can add a new datasource with the url `http://prometheus:9090`


## Kubernetes

- Copy all models that will be deployed to a separate docker volume.
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
  

## References

- https://github.com/thisisclement/Prometheus-TF-Serving
- https://github.com/bitnami/charts/tree/main/bitnami/mongodb
- https://www.youtube.com/watch?v=JGtJj_nAA2s
- https://www.youtube.com/watch?v=A-3RESuvjxo
- https://www.iguazio.com/blog/introduction-to-tf-serving/
- https://github.com/bentoml/Yatai
- https://medium.com/fourthline-tech/how-to-visualize-tensorflow-metrics-in-kibana-761268353ca3