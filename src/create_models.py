import os
import tensorflow as tf


class HalfPlusTwo(tf.Module):
    """ Custom module """

    def __init__(self):
        super(HalfPlusTwo, self).__init__()

    @tf.function(input_signature=[tf.TensorSpec([None], tf.float32)])
    def __call__(self, x):
        return {'y': tf.constant(.5) * x + tf.constant(2.)}


class HalfPlusTen(tf.Module):
    """ Custom module """

    def __init__(self):
        super(HalfPlusTen, self).__init__()

    @tf.function(input_signature=[tf.TensorSpec([None], tf.float32)])
    def __call__(self, x):
        return {'y': tf.constant(.6) * x + tf.constant(10.)}


class HalfPlusTenAgain(tf.Module):
    """ Custom module """

    def __init__(self):
        super(HalfPlusTenAgain, self).__init__()

    @tf.function(input_signature=[tf.TensorSpec([None], tf.float32)])
    def __call__(self, x):
        return {'y': tf.constant(.5) * x + tf.constant(10.)}


def export(model_path: str):
    """ Store a custom model """

    os.makedirs(model_path, exist_ok=True)

    module = HalfPlusTwo()
    path = os.path.join(model_path, 'half_plus_two', '1')
    tf.saved_model.save(module, path)

    module = HalfPlusTen()
    path = os.path.join(model_path, 'half_plus_ten', '1')
    tf.saved_model.save(module, path)

    module = HalfPlusTenAgain()
    path = os.path.join(model_path, 'half_plus_ten', '2')
    tf.saved_model.save(module, path)
