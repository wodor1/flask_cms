from flask import Blueprint, render_template, request, redirect, send_from_directory, url_for, flash
from flask_login import login_required
from werkzeug.utils import secure_filename
from flask_ckeditor import upload_success, upload_fail
from os import path
import python_cms
from flask_login import current_user
from bs4 import BeautifulSoup
from python_cms.db import db

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
        # Check if file exists and filename is not empty
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(path.join(python_cms.ROOT_PATH, 'files_upload', filename))
        else:
            filename = ''

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
    # return upload_success call
    return upload_success(url, filename=f.filename)


@pages_blueprint.route('/post/delete/<string:post_id>', methods=['POST'])
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


@login_required
@pages_blueprint.route("/post/edit/<string:post_id>", methods=['GET', 'POST'])
def edit_post(post_id):
    # Lekérdezzük a postot az adatbázisból.
    post = PostModel.get(post_id)

    # Ellenőrizzük, hogy a jelenleg bejelentkezett felhasználó-e a szerzője a bejegyzésnek.
    if current_user.id != post.author_id:
        abort(403, description="You do not have the right permissions to edit this post")

    # Példányosítjuk a formot.
    form = PostForm()

    # Ha a formot elküldték, és valid, akkor frissítjük a bejegyzést.
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = sanitize_html(form.body.data)

        # Ha van új kép, akkor azt is frissítjük.
        if 'teaser_image' in request.files:
            file = request.files["teaser_image"]
            filename = secure_filename(file.filename)
            file.save(path.join(python_cms.ROOT_PATH, 'files_upload', filename))
            post.teaser_image = filename

        # Frissítjük az adatbázisban.
        db.session.commit()

        flash("The post was successfully updated!", "success")
        return redirect(url_for('pages.view_post', post_id=post.id))

    # Ha GET kéréssel jöttek az oldalra, akkor betöltjük a formot a bejegyzés adataival.
    elif request.method == 'GET':
        form.title.data = post.title
        form.body.data = post.body

    # Végül visszaadjuk a formot a felhasználónak.
    return render_template('edit_post.html.j2', form=form, post_id=post_id)
