from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# The URI for the SQLite database
DATABASE_URI = 'sqlite:///movieweb.db'

# Create a SQLAlchemy engine for connecting to the database
engine = create_engine(DATABASE_URI)

# Create a base class for declarative SQLAlchemy models
Base = declarative_base()

# Create a session factory using the engine
Session = sessionmaker(bind=engine)

"""
This module provides database-related utilities using SQLAlchemy.

Attributes:
    DATABASE_URI (str): The URI for the SQLite database.
    engine: A SQLAlchemy engine for connecting to the database.
    Base: A base class for declarative SQLAlchemy models.
    Session: A session factory for creating database sessions.
"""
