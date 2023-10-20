from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import requests

# Append the 'workspace' directory to the sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from datamanager.data_manager import DataManagerInterface
from models.user import User
from models.movie import Movie
from models.user import UserFavoriteMovies
from models.review import Review
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import requests
from sqlalchemy.exc import IntegrityError  # Import IntegrityError for handling database integrity issues
from flask import flash  # Import flash for displaying flash messages
from sqlalchemy.orm.exc import NoResultFound  # Import NoResultFound for handling query result not found
from sqlalchemy.orm import sessionmaker, scoped_session

OMDB_API_KEY = 'cdd1ad1b'

class SQLiteDataManager(DataManagerInterface):
    def __init__(self, db_file_name):
      print("Initializing SQLiteDataManager with database file:", db_file_name)
      self.engine = create_engine(db_file_name)
      self.Session = sessionmaker(bind=self.engine)
      self.session = self.Session()
      # Add debug prints or logging statements here
      print("Tables present:", self.engine.table_names())
    
    def close_session(self):
        self.Session.remove()


    def commit_changes(self):
        self.session.commit()
    
    def rollback_changes(self):
        self.session.rollback()
    
    def get_all_users(self):
        """Retrieve a list of all users from the database."""
        return self.session.query(User).all()

    def get_users(self):
        return self.session.query(User).all()

    def get_user_by_email(self, email):
        return self.session.query(User).filter_by(email=email).first()
    
    def get_user_movies(self, user_id):
      """Retrieve a list of movies associated with a user."""
      movies = self.session.query(Movie).filter_by(user_id=user_id).all()
      print("Movies in get_user_movies:", movies)
      return movies

    def add_user(self, user):
        """
        Add a new user to the database.

        Args:
            user (User): The User instance to be added to the database.
        """
        self.session.add(user)
        self.session.commit()

    def add_movie(self, user_id, title, genre):
        """
        Add a new movie to a user's list of favorite movies.

      Args:
        user_id (int): The ID of the user to whom the movie will be added.
        title (str): The title of the movie to be added.
        genre (str): The genre of the movie.

      Raises:
        ValueError: If the movie details are not found in the OMDB API.

      Notes:
        This method also performs cleanup to delete orphaned favorite movies.
      """
        user = self.session.query(User).get(user_id)
        if user:
            # Fetch movie details using OMDB API    
            movie_details = self.get_movie_details_by_name(title)
            
            if not movie_details:
                raise ValueError("Movie not found in OMDB API")
        
        # Check if the movie already exists in the user's favorite list
            existing_movie = self.session.query(Movie).filter_by(user=user, title=movie_details['Title']).first()
            if existing_movie:
                flash("Movie is already in favorites", "info")
                return

            new_movie = Movie(title=movie_details['Title'], genre=genre, user=user)
            self.session.add(new_movie)
            self.session.commit()

            # Now, let's perform the cleanup to delete orphaned favorite movies
            try:
                self._delete_orphaned_favorite_movies()
            except Exception as e:
                flash(f"Error deleting orphaned favorite movies: {str(e)}", "error")
        else:
            flash("User not found", "error")
        
    def update_movie(self, user_id, movie_id, title, genre):
        """
        Update the details of a movie.

        Args:
            user_id (int): The ID of the user.
            movie_id (int): The ID of the movie to be updated.
            title (str): The updated name of the movie.
            genre (str): The updated genre of the movie.
        """
        user = self.session.query(User).get(user_id)
        if user:
            movie = self.session.query(Movie).get(movie_id)
            if movie:
                movie.title = title
                movie.genre = genre
                self.session.commit()

    def delete_movie(self, movie_id):
        """
        Delete a movie from the database.

        Args:
            movie_id (int): The ID of the movie to be deleted.
        """
        movie = self.session.query(Movie).get(movie_id)
        if movie:
            self.session.delete(movie)
            self.session.commit()

    def add_review(self, review):
        """
        Add a new review to the database.

        Args:
            review (Review): The Review instance to be added to the database.
        """
        self.session.add(review)
        self.session.commit()

    def update_review(self, review):
        """
        Update the details of a review.

        Args:
            review (Review): The Review instance with updated information.
        """
        self.session.commit()

    def delete_review(self, review_id):
        """
        Delete a review from the database.

        Args:
            review_id (int): The ID of the review to be deleted.
        """
        review = self.session.query(Review).get(review_id)
        if review:
            self.session.delete(review)
            self.session.commit()

    def get_review(self, review_id):
        """
        Retrieve a specific review by review ID.

        Args:
            review_id (int): The ID of the review to be retrieved.

        Returns:
            Review: The Review instance with the given review ID, or None if not found.
        """
        return self.session.query(Review).get(review_id)

    def get_movie_reviews(self, movie_id):
        """
        Retrieve a list of reviews for a specific movie.

        Args:
            movie_id (int): The ID of the movie.

        Returns:
            list: A list of Review instances associated with the given movie ID.
        """
        movie = self.session.query(Movie).get(movie_id)
        return movie.reviews if movie else []

    def get_user_name(self, user_id):
        """
        Retrieve the name of a user by user ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            str: The name of the user, or None if not found.
        """
        user = self.session.query(User).get(user_id)
        if user:
            return user.name
        return None

    def get_movie(self, user_id, movie_id):
        """
        Retrieve a specific movie by movie ID and user ID.

        Args:
            user_id (int): The ID of the user.
            movie_id (int): The ID of the movie.

        Returns:
            Movie: The Movie instance with the given movie ID and associated with the user, or None if not found.
        """
        user = self.session.query(User).get(user_id)
        if user:
            return self.session.query(Movie).get(movie_id)
        return None

    def get_user(self, user_id):
        """
        Retrieve a specific user by user ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            User: The User instance with the given user ID, or None if not found.
        """
        return self.session.query(User).get(user_id)

    def add_favorite_movie(self, user_id, movie_id):
        """
        Add a movie to a user's list of favorite movies.

        Args:
          user_id (int): The ID of the user to whom the movie will be added as a favorite.
          movie_id (int): The ID of the movie to be added as a favorite.

        Returns:
        redirect: Redirects to the user's movies page after the favorite movie update.

        Notes:
        If the movie is already in the user's favorite list, it will not be added again.
        Any issues during the update process will be rolled back and appropriate messages will be flashed.
        """
        user = self.session.query(User).get(user_id)
        movie = self.session.query(Movie).get(movie_id)

        if user and movie:
            try:
                user.favorite_movies.append(movie)
                self.session.commit()
                flash("Favorite movies updated successfully", "success")
            except IntegrityError:
                self.session.rollback()
                flash("Movie is already in favorites", "info")
            except Exception as e:
                self.session.rollback()
                flash(f"Error occurred while updating favorites: {str(e)}", "error")


    def get_user_favorite_movies(self, user_id):
            """
            Get the favorite movies of a specific user.

            Args:
                user_id (int): The ID of the user.

            Returns:
                list: A list of Movie objects representing the user's favorite movies.
            """
            user = self.session.query(User).get(user_id)
            if user:
                return user.favorite_movies
            else:
                flash("User not found", "error")
                return []

    def get_movie_details(self, title):
        """
        Fetch movie details using the OMDB API for a given movie title.

        Args:
            title (str): The title of the movie for which details need to be fetched.

        Returns:
            dict: A dictionary containing the fetched movie details.

        Raises:
            ValueError: If there is an error fetching movie details from the OMDB API.
        """
        url = f'http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}'
        response = requests.get(url)

        if response.status_code != 200:
            raise ValueError("Error fetching movie details from OMDB API")

        data = response.json()
        return data

    def get_movie_details_by_name(self, movie_name):
        """
        Fetch movie details using the OMDB API for a given movie name.

        Args:
            movie_name (str): The name of the movie for which details need to be fetched.

        Returns:
            dict: A dictionary containing the fetched movie details.

        Raises:
            ValueError: If there is an error fetching movie details from the OMDB API.
        """
        
        url = f'http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={movie_name}'
        
        # Print the constructed url
        print("Constructed URL:", url)
        
        response = requests.get(url)

        # Print the entire API response content
        response_content = response.content.decode('utf-8')
        print("API Response:", response_content)
        
        # Print the response status code
        print("API Response Status Code:", response.status_code)
        
        if response.status_code != 200:
            raise ValueError("Error fetching movie details from OMDB API")

        data = response.json()
        return data

    def _delete_orphaned_favorite_movies(self):
      """
      Delete orphaned favorite movie entries from the database.

      This method will delete any records in the UserFavoriteMovies table where the associated
      user or movie is missing from their respective tables.

      Raises:
      Exception: If there is an error while deleting orphaned favorite movie entries.
      """
      try:
        self.session.query(UserFavoriteMovies).filter(
          ~UserFavoriteMovies.user_id.in_(self.session.query(User.id)),
          ~UserFavoriteMovies.movie_id.in_(self.session.query(Movie.id))
        ).delete(synchronize_session=False)  # Specify synchronize_session=False
        self.session.commit()
      except Exception as e:
        self.session.rollback()
        raise e



