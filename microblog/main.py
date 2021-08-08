import datetime
from pprint import pprint
from typing import List, Tuple

import flask_login
import pytz
from dotenv import load_dotenv
from flask import Flask, make_response, render_template, request, session
from flask.helpers import url_for
from flask_bcrypt import Bcrypt
from werkzeug.utils import redirect

import user
from blog import Blog
from database.db import Database
from entry import Entry
from user import User

IST = pytz.timezone('Asia/Kolkata')

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = "meme"

    app.db = Database
    login_manager = flask_login.LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def user_loader(email):
        print(email)
        userdata = User.get_by_email(email)
        if userdata is False:
            return None
        return User(email)

    @app.route('/login')
    def login_template():
        return render_template('login.html')

    @app.route('/register')
    def register_template():
        return render_template('register.html')

    @app.route('/', methods=['GET', 'POST'])
    @flask_login.login_required
    def home() -> str:
        try:
            print(session['email'])
        except KeyError:
            print("Not logged in.")
        entries: List[Tuple] = []
        if request.method == 'POST':
            cur_user = User.get_by_email(session['email'])
            num = cur_user.count_blogs()
            print("num of blogs", num)
            num += 1
            entry_content = request.form.get('content')
            formatted_date = datetime.datetime.now(IST).strftime('%Y-%m-%d')
            print(entry_content, formatted_date)
            title = "Blog "+str(num)
            description = "Quick Created Blog"
            new_blog = Blog(cur_user.email, title, description, cur_user._id)
            new_blog.save_to_mongo()

            title = entry_content[:30]
            new_post = Entry(new_blog.get_id(), title,
                             entry_content, cur_user.email)
            new_post.save_to_mongo()

        entries = []
        print("entries: ", entries)
        cur_user = User(session['email'])
        fetched_entries = cur_user.get_recent_posts(5)
        for entry in fetched_entries:
            pprint(entry)
            entries.append(
                (
                    entry['content'],
                    entry['created_date'],
                    entry['created_date'].strftime("%b %d"),
                    entry['title']
                )
            )
        print(entries)
        return render_template('home.html', entries=entries)

    @app.route('/blogs/<string:user_id>')
    @app.route('/blogs')
    def user_blogs(user_id=None):
        if user_id is not None:
            cur_user = User.get_by_id(user_id)
        else:
            cur_user = User.get_by_email(session['email'])

        blogs = cur_user.get_blogs()

        return render_template("user_blogs.html", blogs=blogs, email=cur_user.email)

    @app.route('/blogs/new', methods=['POST', 'GET'])
    def create_new_blog():
        if request.method == 'GET':
            return render_template('new_blog.html')
        else:
            title = request.form['title']
            description = request.form['description']
            cur_user = User.get_by_email(session['email'])

            new_blog = Blog(cur_user.email, title, description, cur_user._id)
            new_blog.save_to_mongo()

            return make_response(user_blogs(cur_user._id))

    @app.route('/posts/<string:blog_id>')
    def blog_posts(blog_id):
        blog = Blog.from_mongo(blog_id)
        posts = blog.get_posts()

        return render_template('posts.html', posts=posts, blog_title=blog.title, blog_id=blog._id)

    @app.route('/posts/new/<string:blog_id>', methods=['POST', 'GET'])
    def create_new_post(blog_id):
        if request.method == 'GET':
            return render_template('new_post.html', blog_id=blog_id)
        else:
            title = request.form['title']
            content = request.form['content']
            cur_user = User.get_by_email(session['email'])

            new_post = Entry(blog_id, title, content, cur_user.email)
            new_post.save_to_mongo()

            return make_response(blog_posts(blog_id))

    @app.before_first_request
    def initialize_database():
        user.bcrypt = Bcrypt(app)
        user.app = app
        session['_permanent'] = False
        Database.initialize()
        print("count: ", User("arjun").count_posts())

    @app.route('/auth/login', methods=['POST'])
    def login_user():
        email = request.form['email']
        password = request.form['password']

        if User.login_valid(email, password):
            User.login(email)
            cur_user = User(email, password)
            cur_user.auth = True
            if flask_login.login_user(cur_user):
                return redirect(url_for('home'))
            else:
                return "not logged in"

        else:
            session['email'] = None

        # return render_template("profile.html", email=session['email'])
        return redirect(url_for('home'))

    @app.route('/auth/register', methods=['POST'])
    def register_user():
        email = request.form['email']
        password = request.form['password']
        if User.register(email, password):
            return render_template("profile.html", email=session['email'])
        else:
            return render_template("login.html", signuperror="User already exists")

    @login_manager.unauthorized_handler
    def unauthorized_handler():
        return render_template('splashpage.html')

    @app.route('/logout')
    def logout():
        User.logout()
        flask_login.logout_user()
        return redirect(url_for('home'))
    return app
