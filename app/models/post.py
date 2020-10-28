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
            "parent_id": self.parentId,
            'content_id': self.contentId,
            'user_id': self.userId,
            'title': self.title,
            'created_at': self.createdAt,
            'updated_at': self.updatedAt,
            'deleted_at': self.deletedAt
        }

def serialize(post, content, user, number_of_replies):
    return {
        'id': post.id,
        "parent_id": post.parentId,
        'title': post.title,
        'user': {
            'full_name' : user.first_name + " " + user.last_name,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'user_id': post.userId
        },
        "content": {
            'url': content.url,
            "posted_time": prettydate(post.createdAt)
        },
        "number_of_replies": number_of_replies,
        'created_at': post.createdAt,
        'updated_at': post.updatedAt,
    }


def serialize_posts(posts):
    serializable = {}
    number_of_posts = len(posts)
    serializable['number_of_posts'] = number_of_posts

    serialized_posts = []
    for i in range(number_of_posts):
        post = posts[i]
        serialized_posts.append(serialize(post[0], post[1], post[2], post[3]))

    serializable['posts'] = serialized_posts
    return serializable


def serialize_replies(replies):
    number_of_replies = len(replies)

    serializable = {}
    serializable['number_of_replies'] = number_of_replies
    serializable['replies'] = []
    for i in range(0, number_of_replies):
        child_post = replies[i]
        serializable['replies'].append(serialize(child_post[0], child_post[1], child_post[2], child_post[3]))
    return serializable