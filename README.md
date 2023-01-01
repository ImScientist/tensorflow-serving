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
  docker run -t --rm -p 8501:8501 \
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


    version_labels {
      key: 'stable'
      value: 1
    }
    version_labels {
      key: 'canary'
      value: 2
    }