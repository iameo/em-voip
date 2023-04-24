import uuid


def db_id_maker(title):
    #generate a UUID hex file with given title
    return f"{title}__{uuid.uuid4().hex}"
