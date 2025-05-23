from petname import Generate


def generate():
    """Generate a random name using petname."""
    return Generate(words=3, separator="-")  # TODO move const to app settings
