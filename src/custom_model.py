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


class CustomModule(tf.Module):

    def __init__(self):
        super(CustomModule, self).__init__()
        self.v = tf.Variable(1.)

    @tf.function
    def __call__(self, x):
        print('Tracing with', x)
        return x * self.v

    @tf.function(input_signature=[tf.TensorSpec([], tf.float32)])
    def mutate(self, new_v):
        self.v.assign(new_v)


class CustomModuleWithOutputName(tf.Module):
    def __init__(self):
        super(CustomModuleWithOutputName, self).__init__()
        self.v = tf.Variable(1.)

    @tf.function(input_signature=[tf.TensorSpec([], tf.float32)])
    def __call__(self, x):
        return {'custom_output_name': x * self.v}


def run(tmp_dir: str):
    module = CustomModule()
    module(tf.constant(0.))

    """
        No signature path.
        Related to the presence of a Variable in the decorated fn?
    """
    module_no_signatures_path = os.path.join(tmp_dir, 'module_no_signatures')
    tf.saved_model.save(module, module_no_signatures_path)

    imported = tf.saved_model.load(module_no_signatures_path)
    assert imported(tf.constant(3.)).numpy() == 3
    imported.mutate(tf.constant(2.))
    assert imported(tf.constant(3.)).numpy() == 6
    # It will not work
    # imported(tf.constant([3.]))

    """
        Add a signature
        Create signature with ConcreteFunctions
    """
    module_with_signature_path = os.path.join(tmp_dir, 'module_with_signature')
    call = module.__call__.get_concrete_function(tf.TensorSpec(None, tf.float32))
    tf.saved_model.save(module, module_with_signature_path, signatures=call)

    imported_with_signatures = tf.saved_model.load(module_with_signature_path)
    print(list(imported_with_signatures.signatures.keys()))

    """
        Multiple signatures
    """
    module_multiple_signatures_path = os.path.join(tmp_dir, 'module_with_multiple_signatures')
    signatures = {
        "serving_default": module.__call__.get_concrete_function(tf.TensorSpec(None, tf.float32)),
        "array_input": module.__call__.get_concrete_function(tf.TensorSpec([None], tf.float32))
    }
    tf.saved_model.save(module, module_multiple_signatures_path, signatures=signatures)

    imported_with_multiple_signatures = tf.saved_model.load(module_multiple_signatures_path)
    print(list(imported_with_multiple_signatures.signatures.keys()))

    # module = HalfPlusTen()
    # # _ = module(tf.constant([1.]))
    #
    # signatures = {
    #     "serving_default": module.__call__.get_concrete_function(tf.TensorSpec(None, tf.float32))
    # }
    #
    # tf.saved_model.save(module, save_path, signatures=signatures)
