"""
"""

from list_manager import app
from flask import Flask, render_template, request, flash, redirect, url_for, make_response, session, escape
from form import SignUpForm, LoginForm
import authentication as auth
import MySQLdb as msql
import dummy_data
from authentication import BadPasswordError, NoUserExistsError, UserAlreadyExistsError, AccessTokenExpiredError, InvalidAccessTokenError,UserDisabledError
import data_manager as dm
from data_manager import NoListFoundError, NoItemFoundError
import settings

# import config
# config.SECRET_KEY
#app.config['SECRET_KEY']
# app.config['SESSION_COOKIE_NAME'] = settings.SESSION_COOKIE_NAME
app.config.update({
    'SECRET_KEY': 'number_guessing_game',
    'SESSION_COOKIE_NAME': settings.SESSION_COOKIE_NAME
})

# app.secret_key = 'number_guessing_game'

def connect_db():
    return msql.connect(
        host=settings.DATABASES['list_manager_db']['host'],
        user=settings.DATABASES['list_manager_db']['user'],
        passwd=settings.DATABASES['list_manager_db']['password'],
        db=settings.DATABASES['list_manager_db']['db_name']
    )

@app.route('/login', methods = ['GET', 'POST'])
def login():
    errors = []
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit() == False:
            flash('All fields are required')
            return render_template('login.html', form = form)
        else:
            email = request.form['email']
            password = request.form['password']
            print email , password
            db = connect_db()
            try:
                user_info = auth.authenticate_using_password(email, password, db)
                print user_info
            except BadPasswordError:
                flash("InValid Password")
                response = make_response(redirect(url_for('login')))
                return response
            except NoUserExistsError:
                flash("No User Exists")
                response = make_response(redirect(url_for('login')))
                return response
            session['access_token']= user_info['access_token']
            print "this is sesssion info: %s" %(dir(session))
            response = make_response(redirect(url_for('users')))
            return response


    else:
        return render_template('login.html', form = form)


@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    form = SignUpForm()
    if request.method == 'POST':
        if form.validate_on_submit() == False:
            flash('All fields are required')
            return render_template('signup.html', form = form)
        else:
            return "User signed up"
    else:
        return render_template('signup.html', form = form)


@app.route('/home', methods = ['GET'])
def home():
    loginform = LoginForm()

    return render_template('home.html', loginform = loginform)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
DUMMY_USERS = {
    'meta': {},
    'data': {
        'users': [
            {
                'name': 'Divya',
                'email': 'email',
                'access_token': 'abc1234'
            }
        ],
        'lists': [
            {
                'id': 1,
                'name': 'grocery list',
                'items': [
                    {
                        'name': 'tide',
                        'status': 'incomplete'
                    },
                    {
                        'name': 'wine',
                        'status': 'incomplete'
                    }
                ]
            },
            {
                'id': 2,
                'name': 'hawaii trip planning',
                'items': [
                    {
                        'name': 'Beer',
                        'status': 'incomplete'
                    },
                    {
                        'name': 'air tickets',
                        'status': 'incomplete'
                    }
                ]
            }
        ]
    }
}


@app.route('/users/', methods=['GET'])
def users():
    access_token = session.get('access_token', None)
    db = connect_db ()
    try:
        user_info = auth.authenticate_using_access_token(access_token, db)
        user_id = user_info['id']
        list_of_lists = dm.list_of_list(user_id, db)
    except AccessTokenExpiredError:
        flash("Access Token Expired. Login again")
        return render_template(url_for('login'))
    except InvalidAccessTokenError:
        flash("In Valid Access Token. Login again")
        return render_template(url_for('login'))
    except NoListFoundError:
        flash("No List Created yet.")
        return render_template(url_for('users', user_id = user_id )) #need to check this. as it seems it go in infinite iteration when no list is added by user.


    print type(user_info)
    if request.method == 'GET':
        print  user_info
        return render_template('user_home.html', user_info = user_info, lists = list_of_lists, access_token = access_token)
    # else:
    #     dm.deactive_user(user_info['id'], query_access_token, db)
    #     response_data = {
    #         "meta":{},
    #         "data":{
    #             "users":[
    #                 {
    #                     "authentication" : "Success",
    #                     "name" : user_info['name'],
    #                     "id" : user_info['id'],
    #                     "name" : user_info['name'],
    #                     "delete" : "success"
    #                 }
    #             ]
    #         }
    #     }
    #     status = 200
    #
    # body = json.dumps(response_data)
    # headers = {
    #              'Content-Type' : 'application/json'
    #         }
    # return (body, status, headers)
    #  return render_template('user_home.html', user_data=DUMMY_USERS)


def get_list_data(list_id, access_token):
    try:
        return  [
                    DUMMY_USERS['data']['lists'][list_id-1]
                ]
    except (KeyError, IndexError):
        return {
            'data': {}
        }

@app.route('/lists', methods=['GET'])
def user_home():
    pass
@app.route('/lists/<int:list_id>', methods=['GET'])
def lists(list_id):
    print 'list_id: %s, access_token: %s' % (list_id, request.args.get('access_token'))
    access_token = session.get('access_token', None)
    db = connect_db ()
    try:
        user_info = auth.authenticate_using_access_token(access_token, db)
        user_id = user_info['id']
        list_info = dm.fetch_list(list_id, user_id, db)
    except AccessTokenExpiredError:
        flash("Access Token Expired. Login again")
        return render_template(url_for('login'))
    except InvalidAccessTokenError:
        flash("In Valid Access Token. Login again")
        return render_template(url_for('login'))
    except NoListFoundError:
        flash("No List found with this id:%d" %(list_id))
        return render_template(url_for('users', user_id = user_info['id'],
        access_token = user_info['access_token'] ))

    return render_template('list_info.html', list_info=list_info)

@app.route('/logout')
def logout():
    # import pdb; pdb.set_trace()

    session.pop('access_token', None)
    return redirect(url_for('home'))
