from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    """
    Represents a user in the 'users' table of the database.

    Attributes:
        id (int): The primary key for the user.
        name (str): The name of the user.
        email (str): The email address of the user (unique).
        favorite_movies (relationship): A relationship to the 'Movie' objects associated with the user.
        reviews (relationship): A relationship to the 'Review' objects associated with the user.
    """

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    favorite_movies = relationship('Movie', secondary='user_favorite_movies', back_populates='user', cascade="all, delete")
    reviews = relationship('Review', back_populates='user')

class UserFavoriteMovies(Base):
    __tablename__ = 'user_favorite_movies'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), primary_key=True)
