"""
"""

import hashlib
import uuid


SALT_DELIMITER = '$'


class BadPasswordError(Exception):
    pass


class BadAccessTokenError(Exception):
    pass


def create_user_in_db(email, password, db):
    salt = str(uuid.uuid4())
    password_hash = hashlib.md5('%s%s%s' % (salt, SALT_DELIMITER, password)).hexdigest()
    salted_password = '%s%s%s' % (salt, SALT_DELIMITER, password_hash)
    store_password_in_db(email, salted_password, db)


def authenticate_using_password(email, password, db):
    stored_password = get_user_password_from_db(email, db)
    parts = stored_password.split(SALT_DELIMITER)
    salt = parts[0]
    password_hash = hashlib.md5('%s%s%s' % (salt, SALT_DELIMITER, password)).hexdigest()
    if password_hash == parts[1]:
        # TODO: authetication successful
    else:
        raise BadPasswordError()


def store_password_in_db(email, password, db):
    # TODO:
    pass


def get_user_password_from_db(email, db):
    # TODO:
    pass


def authenticate_using_access_token(user_id, access_token, db):
    pass


"""
try:
    authenticate_using_password(email, password)
except BadPasswordError:
    # TODO: send error JSON response
    pass
# TODO: send successful login response
"""


