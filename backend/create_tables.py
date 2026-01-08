#!/usr/bin/env python3
"""Create database tables"""
from app.db import engine, Base
from app.models import Menu, Conversation

Base.metadata.create_all(bind=engine)
print("Tables created successfully")
