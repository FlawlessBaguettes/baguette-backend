from app import db
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import JSON, UUID
import uuid


class Post(db.Model):
    __tablename__ = 'posts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    parentId = Column(UUID(as_uuid=True), db.ForeignKey('posts.id'))
    contentId = Column(UUID(as_uuid=True), db.ForeignKey('content.id'), nullable=False)
    userId = Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    #TO DO: Update to utcnow()
    createdAt = Column(DateTime, server_default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())
    deletedAt = Column(DateTime)

    def __init__(self, parentId, contentId, userId):
        self.parentId = parentId
        self.contentId = contentId
        self.userId = userId

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            "parentId": self.parentId,
            'contentId': self.contentId,
            'userId': self.userId,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt,
            'deletedAt': self.deletedAt
        }

def serialize(post, content, user):
    return {
        'id': post.id,
        "parentId": post.parentId,
        'contentId': post.contentId,
        'userId': post.userId,
        'createdAt': post.createdAt,
        'updatedAt': post.updatedAt,
        'url': content.url,
        'username': user.username 
    }