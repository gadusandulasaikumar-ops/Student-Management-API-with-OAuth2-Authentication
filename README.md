# Student Management API with OAuth2 Authentication

This is a backend project I built while learning FastAPI, SQLAlchemy, and OAuth2 authentication.

The API allows users to register and log in, and authenticated users can manage student records through CRUD operations.

## What I used

* Python
* FastAPI
* SQLAlchemy
* SQLite
* OAuth2
* JWT
* Passlib / bcrypt

## Features

* User registration
* User login with OAuth2
* Password hashing
* JWT access tokens
* Protected API endpoints
* Create student
* Read student
* Update student marks
* Delete student
* SQLite database using SQLAlchemy

## How it works

A user first registers with a username and password. The password is stored as a hashed value in the database.

After login, the API returns a JWT access token. The token is required to access the student CRUD endpoints.

I used FastAPI's dependency injection with `Depends()` to handle the database session and token verification.

## Project structure

The project is currently kept in a single Python file while learning the concepts. I plan to split it into separate files as I build larger projects.

## Running the project

Install the required packages and run the FastAPI application with Uvicorn.

Then open the Swagger documentation to test the endpoints.

## What I learned

Through this project, I practiced working with REST APIs, databases, authentication, password hashing, JWT tokens, OAuth2, SQLAlchemy sessions, and FastAPI dependencies.
