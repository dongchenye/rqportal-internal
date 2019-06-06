import yaml


def _default_conf():
    import os
    return os.path.join(os.path.dirname(__file__), 'conf/online.yaml')


class RQConfig:
    def __init__(self, config_file=None):
        if not config_file:
            config_file = _default_conf()
        self._conf = yaml.load(open(config_file, "rb"))

    def get(self, path):
        """
        :param path: database.feeds
        :return:
        """
        elements = path.split('.')
        conf = self._conf
        for i in range(len(elements)):
            try:
                conf = conf[elements[i]]
            except KeyError:
                print("WARN: %s does not be set in config file" % elements[i])
        return conf
