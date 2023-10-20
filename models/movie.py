from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Movie(Base):
    """
    Represents a movie in the 'movies' table of the database.

    Attributes:
        id (int): The primary key for the movie.
        title (str): The title of the movie.
        genre (str): The genre of the movie.
        user_id (int): The ID of the user who added the movie (foreign key).
        user (relationship): A relationship to the 'User' object associated with the movie.
        reviews (relationship): A relationship to the 'Review' objects associated with the movie.
    """

    __tablename__ = 'movies'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    genre = Column(String(50))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='favorite_movies')
    reviews = relationship('Review', back_populates='movie')
