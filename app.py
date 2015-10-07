"""
sample flask API
"""

import json

from flask import Flask
from flask import request
import authentication as auth
import MySQLdb as msql
import dummy_data
from authentication import BadPasswordError, NoUserExistsError

app = Flask(__name__)
app.debug = True



@app.route('/')
def hello():
    html_string="""
    <body>
        <h1>Hello World</h1>
    </body>"""
    return html_string

def connect_db():
    db = msql.connect(host = '127.0.0.1', user = 'dkaushik', passwd = 'divya123', db = 'list_app')

    return db

def authenticate_user(user_id):
    """
    returns True if user is successfully authenticated, else returns False
    """
    # TODO:
    access_token = None
    user_info = None
    for x in dummy_data.existing_users:
        if x['id'] == user_id:
            access_token = x['access_token']
            user_info = x

    if access_token == None:
        return (False, user_info)
    else:
        if access_token == request.args.get('access_token'):
            return (True, user_info)
        else:
            return (False, user_info)

def users_existence():
    username = request.form['username']
    print username, dummy_data.existing_users
    for x in dummy_data.existing_users:
        print x, x['username']
        if x['username'] == username:
            return x
    return None
@app.route('/users/login', methods=['POST'])
def users_login():

    # that's how you access query parameters
    #access_token = request.args.get('access_token', '')

    # that's how you determine what HTTP method is being called
    if request.method == 'POST':

        # that's how you access request HTTP headers
        #if not request.headers['Content-Type'].lower().startswith('application/json'):
          #  raise ValueError('POST and PUT accept only json data')
        email = request.form['email']
        password = request.form['password']
        print email , password
        db = connect_db()
        try:
            user_info = auth.authenticate_using_password(email, password, db)
            print user_info
            response_data= {
                "mata": {},
                "data": {
                    "users": [{
                        "login_status" : 'Success',
                        "id" : user_info[0]['id'],
                        "name" : user_info[0]['name'],
                        "access_token" : user_info[0]['access_token']
                    }]
                }
            }
            status = 200
        except BadPasswordError:
            response_data = {
                "meta" : {},
                "data" : {
                    "users" : [{
                    "login" : False,
                    "message" : "Wrong password"
                    }]
                }
            }
            status = 400
        except NoUserExistsError:
            response_data = {
                "meta" : {},
                "data" : {
                    "users" : [{
                        "login" : False,
                        "message" : "User doesn't exists. Sign up please"
                    }]
                }
            }
            status = 400
        body = json.dumps(response_data)
        headers = {
            'Content-Type' : 'application/json'
        }
        return (body, status, headers)

        # that's how you access request body
        #data = request.json['data']

@app.route('/users' , methods=['POST'])
def users():
    name = request.form['name']
    username = request.form['username']
    password = request.form['password']
    id = len(dummy_data.existing_users)
    access_token = hash(username+password)
    dummy_data.existing_users.append({"id" : id, "name" : name, "username": username, "password": password, "access_token" : access_token})
    response_data = {
                "meta" : {},
                "data" : {
                    "users" : [{
                    "message" : "User has been created. Login now"
                    }]
                }
            }
    status = 200
    headers = {
        'Content-Type' : 'application/json'
    }
    body = json.dumps(response_data)
    return (body, status, headers)

#response body for user info
@app.route('/users/<int:user_id>', methods=['GET', 'DELETE'])
def user_info(user_id):
    authentication , user_info = authenticate_user(user_id)
    print  user_info
    if request.method == 'GET':
        if user_info :
            if authentication:
                response_data = {
                    "meta":{},
                    "data":{
                        "users":[
                            {
                                "authentication" : True,
                                "name" : user_info['name'],
                                "id" : user_info['id'],
                                "username" : user_info['username'],
                            }
                        ]
                    }
                }
                status = 200
            else:
                response_data = {
                    "meta" : {},
                    "data" : {
                        "users" : [{
                            "authentication" : False,
                            "name" : user_info['name'],
                            "id" : user_info['id'],
                            "username" : user_info['username'],
                        }]
                    }
                }
                status = 401
        else:
            response_data = {
                "meta" : {},
                "data" : {
                    "users" : [
                        {
                            "message" : "user with user_id %d doesnot exists" % (user_id)
                        }
                    ]
                }
            }
            status = 400

    else:
        if  user_info :
            if authentication:
                user_info['id'] = None
                response_data = {
                    "meta":{},
                    "data":{
                        "users":[
                            {
                                "authentication" : True,
                                "name" : user_info['name'],
                                "id" : user_info['id'],
                                "username" : user_info['username'],
                                "delete" : "success"
                            }
                        ]
                    }
                }
                status = 200
            else:
                response_data = {
                    "meta" : {},
                    "data" : {
                        "users" : [{
                            "authentication" : False,
                            "name" : user_info['name'],
                            "id" : user_info['id'],
                            "username" : user_info['username'],
                            "delete" : "failure"
                        }]
                    }
                }
                status = 401
        else:
            response_data = {
                "meta" : {},
                "data" : {
                    "users" : [
                        {
                            "message" : "user with user_id %d doesnot exists" % (user_id),
                            "delete" : "failure"
                        }
                    ]
                }
            }
            status = 400
    body = json.dumps(response_data)
    headers = {
                 'Content-Type' : 'application/json'
            }
    return (body, status, headers)

