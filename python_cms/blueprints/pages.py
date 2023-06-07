from flask import Blueprint, render_template, request, redirect, send_from_directory, url_for, flash
from flask_login import login_required
from werkzeug.utils import secure_filename
from flask_ckeditor import upload_success, upload_fail
from os import path
import python_cms
from flask_login import current_user
from bs4 import BeautifulSoup

from python_cms.forms.post_form import PostForm
from python_cms.models.post import PostModel

pages_blueprint = Blueprint('pages', __name__)


@pages_blueprint.route("/")
def index():
  posts = PostModel.get_all()
  return render_template("index.html.j2", posts=posts)


@pages_blueprint.route("/about")
def about():
  return render_template("about.html.j2")


@pages_blueprint.route("/post/<int:post_id>")
def view_post(post_id):
  post = PostModel.get(post_id)
  post.body = post.body.decode('utf-8')
  return render_template("post.html.j2", post=post)


VALID_TAGS = [
    'div', 'br', 'p', 'h1', 'h2', 'img', 'h3', 'ul', 'li', 'em', 'strong', 'a',
    'blockquote'
]


def sanitize_html(value):

  soup = BeautifulSoup(value, features="html.parser")

  for tag in soup.findAll(True):
    if tag.name not in VALID_TAGS:
      tag.extract()

  return soup.renderContents()


@pages_blueprint.route("/add", methods=["GET", "POST"])
@login_required
def create_post():
  form = PostForm()
  if request.method == "POST" and form.validate_on_submit():
    # print(json.dumps(request.form, indent=2))
    body = request.form["body"]

    clean_body = sanitize_html(body)

    title = request.form["title"]
    user = current_user.get_id()

    file = request.files["teaser_image"]
    # print(file)
    filename = secure_filename(file.filename)
    file.save(path.join(python_cms.ROOT_PATH, 'files_upload', filename))

    post = PostModel(title=title,
                     body=clean_body,
                     user_id=user,
                     teaser_image=filename)
    post.save()
    flash(f"Post with title: {title} created successfully", "success")
    return redirect(url_for("pages.create_post"))
  print(form.errors)
  return render_template("create_post.html.j2", form=form)


@pages_blueprint.route("/files/<path:filename>")
def files(filename):
  directory = path.join(python_cms.ROOT_PATH, 'files_upload')
  return send_from_directory(directory=directory, path=filename)


@pages_blueprint.route('/upload', methods=['POST'])
def upload():
  f = request.files.get('upload')
  # Add more validations here
  extension = f.filename.split('.')[-1].lower()
  if extension not in ['jpg', 'gif', 'png', 'jpeg']:
    return upload_fail(message='Image only!')
  directory = path.join(python_cms.ROOT_PATH, 'files_upload')
  f.save(path.join(directory, f.filename))
  url = url_for('pages.files', filename=f.filename)
  return upload_success(url, filename=f.filename)  # return upload_success call
