import time


def wait_until(predicate, timeout, period=0.25, *args, **kwargs) -> bool:
    """
    Wait until a predicate is true or timeout is reached.
    :param predicate:
    :param timeout:
    :param period:
    :param args:
    :param kwargs:
    :return:
    """
    must_end = time.time() + timeout
    while time.time() < must_end:
        if predicate(*args, **kwargs):
            return True
        time.sleep(period)
    return False
