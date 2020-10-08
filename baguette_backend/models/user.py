from app import db
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import JSON, UUID
import uuid


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False, primary_key=True, unique=True,)
    username = Column(db.String(), nullable=False, unique=True,)
    password = Column(db.String(), nullable=False)
    email = Column(db.String(), nullable=False, unique=True,)
    first_name = Column(db.String(), nullable=False)
    last_name = Column(db.String(), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)

    post = db.relationship('Post', backref='user', uselist=False)

    #TO DO: Update to utcnow()
    createdAt = Column(DateTime, server_default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())
    deletedAt = Column(DateTime)

    def __init__(self, username, password, email, first_name, last_name, date_of_birth):
        self.username = username
        self.password = password
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            "username": self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt,
            'deletedAt': self.deletedAt
        }