# POST and GET http request on /lists
@app.route('/lists', methods=['POST', 'GET'])
def lists():
    access_token = request.args.get('access_token')
    # TODO: authenticate based on access_token

    #All list under that user
    if request.method == 'GET':
        response_data = {
            "meta" : {},
            "data" : {
                "lists" : [
                    {
                        "id" : 1,
                        "name" : "Grocery list",
                        "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "eggs",
                                            "quantity" : "12 pc",
                                            "status" :  "Incomplete"
                                            }
                        ]
                    },
                    {
                        "id" : 2,
                        "name" : "Shopping list",
                        "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "Anne taylor top",
                                            "quantity" : "7 pc",
                                            "status" : "incomplete"
                                            }
                        ]
                    },
                    {
                        "id" : 3,
                        "name" : "to-do list",
                        "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "Python programming",
                                            "quantity" : None,
                                            "status" : "incomplete"
                                            }
                        ]
                    }
                ]
            }
        }
        body = json.dumps(response_data)
        status = 200
        headers = {
            "Content-Type" : 'application/json'
        }
        return (body,status,headers)
    else:
        # Add new list(how to handle request data)
        new_list_name = "Household list"
        response_data = {
            "meta" : {},
            "data" : {
                "lists" : [
                    {
                        "id" : 1,
                        "name" : "Grocery list",
                        "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "eggs",
                                            "quantity" : "12 pc",
                                            "status" :  "Incomplete"
                                            }
                        ]
                    },
                    {
                        "id" : 2,
                        "name" : "Shopping list",
                        "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "Anne taylor top",
                                            "quantity" : "7 pc",
                                            "status" : "incomplete"
                                            }
                        ]
                    },
                    {
                        "id" : 3,
                        "name" : "to-do list",
                        "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "Python programming",
                                            "quantity" : None,
                                            "status" : "incomplete"
                                            }
                        ]
                    },
                    {
                        "id" : 4,
                        "name" : new_list_name,
                        "items" : [
                                            {
                                                "id" : 1,
                                                "name" : "Toilet paper",
                                                "quantity" :  "32 pc",
                                                "status" : "incomplete"
                                            }
                        ]
                    }
                ]
            }
        }
        body = json.dumps(response_data)
        status = 200
        headers = {
            "Content-Type" : 'application/json'
        }
        return (body,status,headers)

