from flask import Flask, render_template, request, redirect, url_for, flash
from datamanager.sqlite_data_manager import SQLiteDataManager
from datamanager import data_manager
from database import Base, engine
from models.user import User
from models.movie import Movie
from models.review import Review
from email_validator import validate_email, EmailNotValidError
from sqlalchemy.orm.exc import NoResultFound
from flask import Flask, jsonify, request
import uuid


app = Flask(__name__)
app.secret_key = "mysecretkey123"

# Initialize your SQLiteDataManager with the appropriate database URI
data_manager = SQLiteDataManager("sqlite:///movieweb.db")

def generate_unique_id():
    return str(uuid.uuid4())

# Generate a new UUID
movie_id = generate_unique_id()
        
# Home route
@app.route('/')
def home():
    """
    Render the home page.

    Returns:
        render_template: The rendered home.html template.
    """
    return render_template('home.html')

# Add User route
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """
    Add a new user to the database.

    Returns:
        render_template or redirect: If the request method is GET, render the add_user.html template.
                                    If the request method is POST, add the user and redirect to the users list page.
    """
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')

        # Validate the email format
        try:
            valid_email = validate_email(email)
            email = valid_email.email
        except EmailNotValidError:
            flash("Invalid email address", "error")
            return redirect('/add_user')  # Redirect back to the add_user page

        # Create a new user instance
        new_user = User(name=name, email=email)

        # Add the new user instance to the session
        data_manager.add_user(new_user)

        # Check for existing email
        existing_user = data_manager.get_user_by_email(email)
        if existing_user:
            flash("Email already exists", "error")
            return redirect('/add_user')


        flash("User added successfully", "success")
        return redirect('/users')  # Redirect to the users list page

    return render_template('add_user.html')

@app.route('/users', methods=['GET'])
def users():
    """
    Render the users list page.

    Returns:
        render_template: The rendered users.html template with user data.
    """
    users_data = data_manager.get_users()
    return render_template('users.html', users=users_data)

# User Movies route
@app.route('/users/<string:user_id>/movies')
def user_movies(user_id):
    """
    Render the user's movies page.

    Args:
        user_id (str): The ID of the user.

    Returns:
        render_template: The rendered user_movie.html template with user's movies data.
    """
    try:
        user_name = data_manager.get_user_name(user_id)
        movies = data_manager.get_user_movies(user_id)
        user = data_manager.get_user(user_id)
        print("User ID:", user_id)
        print("User Name:", user_name)
        print("Movies:", movies)
        return render_template('user_movie.html', user_id=user_id, user_name=user_name, movies=movies, user=user)
    except Exception as e:
        print("Error in user_movies route:", e)
        return render_template('error.html', error=str(e))

# Add a Movie route
@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """
    Add a movie to a user's collection or display the movie addition form.

    Args:
        user_id (int): The ID of the user to whom the movie will be added.

    Returns:
        If the request method is GET:
            render_template: The rendered add_movie.html template with the user's ID and name.
        If the request method is POST:
            redirect: Redirects to the user's movies page if the movie is successfully added,
                      or back to the add_movie page if there's an error.

    """
    if request.method == 'POST':
      name = request.form['name']
      genre = request.form['genre']
      
      try:
        # Fetch movie details from the OMDB API
        movie_details = data_manager.get_movie_details_by_name(name)
        
        if not movie_details:
            flash("Movie not found in OMDB API", "error")
            return redirect(url_for('add_movie', user_id=user_id))
        
        # Add the movie to the user's collection
        data_manager.add_movie(user_id, movie_details['Title'], genre)
        flash("The movie has been added", "success")
        return redirect(url_for('user_movies', user_id=user_id))
      except Exception as e:
        flash(f"Error adding movie: {str(e)}", "error")
        return redirect(url_for('add_movie', user_id=user_id))
    
    else:
        user_name = data_manager.get_user_name(user_id)
        return render_template('add_movie.html', user_id=user_id, user_name=user_name)

