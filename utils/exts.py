def generate_id(n, is_alphanum=True):
    """
    generate a random ID of length n

    args:
        n: length of ID
        is_alphanum: True to return an alphanumeric str otherwise False
    """
    import random, string
    _id = ''.join(["{}".format(random.randint(0,9)) for num in range(0,n)])
    if is_alphanum:
        alphanum = string.ascii_letters + string.digits
        _id = ''.join(random.choice(alphanum) for i in range(0,n))
    return _id

def random_label(prefix="LABEL", n=7):
    """return random generated label name; ideally for conference test"""
    return f"{prefix}-{generate_id(n)}"

def random_client_name(prefix="CLIENT"):
    """return randomly generated client name"""
    return f"Agent-{generate_id(5)}"
    