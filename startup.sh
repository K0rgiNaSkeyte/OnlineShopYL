#!/bin/bash

# Initialize the database
python -c "from app import create_app; from app.extensions import db; app = create_app(); app.app_context().push(); db.create_all()"

# Start the application
gunicorn run:app