# Update a movie route
@app.route('/users/<string:user_id>/update_movie/<string:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """
    Update a movie's details.

    Args:
        user_id (str): The ID of the user.
        movie_id (str): The ID of the movie.

    Returns:
        render_template or redirect: If the request method is GET, render the update_movie.html template.
                                    If the request method is POST, update the movie and redirect to the user's movies page.
    """
    if request.method == 'POST':
        title = request.form['title']
        genre = request.form['genre']

        try:
            data_manager.update_movie(user_id, movie_id, title, genre)
            flash("The movie has been updated", "success")
            return redirect(url_for('user_movies', user_id=user_id))
        except Exception as e:
            flash(f"Error updating movie: {str(e)}", "error")
            return redirect(url_for('update_movie', user_id=user_id, movie_id=movie_id))
    else:
        movie = data_manager.get_movie(user_id, movie_id)
        return render_template('update_movie.html', user_id=user_id, movie=movie)

# Delete Movie route
@app.route('/users/<string:user_id>/delete_movie/<string:movie_id>', methods=['GET', 'POST'])
def delete_movie(user_id, movie_id):
    """
    Delete a movie.

    Args:
        user_id (str): The ID of the user.
        movie_id (str): The ID of the movie.

    Returns:
        redirect: Redirect to the user's movies page.
    """
    try:
        data_manager.delete_movie(movie_id)
        flash("The movie has been deleted", "success")
        return redirect(url_for('user_movies', user_id=user_id))
    except Exception as e:
        return render_template('error.html', error=str(e))

# Add Review route
@app.route('/users/<string:user_id>/movies/<string:movie_id>/add_review', methods=['GET', 'POST'])
def add_review(user_id, movie_id):
    """
    Add a review for a movie.

    Args:
        user_id (str): The ID of the user.
        movie_id (str): The ID of the movie.

    Returns:
        render_template or redirect: If the request method is GET, render the add_review.html template.
                                    If the request method is POST, add the review and redirect to the user's movies page.
    """
    if request.method == 'POST':
        review_text = request.form['review_text']
        rating = int(request.form['rating'])

        try:
            user = data_manager.get_user(user_id)
            movie = data_manager.get_movie(user_id, movie_id)
            new_review = Review(user=user, movie=movie, review_text=review_text, rating=rating)
            data_manager.add_review(new_review)
            flash("Review added successfully", "success")
            return redirect(url_for('user_movies', user_id=user_id))
        except Exception as e:
            flash(f"Error adding review: {str(e)}", "error")
            return redirect(url_for('add_review', user_id=user_id, movie_id=movie_id))
    else:
        user_name = data_manager.get_user_name(user_id)
        movie = data_manager.get_movie(movie_id)
        return render_template('add_review.html', user_id=user_id, user_name=user_name, movie=movie)

# Update Review route
@app.route('/users/<string:user_id>/movies/<string:movie_id>/update_review/<int:review_id>', methods=['GET', 'POST'])
def update_review(user_id, movie_id, review_id):
    """
    Update a review's details.

    Args:
        user_id (str): The ID of the user.
        movie_id (str): The ID of the movie.
        review_id (int): The ID of the review.

    Returns:
        render_template or redirect: If the request method is GET, render the update_review.html template.
                                    If the request method is POST, update the review and redirect to the user's movies page.
    """
    review = data_manager.get_review(review_id)

    if request.method == 'POST':
        review_text = request.form['review_text']
        rating = int(request.form['rating'])

        try:
            review.review_text = review_text
            review.rating = rating
            data_manager.update_review(review)
            flash("Review updated successfully", "success")
            return redirect(url_for('user_movies', user_id=user_id))
        except Exception as e:
            flash(f"Error updating review: {str(e)}", "error")
            return redirect(url_for('update_review', user_id=user_id, movie_id=movie_id, review_id=review_id))
    else:
        user_name = data_manager.get_user_name(user_id)
        movie = data_manager.get_movie(user_id, movie_id)
        return render_template('update_review.html', user_id=user_id, user_name=user_name, movie=movie, review=review)

# Delete Review route
@app.route('/users/<string:user_id>/movies/<string:movie_id>/delete_review/<int:review_id>', methods=['POST'])
def delete_review(user_id, movie_id, review_id):
    """
    Delete a review.

    Args:
        user_id (str): The ID of the user.
        movie_id (str): The ID of the movie.
        review_id (int): The ID of the review.

    Returns:
        redirect: Redirect to the user's movies page.
    """
    try:
        data_manager.delete_review(review_id)
        flash("Review deleted successfully", "success")
    except Exception as e:
        flash(f"Error deleting review: {str(e)}", "error")

    return redirect(url_for('user_movies', user_id=user_id))

# Display Reviews for a Movie route
@app.route('/users/<string:user_id>/movies/<string:movie_id>/reviews', methods=['GET'])
def movie_reviews(user_id, movie_id):
    """
    Render the reviews for a movie.

    Args:
        user_id (str): The ID of the user.
        movie_id (str): The ID of the movie.

    Returns:
        render_template: The rendered movie.reviews.html template with reviews data.
    """
    try:
        user_name = data_manager.get_user_name(user_id)
        movie = data_manager.get_movie(user_id, movie_id)
        reviews = data_manager.get_movie_reviews(movie_id)
        return render_template('movie.reviews.html', user_id=user_id, user_name=user_name, movie=movie, reviews=reviews)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/users/<user_id>/add_favorite_movie', methods=['POST'])
def add_favorite_movie(user_id):
    try:
        user = data_manager.get_user(user_id)
        if user:
            favorite_movie_ids = request.form.getlist('favorite_movies')

            for movie_id in favorite_movie_ids:
                try:
                    movie = data_manager.get_movie(movie_id)
                    if movie and movie not in user.favorite_movies:
                        user.favorite_movies.append(movie)
                except NoResultFound:
                    flash(f"Movie with ID {movie_id} not found", "error")

            data_manager.session.commit()
            flash("Favorite movies updated successfully", "success")
        else:
            flash("User not found", "error")
    except Exception as e:
        data_manager.session.rollback()
        flash(f"Error occurred while updating favorites: {str(e)}", "error")

    return redirect(url_for('user_movies', user_id=user_id))

@app.route('/api/movie_details/<string:movie_name>', methods=['GET'])
def api_movie_details(movie_name):
    """Fetch movie details from OMDB API for a given movie name and return as JSON."""
    try:
        movie_details = data_manager.get_movie_details_by_name(movie_name)
        
        if not movie_details:
            return jsonify({'error': 'Movie not found in OMDB API'}), 404
        
        return jsonify(movie_details), 200
        
    except Exception as e:
        return jsonify({'error': f"Error fetching movie details: {str(e)}"}), 500


# Create the tables in the database
Base.metadata.create_all(engine)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)