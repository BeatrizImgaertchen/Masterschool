from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Review(Base):
    """
    Represents a review in the 'reviews' table of the database.

    Attributes:
        id (int): The primary key for the review.
        user_id (str): The ID of the user who wrote the review (foreign key).
        movie_id (int): The ID of the movie being reviewed (foreign key).
        review_text (str): The text of the review.
        rating (int): The rating given in the review.
        user (relationship): A relationship to the 'User' object associated with the review.
        movie (relationship): A relationship to the 'Movie' object associated with the review.
    """

    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False)
    review_text = Column(String)
    rating = Column(Integer)
    user = relationship('User', back_populates='reviews')
    movie = relationship('Movie', back_populates='reviews')
