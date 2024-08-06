import logging
import json

def prefix_log(logger, prefix, msg, lvl='debug'):
    if prefix is None:
        prefix == __name__

    msg = str(msg)

    getattr(logger, lvl)(
        f'{prefix} - {msg}'
    )

def json_logger(logger, prefix, msg_dict, lvl='debug'):
    msg = json.dumps(msg_dict, indent=False)
    prefix_log(logger, prefix, msg, lvl)


def create_logger():

    # create logger
    logger = logging.getLogger('main_service')
    logger.setLevel(logging.DEBUG)

    # # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # # add formatter to ch
    ch.setFormatter(formatter)

    # # add ch to logger
    logger.addHandler(ch)

    logger.info('Started WGO Logger')

    return logger


wgo_logger = create_logger()



