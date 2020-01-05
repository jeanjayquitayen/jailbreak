import logging
import datetime



# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create file handler and set level to debug
ch = logging.FileHandler("../captures/" + datetime.datetime.now().strftime("%m-%d-%Y-%I-%M-%S") + ".log")
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to loggerDEBUG
logger.addHandler(ch)

    # def debug(self, message):
    #     self.logger.debug(message)
    # def info(self, message):
    #     self.logger.info(message)
    # def warning(self, message):
    #     self.logger.warning(message)
    # def error(self, message):
    #     self.logger.error(message)
    # def critical(self, message):
    #     self.logger.critical(message)

if __name__ == "__main__":
    logger = Logger()
    logger.create_logger()
    logger.debug