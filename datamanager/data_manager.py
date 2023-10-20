from abc import ABC, abstractmethod

class DataManagerInterface(ABC):
    """
    An abstract base class defining the interface for interacting with data in the application.

    This class defines a set of abstract methods that need to be implemented by concrete
    data manager classes to provide functionality for working with user and movie data.

    Attributes:
        None

    Methods:
        get_all_users(self): Retrieve a list of all users in the database.
        get_user_movies(self, user_id): Retrieve a list of movies associated with a user.
        delete_movie(self, user_id, movie_id): Delete a movie from a user's list of movies.
        update_movie(self, user_id, movie_id, name, genre): Update the details of a movie.
    """
    @abstractmethod
    def get_all_users(self):
        """
        Retrieve a list of all users in the database.

        Returns:
            list: A list of User objects representing all users.
        """
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        """
        Retrieve a list of movies associated with a user.

        Args:
            user_id (str): The ID of the user.

        Returns:
            list: A list of Movie objects representing the user's movies.
        """
        pass

    @abstractmethod
    def delete_movie(self, user_id, movie_id):
        """
        Delete a movie from a user's list of movies.

        Args:
            user_id (str): The ID of the user.
            movie_id (str): The ID of the movie to be deleted.

        Returns:
            None
        """
        pass

    @abstractmethod
    def update_movie(self, user_id, movie_id, name, genre):
        """
        Update the details of a movie.

        Args:
            user_id (str): The ID of the user.
            movie_id (str): The ID of the movie to be updated.
            name (str): The updated name of the movie.
            genre (str): The updated genre of the movie.

        Returns:
            None
        """
        pass
