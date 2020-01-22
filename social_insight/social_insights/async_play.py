import time
import logging
from logging import StreamHandler, DEBUG

logger = logging.getLogger('async')
handler = StreamHandler()
handler.setFormatter(logging.Formatter(fmt="%(asctime)s %(message)s"))
logger.addHandler(handler)
logger.setLevel(DEBUG)


def talk_to_me(message):
    logger.info("Let's talk")
    try:
        while True:
            incoming_msg = yield
            if incoming_msg in message:
                logger.info("I will wait")
                time.sleep(3)
                logger.info("Yes you found {}".format(incoming_msg))
    except GeneratorExit:
        logger.info("Thanks for speaking")


kid = "fun loving kid"
x = talk_to_me(kid)
next(x)
for k in kid.split(' '):
    x.send(k)
