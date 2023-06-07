from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Length, InputRequired
from flask_wtf.file import FileField, FileAllowed
from flask_ckeditor import CKEditorField


class PostForm(FlaskForm):
  title = StringField(
      "Title",
      validators=[
          InputRequired(),
          Length(min=4,
                 max=35,
                 message="Title must be between 4 and 35 characters long.")
      ])
  teaser_image = FileField(
      "Teaser Image",
      validators=[FileAllowed(["jpg", "png", "jpeg"], "Images only!")])
  # body = TextAreaField(
  #     "Body",
  #     validators=[
  #         InputRequired(),
  #         Length(min=50,
  #                max=4000,
  #                message="Body must be between 50 and 4000 characters long.")
  #     ])
  body = CKEditorField(
      "Body",
      validators=[
          InputRequired(),
          Length(min=50,
                 max=4000,
                 message="Body must be between 50 and 4000 characters long.")
      ])
  submit = SubmitField(label="Create")
