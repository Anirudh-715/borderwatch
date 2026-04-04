#!/usr/bin/env python3
"""
BorderWatch - Database initialization script.
Run this once before starting the app for the first time.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from models.database import init_db

if __name__ == '__main__':
    print("Initializing BorderWatch database...")
    init_db()
    print("Done! You can now run: python app.py")
