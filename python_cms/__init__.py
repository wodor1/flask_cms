from flask import Flask
from os import environ, path, mkdir
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from flask import flash, redirect, url_for, abort
from flask_login import login_required, current_user
from python_cms.blueprints.pages import pages_blueprint
from python_cms.blueprints.auth import auth_blueprint
from python_cms.db import db

from python_cms.models.user import UserModel
from python_cms.models.post import PostModel

app = Flask(__name__)

ROOT_PATH = app.root_path

app.register_blueprint(pages_blueprint)
app.register_blueprint(auth_blueprint)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

app.jinja_env.auto_reload = True

app.secret_key = environ.get("SECRET_KEY")
login_manager = LoginManager()
login_manager.init_app(app)

app.config[
    'CKEDITOR_FILE_UPLOADER'] = 'pages.upload'  # this value can be endpoint or url

ckeditor = CKEditor(app)


@login_manager.user_loader
def load_user(user_id):
    return UserModel.get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return "You must be logged in to view this page."


# @app.before_first_request
# def create_tables():
#   db.create_all()

# USE THIS INSTEAD
with app.app_context():
    print("Creating tables...")
    db.create_all()
    files_path = path.join(app.root_path, "files_upload")
    if not path.exists(files_path):
        print("Creating files_upload folder...")
        mkdir(files_path)


@app.route('/post/delete/<string:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = PostModel.get(post_id)
    if post is None:
        abort(404, "Post not found")  # You can return a custom error page here

    if current_user.id != post.author_id:
        return ("You are not authorized to delete this post", 403)

    post.delete()
    db.session.commit()

    flash("The post has been successfully deleted.")
    # replace 'index' with the route of your home page
    return redirect(url_for('pages.index'))
