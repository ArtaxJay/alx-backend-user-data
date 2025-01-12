#!/usr/bin/env python3
"""
Provides utility functions for password hashing and verification.
"""
import bcrypt


def hash_password(password: str) -> bytes:
    """
    Hash a plain-text password with salting for secure storage.

    Args:
        password (str): The password to be hashed.

    Returns:
        bytes: The salted, hashed password as a byte string.
    """
    password_bytes = password.encode('utf-8')  # Convert to bytes
    salt = bcrypt.gensalt()  # Generate a salt
    hashed_password = bcrypt.hashpw(password_bytes, salt)  # Hash with the salt
    return hashed_password


def is_valid(hashed_password: bytes, password: str) -> bool:
    """
    Verify that a provided password matches its hashed counterpart.

    Args:
        hashed_password (bytes): The stored hashed password.
        password (str): The password input to be validated.

    Returns:
        bool: True if the password matches the hash; otherwise, False.
    """
    # Convert input password to bytes
    password_bytes = password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_password)  # Compare securely
