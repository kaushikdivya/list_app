"""
"""

import hashlib
import uuid
import time
import MySQLdb as msql


SALT_DELIMITER = '$'


class BadPasswordError(Exception):
    pass


class BadAccessTokenError(Exception):
    pass

class NoUserExistsError(Exception):
    pass

class ManyUsersFetchedError(Exception):
    pass

# def create_user_in_db(email, password, cur):
#     salt = str(uuid.uuid4())
#     password_hash = hashlib.md5('%s%s%s' % (salt, SALT_DELIMITER, password)).hexdigest()
#     salted_password = '%s%s%s' % (salt, SALT_DELIMITER, password_hash)
#     store_password_in_db(email, salted_password, db)


def authenticate_using_password(email, password, db):
    try:
        stored_password, user_info = get_user_password_from_db(email, db)
        user_id = user_info[0]['id']
        parts = stored_password.split(SALT_DELIMITER)
        print parts
        salt = parts[0]
        password_hash = hashlib.md5('%s%s%s' % (salt, SALT_DELIMITER, password)).hexdigest()
        if password_hash == parts[1]:
                access_token = generate_access_token(email,user_id,db)
                user_info[0]['access_token'] = access_token
                print user_info
                return user_info
        # TODO: authetication successful
        else:
            raise BadPasswordError()
    except NoUserExistsError:
        raise NoUserExistsError


def store_password_in_db(email, password, db):
    # TODO:
    pass


def get_user_password_from_db(email, db):
    cur = db.cursor(msql.cursors.DictCursor)
    print email
    rows_count = cur.execute("""select u.id, u.name, u.password from users u where u.email = %s""" , (email,))
    if rows_count == 1:
        rows = cur.fetchall()
        user_info = list(rows)
        print user_info
        password = user_info[0]['password']
        print password
        type (password)
        return password, user_info
    elif rows_count == 0:
        raise NoUserExistsError()
    else:
        raise ManyUsersFetchedError()

def generate_access_token(email,user_id,db):
    access_token = hashlib.md5('%s%s' % (email,str(time.time()))).hexdigest()
    type(access_token)
    print access_token,user_id
    cur = db.cursor(msql.cursors.DictCursor)
    cur.execute("""update access_tokens set access_token = %s where user_id = %s""" , (access_token, user_id) )
    db.commit()
    return access_token

def authenticate_using_access_token(access_token, db):
    """
    returns user object if successful, else raises relveant exception
    """
    pass


"""
try:
    authenticate_using_password(email, password)
except BadPasswordError:
    # TODO: send error JSON response
    pass
# TODO: send successful login response
"""


