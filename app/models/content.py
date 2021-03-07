from app import db
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import JSON, UUID
import uuid


class Content(db.Model):
    __tablename__ = 'content'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    external_id = Column(db.String(), nullable=False)
    url = Column(db.String(), nullable=False)

    post = db.relationship('Post', backref='content', uselist=False)

    #TO DO: Update to utcnow()
    createdAt = Column(DateTime, server_default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())
    deletedAt = Column(DateTime)

    def __init__(self, external_id, url):
        self.external_id = external_id
        self.url = url

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'external_id': self.external_id,
            "url": self.contentUrl,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt,
            'deletedAt': self.deletedAt
        }
