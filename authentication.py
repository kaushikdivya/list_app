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

class UserAlreadyExists(Exception):
    pass

class AccessTokenExpiredError(Exception):
    pass

class NoUserExistsWithThisAccessTokenError(Exception):
    pass


def create_user_in_db(name, email, password, db):
    cur = db.cursor(msql.cursors.DictCursor)
    cur.execute("""select u.id from users u where email = %s""" , (email,)) #neeed to add users with deleted_time
    print cur.rowcount
    if cur.rowcount > 0:
        raise UserAlreadyExists
    else:
        salt = str(uuid.uuid4())
        password_hash = hashlib.md5('%s%s%s' % (salt, SALT_DELIMITER, password)).hexdigest()
        salted_password = '%s%s%s' % (salt, SALT_DELIMITER, password_hash)
        insert_status = cur.execute("""insert into users (name, email, password) values (%s,%s,%s)""" , (name, email, salted_password))
        commit_status = db.commit()
        print insert_status, commit_status

def authenticate_using_password(email, password, db):
    stored_password, user_info = get_user_password_from_db(email, db)
    user_id = user_info['id']
    parts = stored_password.split(SALT_DELIMITER)
    print parts
    salt = parts[0]
    password_hash = hashlib.md5('%s%s%s' % (salt, SALT_DELIMITER, password)).hexdigest()
    if password_hash == parts[1]:
            access_token = generate_access_token(email,user_id,db)
            user_info['access_token'] = access_token
            print user_info
            return user_info
    # TODO: authetication successful
    else:
        raise BadPasswordError()


# def authenticate_using_access_token(email, password, db):
#     # TODO:
#     pass


def get_user_password_from_db(email, db):
    cur = db.cursor(msql.cursors.DictCursor)
    print email
    rows_count = cur.execute("""select u.id, u.name, u.password from users u where u.email = %s and u.deleted_time is null""" , (email,))
    if rows_count == 1:
        user_info = cur.fetchone()
        print user_info
        password = user_info['password']
        print password
        type (password)
        return password, user_info
    elif rows_count == 0:
        raise NoUserExistsError()
        #Should there be a check for mutiple users with same email though that is taken care at the db side.????????

def generate_access_token(email,user_id,db):
    access_token = hashlib.md5('%s%s' % (email,str(time.time()))).hexdigest()
    type(access_token)
    print access_token,user_id
    cur = db.cursor(msql.cursors.DictCursor)
    cur.execute("""insert into access_tokens (user_id, access_token) values (%s, %s )""" , (user_id, access_token))
    db.commit()
    return access_token

def authenticate_using_access_token(access_token, db):
    """
    returns user object if successful, else raises relveant exception
    """
    cur = db.cursor(msql.cursors.DictCursor)
    rows_count = cur.execute("""select a.user_id, a.created_time, a.deleted_time from access_tokens a where a.access_token = %s""" , (access_token,))
    if rows_count == 0:
        raise NoUserExistsWithThisAccessTokenError
    elif rows_count == 1:
        row = cur.fetchone()
        user_id = row[0]['user_id']
        created_time = row[0]['created_time']
        deleted_time = row[0]['deleted_time']
        if deleted_time == 'null':
            raise AccessTokenExpiredError
        else:
            cur.execute("""select u.id, u.name from users u where u.id = %s""" , (user_id,))
            user_tup = cur.fetchone()
            user_info = user_tup[0]
            return user_info



"""
try:
    authenticate_using_password(email, password)
except BadPasswordError:
    # TODO: send error JSON response
    pass
# TODO: send successful login response
"""


