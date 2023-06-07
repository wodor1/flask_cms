from python_cms.db import BaseModel, db
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import String
from flask_login import UserMixin


class UserModel(BaseModel, UserMixin):
  __tablename__ = "users"
  id = mapped_column(String(80), primary_key=True)
  name = mapped_column(String(80), primary_key=True)
  email = mapped_column(String(80), primary_key=True)
  profile_pic = mapped_column(String(80), primary_key=True)

  # one to many relationship: one user can have many posts
  posts = relationship("PostModel", back_populates="author")

  def __init__(self, id, name, email, picture):
    self.id = id
    self.name = name
    self.email = email
    self.profile_pic = picture

  @classmethod
  def get(cls, user_id):
    return cls.query.filter_by(id=user_id).first()

  def save(self):
    db.session.add(self)
    db.session.commit()