#change name of the existing list
@app.route('/lists/<int:list_id>', methods=['PUT'])
def change_list_name(list_id):
    new_name = "Vacation list"
    if list_id == 1:
        response_data = {
            "meta" : {},
            "data" : {
                "lists" : [
                    {
                        "id" : 1,
                        "name" : new_name,
                         "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "eggs",
                                            "quantity" : "12 pc",
                                            "status" :  "Incomplete"
                                            }
                        ]
                    },
                    {
                        "id" : 2,
                        "name" : "Shopping list",
                        "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "Anne taylor top",
                                            "quantity" : "7 pc",
                                            "status" : "incomplete"
                                            }
                        ]
                    },
                    {
                        "id" : 3,
                        "name" : "to-do list",
                        "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "Python programming",
                                            "quantity" : None,
                                            "status" : "incomplete"
                                            }
                        ]
                    },
                    {
                        "id" : 4,
                        "name" :  "Household list",
                        "items" : [
                                            {
                                                "id" : 1,
                                                "name" : "Toilet paper",
                                                "quantity" :  "32 pc",
                                                "status" : "incomplete"
                                            }
                        ]
                    }
                ]
            }
        }
    elif list_id == 2:
        response_data = {
            "meta" : {},
            "data" : {
                "lists" : [
                    {
                        "id" : 1,
                        "name" : "Grocery list",
                         "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "eggs",
                                            "quantity" : "12 pc",
                                            "status" :  "Incomplete"
                                            }
                        ]
                    },
                    {
                        "id" : 2,
                        "name" : new_name,
                        "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "Anne taylor top",
                                            "quantity" : "7 pc",
                                            "status" : "incomplete"
                                            }
                        ]
                    },
                    {
                        "id" : 3,
                        "name" : "to-do list",
                        "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "Python programming",
                                            "quantity" : None,
                                            "status" : "incomplete"
                                            }
                        ]
                    },
                    {
                        "id" : 4,
                        "name" :  "Household list",
                        "items" : [
                                            {
                                                "id" : 1,
                                                "name" : "Toilet paper",
                                                "quantity" :  "32 pc",
                                                "status" : "incomplete"
                                            }
                        ]
                    }
                ]
            }
        }
    elif list_id == 3:
        response_data = {
            "meta" : {},
            "data" : {
                "lists" : [
                    {
                        "id" : 1,
                        "name" : "Grocery list",
                         "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "eggs",
                                            "quantity" : "12 pc",
                                            "status" :  "Incomplete"
                                            }
                        ]
                    },
                    {
                        "id" : 2,
                        "name" : "Shopping list",
                        "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "Anne taylor top",
                                            "quantity" : "7 pc",
                                            "status" : "incomplete"
                                            }
                        ]
                    },
                    {
                        "id" : 3,
                        "name" : new_name,
                        "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "Python programming",
                                            "quantity" : None,
                                            "status" : "incomplete"
                                            }
                        ]
                    },
                    {
                        "id" : 4,
                        "name" :  "Household list",
                        "items" : [
                                            {
                                                "id" : 1,
                                                "name" : "Toilet paper",
                                                "quantity" :  "32 pc",
                                                "status" : "incomplete"
                                            }
                        ]
                    }
                ]
            }
        }
    elif list_id == 4:
        response_data = {
            "meta" : {},
            "data" : {
                "lists" : [
                    {
                        "id" : 1,
                        "name" : "Grocery list",
                         "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "eggs",
                                            "quantity" : "12 pc",
                                            "status" :  "Incomplete"
                                            }
                        ]
                    },
                    {
                        "id" : 2,
                        "name" : "Shopping list",
                        "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "Anne taylor top",
                                            "quantity" : "7 pc",
                                            "status" : "incomplete"
                                            }
                        ]
                    },
                    {
                        "id" : 3,
                        "name" : "to-do list",
                        "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "Python programming",
                                            "quantity" : None,
                                            "status" : "incomplete"
                                            }
                        ]
                    },
                    {
                        "id" : 4,
                        "name" :  new_name,
                        "items" : [
                                            {
                                                "id" : 1,
                                                "name" : "Toilet paper",
                                                "quantity" :  "32 pc",
                                                "status" : "incomplete"
                                            }
                        ]
                    }
                ]
            }
        }
    else:
        raise ValueError("No list with list_id %d found" % list_id)
    body = json.dumps(response_data)
    status = 200
    headers = {
        'Content-Type' : 'application/json'
    }
    return (body,status,headers)

