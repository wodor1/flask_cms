from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from python_cms.db import BaseModel, db


class PostModel(BaseModel):
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    title = mapped_column(String(80), nullable=False)
    teaser_image = mapped_column(String(80), nullable=False)
    body = mapped_column(String(8000), nullable=False)
    author_id = mapped_column(
        String(80), ForeignKey("users.id"), nullable=False)

    author = relationship("UserModel", back_populates="posts")

    def __init__(self, title, body, user_id, teaser_image):
        self.title = title
        self.body = body
        self.author_id = user_id
        self.teaser_image = teaser_image

    @classmethod
    def get(cls, post_id):
        return cls.query.filter_by(id=post_id).first()

    @classmethod
    def get_all(cls):
        return cls.query.all()

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get(cls, id):
        return cls.query.get(id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
