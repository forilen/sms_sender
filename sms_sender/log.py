import logging

FORMAT = "%(asctime)-15s %(levelname)s %(message)s"
logging.basicConfig(format=FORMAT)


class Log(object):

    def __init__(self):
        pass

    @classmethod
    def info(self, msg):
        logging.info(msg)

    @classmethod
    def warning(self, msg):
        logging.warning(msg)

    @classmethod
    def error(self, msg):
        logging.error(msg)