#Delete the complete list
@app.route('/lists/<int:list_id>', methods=['DELETE'])
def delete_list(list_id):
    if list_id == 1:
        response_data = {
            "meta" : {},
            "data" : {
                "lists" : [
                    {
                        "id" : 2,
                        "name" : "Shopping list",
                        "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "Anne taylor top",
                                            "quantity" : "7 pc",
                                            "status" : "incomplete"
                                            }
                        ]
                    },
                    {
                        "id" : 3,
                        "name" : "to-do list",
                        "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "Python programming",
                                            "quantity" : None,
                                            "status" : "incomplete"
                                            }
                        ]
                    },
                    {
                        "id" : 4,
                        "name" :  "Household list",
                        "items" : [
                                            {
                                                "id" : 1,
                                                "name" : "Toilet paper",
                                                "quantity" :  "32 pc",
                                                "status" : "incomplete"
                                            }
                        ]
                    }
                ]
            }
        }
    elif list_id == 2:
        response_data = {
            "meta" : {},
            "data" : {
                "lists" : [
                    {
                        "id" : 1,
                        "name" : "Grocery list",
                         "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "eggs",
                                            "quantity" : "12 pc",
                                            "status" :  "Incomplete"
                                            }
                        ]
                    },

                    {
                        "id" : 3,
                        "name" : "to-do list",
                        "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "Python programming",
                                            "quantity" : None,
                                            "status" : "incomplete"
                                            }
                        ]
                    },
                    {
                        "id" : 4,
                        "name" :  "Household list",
                        "items" : [
                                            {
                                                "id" : 1,
                                                "name" : "Toilet paper",
                                                "quantity" :  "32 pc",
                                                "status" : "incomplete"
                                            }
                        ]
                    }
                ]
            }
        }
    elif list_id == 3:
        response_data = {
            "meta" : {},
            "data" : {
                "lists" : [
                    {
                        "id" : 1,
                        "name" : "Grocery list",
                         "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "eggs",
                                            "quantity" : "12 pc",
                                            "status" :  "Incomplete"
                                            }
                        ]
                    },
                    {
                        "id" : 2,
                        "name" : "Shopping list",
                        "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "Anne taylor top",
                                            "quantity" : "7 pc",
                                            "status" : "incomplete"
                                            }
                        ]
                    },

                    {
                        "id" : 4,
                        "name" :  "Household list",
                        "items" : [
                                            {
                                                "id" : 1,
                                                "name" : "Toilet paper",
                                                "quantity" :  "32 pc",
                                                "status" : "incomplete"
                                            }
                        ]
                    }
                ]
            }
        }
    elif list_id == 4:
        response_data = {
            "meta" : {},
            "data" : {
                "lists" : [
                    {
                        "id" : 1,
                        "name" : "Grocery list",
                         "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "eggs",
                                            "quantity" : "12 pc",
                                            "status" :  "Incomplete"
                                            }
                        ]
                    },
                    {
                        "id" : 2,
                        "name" : "Shopping list",
                        "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "Anne taylor top",
                                            "quantity" : "7 pc",
                                            "status" : "incomplete"
                                            }
                        ]
                    },
                    {
                        "id" : 3,
                        "name" : "to-do list",
                        "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "Python programming",
                                            "quantity" : None,
                                            "status" : "incomplete"
                                            }
                        ]
                    }
                ]
            }
        }
    else:
        raise ValueError("No list with list_id %d found" % list_id)
    body = json.dumps(response_data)
    status = 200
    headers = {
    'Content-Type' : 'application/json'
    }
    return (body, status, headers)

#fetching item to a list
@app.route('/list/<list_id>', methods=['POST'])
def fetch_items(list_id):
    if list_id == 1:
        response_data = {
        "meta" : {},
        "data" : {
            "lists" : [
                {
                    "id" : 1,
                    "name" : "Grocery list",
                    "items" : [
                                        {
                                        "id" : 1,
                                        "name" : "eggs",
                                        "quantity" : "12 pc",
                                        "status" :  "Incomplete"
                                        }
                                    ]
                    }
                ]
            }
        }
    elif list_id == 2:
        response_data = {
        "meta" : {},
        "data" : {
            "lists" : [
                    {
                        "id" : 2,
                        "name" : "Shopping list",
                        "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "Anne taylor top",
                                            "quantity" : "7 pc",
                                            "status" : "incomplete"
                                            }
                        ]
                    }
                ]
            }
        }

    elif list_id == 3:
        response_data = {
        "meta" : {},
        "data" : {
            "list": {
                        "id" : 3,
                        "name" : "to-do list",
                        "items" : [
                                            {
                                            "id" : 1,
                                            "name" : "Python programming",
                                            "quantity" : None,
                                            "status" : "incomplete"
                                            }
                        ]
                    }
                }
            }

    elif list_id == 4:
        response_data = {
        "meta" : {},
        "data" : {
            "lists" : [
            {
                        "id" : 4,
                        "name" :  "Household list",
                        "items" : [
                                            {
                                                "id" : 1,
                                                "name" : "Toilet paper",
                                                "quantity" :  "32 pc",
                                                "status" : "incomplete"
                                            }
                        ]
                    }
                ]
            }
        }

    else:
        raise ValueError("No list found with list_id %d found" % list_id)

# that's how you bound parts of URL to parameter that go to your function
@app.route('/lists/<int:list_id>', methods=['GET', 'POST'])
def lists_with_list_id(list_id):

    if request.method == 'GET':
        response_data = {
            'meta': {},
            'data': {
                "lists": [
                    {
                        "id": list_id,
                        "name": "dummy-list-name",
                        "items": [
                            {
                                "id": 1,
                                "name": "tide",
                                "status": "incomplete"
                            }
                        ]
                    }
                ]
            }
        }
        body = json.dumps(response_data)
        status = 200
        headers = {
            'Content-Type': 'application/json'
        }
        # that's how you send back a response
        return (body, status, headers)


if __name__ == "__main__":
    app.run()



