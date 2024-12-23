"""
    Example how to export metrics to a Pushgateway
"""

import time
import logging
import numpy as np
import pandas as pd
from prometheus_client import Gauge, CollectorRegistry, push_to_gateway

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-6s [%(name)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)

PUSHGATEWAY_URL = 'localhost:9091'

registry = CollectorRegistry()

g = Gauge(
    name='results_test',
    documentation='results on test set',
    labelnames=('country', 'metric'),
    registry=registry)


def generate_data(seed: int = None) -> pd.DataFrame:
    """ Generate a table with the columns country | rmse | mae """

    np.random.seed(seed)

    data = pd.DataFrame()
    data['country'] = ['DE', 'US', 'GB', 'IT', 'FR']
    data['rmse'] = np.random.exponential(size=(5,)).round(2)
    data['mae'] = np.random.exponential(size=(5,)).round(2)

    return data


def record_predictions(seed: int = None) -> None:
    """ Record predictions to Prometheus """

    # -> {'country': [], 'rmse': [], 'mae': []}
    data = generate_data(seed=seed).to_dict(orient='list')

    for country, rmse, mae in zip(data['country'], data['rmse'], data['mae']):
        logger.info(f'country, rmse, mae: {country}, {rmse}, {mae}')
        g.labels(country, 'rmse').set(rmse)
        g.labels(country, 'mae').set(mae)

    logger.info('Push to gateway')
    push_to_gateway(PUSHGATEWAY_URL, job='batch_training', registry=registry)


if __name__ == '__main__':

    counter = 0

    while True:
        record_predictions(counter)
        time.sleep(30)
        counter += 1
