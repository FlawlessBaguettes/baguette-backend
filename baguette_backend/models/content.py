from app import db
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import JSON, UUID
import uuid


class Content(db.Model):
    __tablename__ = 'content'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    contentUrl = Column(db.String())
    #TO DO: Update to utcnow()
    createdAt = Column(DateTime, server_default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())
    deletedAt = Column(DateTime)

    def __init__(self, url):
        self.contentUrl = url

    def __repr__(self):
        return '<id {}>'.format(self.id)
