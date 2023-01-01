import os
import tensorflow as tf


class HalfPlusTen(tf.Module):
    """ Custom module """

    def __init__(self):
        super(HalfPlusTen, self).__init__()

    @tf.function(input_signature=[tf.TensorSpec([None], tf.float32)])
    def __call__(self, x):
        return {'y': tf.constant(.5) * x + tf.constant(10.)}


class HalfPlusTenAgain(tf.Module):
    """ Custom module """

    def __init__(self):
        super(HalfPlusTenAgain, self).__init__()

    @tf.function(input_signature=[tf.TensorSpec([None], tf.float32)])
    def __call__(self, x):
        return {'y': tf.constant(.55) * x + tf.constant(10.)}


def export(model_path: str):
    """ Store a custom model """

    path_v1 = os.path.join(model_path, 'half_plus_ten', '1')
    path_v2 = os.path.join(model_path, 'half_plus_ten', '2')

    os.makedirs(model_path, exist_ok=True)

    module = HalfPlusTen()
    tf.saved_model.save(module, path_v1)

    module = HalfPlusTenAgain()
    tf.saved_model.save(module, path_v2)
