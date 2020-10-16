from app import db
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import JSON, UUID
import uuid

import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir) 
from utils.date import prettydate


class Post(db.Model):
    __tablename__ = 'posts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    parentId = Column(UUID(as_uuid=True), db.ForeignKey('posts.id'))
    contentId = Column(UUID(as_uuid=True), db.ForeignKey('content.id'), nullable=False)
    userId = Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)

    title = Column(db.String(), nullable=False)
    #TO DO: Update to utcnow()
    createdAt = Column(DateTime, server_default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())
    deletedAt = Column(DateTime)

    def __init__(self, parentId, contentId, userId, title):
        self.parentId = parentId
        self.contentId = contentId
        self.userId = userId
        self.title = title

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            "parentId": self.parentId,
            'contentId': self.contentId,
            'userId': self.userId,
            'title': self.title,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt,
            'deletedAt': self.deletedAt
        }


def serialize_post(post):
    parent_post = post[0]
    children = post[1:]
    children_length = len(children)

    serialable = serialize(parent_post[0], parent_post[1], parent_post[2])
    serialable['number_of_children'] = children_length
    serialable['children'] = {}
    for i in range(0, children_length):
        child_post = children[i]
        serialable['children'][str(i)] = serialize(child_post[0], child_post[1], child_post[2])
    return serialable

def serialize(post, content, user):
    return {
        'id': post.id,
        "parentId": post.parentId,
        'contentId': post.contentId,
        'userId': post.userId,
        'title': post.title,
        'url': content.url,
        'name': {
            'full_name' : user.first_name + " " + user.last_name,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username 
        },
        "posted_time": prettydate(post.createdAt),
        'createdAt': post.createdAt,
        'updatedAt': post.updatedAt,
    }