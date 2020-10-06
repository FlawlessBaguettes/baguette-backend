from app import db
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import JSON, UUID
import uuid


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    parentId = db.Column(UUID(as_uuid=True))
    contentId = db.Column(UUID(as_uuid=True), db.ForeignKey('content.id'))
    userId = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
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
