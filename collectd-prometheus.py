# -*- coding: utf-8 -*-

import collectd
import requests
import signal
import json
import re

from prometheus_client.parser import text_string_to_metric_families

PLUGIN_NAME = 'prometheus'

DEFAULT_INTERVAL = 30
DEFAULT_TIMEOUT = 30
DEFAULT_PROTOCOL = 'http'
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = '8080'
DEFAULT_PROCESS = 'unknown'

# Config options
KEY_PROCESS = 'Process'
KEY_PROTOCOL = 'Protocol'
KEY_INTERVAL = 'Interval'
KEY_PORT = 'Port'
KEY_HOST = 'Host'
KEY_REGEX_FILTER = 'Filter'
KEY_TIMEOUT = 'Timeout'
KEY_SSL_IGNORE = 'SslIgnore'
KEY_SSL_CERT = 'SslCert'
KEY_SSL_KEY = 'SslKey'
KEY_SSL_CACERT = 'SslCacert'

class PrometheusProcess(object):
    """
    Plugin that parse prometheus metrics to collectd.
    """
    def __init__(self):
        self.process = DEFAULT_PROCESS
        self.host = DEFAULT_HOST
        self.port = DEFAULT_PORT
        self.protocol = DEFAULT_PROTOCOL
        self.timeout = DEFAULT_TIMEOUT
        self.regex_filters = []
        self.ssl_ignore = None
        self.ssl_cert = None
        self.ssl_key = None
        self.ssl_cacert = None

    def config(self, cfg):
        for children in cfg.children:
            if children.key == KEY_PROCESS:
                self.process = children.values[0]
            if children.key == KEY_HOST:
                self.host = children.values[0]
            if children.key == KEY_PORT:
                self.port = children.values[0]
            if children.key == KEY_PROTOCOL:
                self.protocol = children.values[0]
            if children.key == KEY_TIMEOUT:
                self.timeout = int(children.values[0])
            if children.key == KEY_SSL_IGNORE:
                self.ssl_ignore = bool(children.values[0])
                if self.ssl_ignore:
                    import urllib3
                    urllib3.disable_warnings()
            if children.key == KEY_SSL_CERT:
                self.ssl_cert = children.values[0]
            if children.key == KEY_SSL_KEY:
                self.ssl_key = children.values[0]
            if children.key == KEY_SSL_CACERT:
                self.ssl_cacert = children.values[0]
            if children.key == KEY_REGEX_FILTER:
                self.regex_filters.append(children.values[0])
        collectd.debug(json.dumps(self.__dict__))

class Prometheus(object):
    """
    Plugin that parse prometheus metrics to collectd.
    """
    def __init__(self):
        self.interval = DEFAULT_INTERVAL
        self.process_monitored = []

    def config(self, cfg):
        for children in cfg.children:
            if children.key == KEY_INTERVAL:
                self.interval = children.values[0]
            if children.key == KEY_PROCESS:
                process_configuration = PrometheusProcess()
                process_configuration.config(children)

                self.process_monitored.append(process_configuration)
        collectd.register_read(self.read, interval = self.interval)

    def read(self):
        for process in self.process_monitored:
            kwargs = {}

            if process.ssl_ignore is not None:
                kwargs.update({'verify': not process.ssl_ignore})
            if process.ssl_cert is not None and process.ssl_key is not None:
                kwargs.update({'cert': (process.ssl_cert, process.ssl_key)})
            if process.ssl_cacert is not None:
                kwargs.update({'verify': process.ssl_cacert})
            if process.timeout is not None:
                kwargs.update({'timeout': process.timeout})

            try:
              metrics = requests.get("%s://%s:%s/metrics" % (process.protocol, process.host, process.port), **kwargs).content
              for family in text_string_to_metric_families(metrics):
                  for sample in family.samples:
                      # Normalize metric name
                      metric_name = re.sub(r'[^_a-zA-Z0-9]', '_', sample.name)
                      metric_name = re.sub(r'(?<!^)(?=[A-Z])', '_', metric_name).lower()

                      # Check if metric need to be dispatched
                      metric_match = False if len(process.regex_filters) > 0 else True
                      for metric_filter in process.regex_filters:
                          if re.compile(metric_filter).match(metric_name):
                              metric_match = True

                      if metric_match:
                          metric = collectd.Values()
                          metric.plugin = PLUGIN_NAME
                          metric.plugin_instance = process.process
                          metric.meta = sample.labels
                          metric.type = 'gauge'
                          metric.type_instance = metric_name
                          metric.values = [sample.value]
                          metric.dispatch()

                          collectd.debug("Name: {0} Labels: {1} Value: {2}".format(*sample))
                      else:
                          collectd.debug("Name: {0} not match Labels: {1} Value: {2}".format(*sample))
            except Exception as e:
                collectd.error('unable to get prometheus data %s://%s:%s/metrics with current configuration %s: %s' % (process.protocol, process.host, process.port, json.dumps(process.__dict__), e))

def init():
    signal.signal(signal.SIGCHLD, signal.SIG_DFL)

prom = Prometheus()
collectd.register_init(init)
collectd.register_config(prom.config)

