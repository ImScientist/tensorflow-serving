"""
    There is another link:
        https://www.tensorflow.org/tfx/tutorials/serving/rest_simple
"""
import os
import json
import logging
import requests
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

tfkl = tf.keras.layers

logger = logging.getLogger()
logger.setLevel(logging.INFO)

CLASS_NAMES = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
               'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']


def plot_image(img, predictions_array=None, true_label=None):
    """ Plot image """
    plt.grid(False)
    plt.xticks([])
    plt.yticks([])

    plt.imshow(img, cmap=plt.cm.binary)

    if predictions_array is not None and true_label is not None:
        predicted_label = np.argmax(predictions_array)

        color = 'blue' if predicted_label == true_label else 'red'

        plt.xlabel("{} {:2.0f}% ({})".format(CLASS_NAMES[predicted_label],
                                             100 * np.max(predictions_array),
                                             CLASS_NAMES[true_label]),
                   color=color)


def plot_value_array(predictions_array, true_label):
    """ Barplot of predicted probabilities for every class """

    plt.grid(False)
    plt.xticks(range(10))
    plt.yticks([])
    thisplot = plt.bar(range(10), predictions_array, color="#777777")
    plt.ylim([0, 1])
    predicted_label = np.argmax(predictions_array)

    thisplot[predicted_label].set_color('red')
    thisplot[true_label].set_color('blue')


def create_model():
    """ Create a model """

    model = tf.keras.Sequential([
        tfkl.Rescaling(scale=1. / 255, input_shape=(28, 28)),
        tfkl.Flatten(),  # TODO: remove input_shape=(28, 28)
        tfkl.Dense(128, activation='relu'),
        tfkl.Dense(10)
    ])

    model.compile(
        optimizer='adam',
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=['accuracy'])

    probability_model = tf.keras.Sequential([
        model,
        tf.keras.layers.Softmax()])

    return model, probability_model


def show_training_data(images, labels):
    """ Show the training data """
    plot_image(images[0])

    plt.figure(figsize=(10, 10))
    for i in range(25):
        plt.subplot(5, 5, i + 1)
        plt.xticks([])
        plt.yticks([])
        plt.grid(False)
        plt.imshow(images[i], cmap=plt.cm.binary)
        plt.xlabel(CLASS_NAMES[labels[i]])
    plt.show()


def train(save_dir: str):
    """ Train model """

    fashion_mnist = tf.keras.datasets.fashion_mnist

    (train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()

    show_training_data(images=train_images, labels=train_labels)

    model, probability_model = create_model()
    model.fit(train_images, train_labels, epochs=10)

    test_loss, test_acc = model.evaluate(test_images, test_labels, verbose=2)
    logger.info(f'test_loss: {test_loss}\n'
                f'test_acc: {test_acc}')

    # output shape = (None, n_classes)
    predictions = probability_model.predict(test_images)

    # Verify predictions
    num_rows = 5
    num_cols = 3
    num_images = num_rows * num_cols
    plt.figure(figsize=(2 * 2 * num_cols, 2 * num_rows))

    for i in range(num_images):
        img = test_images[i]
        predictions_array = predictions[i]
        true_label = test_labels[i]

        # plt.figure(figsize=(6, 3))
        # plt.subplot(1, 2, 1)
        plt.subplot(num_rows, 2 * num_cols, 2 * i + 1)
        plot_image(img=img, predictions_array=predictions_array, true_label=true_label)

        # plt.subplot(1, 2, 2)
        plt.subplot(num_rows, 2 * num_cols, 2 * i + 2)
        plot_value_array(predictions_array=predictions_array, true_label=true_label)
        # plt.show()

    plt.tight_layout()
    plt.show()

    """
        Single image prediction
    """
    img = np.expand_dims(test_images[1], 0)
    predictions_single = probability_model.predict(img)
    logger.info(f'single prediction: {predictions_single}')

    # Save the probability_model
    os.makedirs(save_dir, exist_ok=True)
    probability_model.save(save_dir)

    """
        Single image prediction with REST call
    """
    # Both work
    data = json.dumps({
        "signature_name": "serving_default",
        "instances": test_images[0:3].tolist()
    })

    # TODO: not unique
    data = json.dumps({
        "signature_name": "serving_default",
        "instances": [{'sequential_2_input': test_images[0:3].tolist()}]
    })

    headers = {"content-type": "application/json"}
    json_response = requests.post(
        'http://localhost:8501/v1/models/fashion_mnist_prob:predict',
        data=data,
        headers=headers)
    logger.info(f'json_response: {json_response}')

    predictions = json.loads(json_response.text)['predictions']
    logger.info(f'predictions: {predictions}')
