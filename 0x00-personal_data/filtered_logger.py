#!/usr/bin/env python3
"""
Definition of filter_datum function with log message obfuscation.
"""
from typing import List
import re
import logging
import os
import mysql.connector

# Fields that may contain Personally Identifiable Information (PII)
PII_FIELDS = ('name', 'email', 'phone', 'ssn', 'password')


def filter_datum(fields: List[str], redaction: str, message: str, separator: str) -> str:
    """
    Returns a log message with specified fields obfuscated.

    Args:
        fields (List[str]): Fields to obfuscate.
        redaction (str): Replacement string for obfuscation.
        message (str): Log message to be processed.
        separator (str): Field separator in the log message.

    Returns:
        str: Obfuscated log message.
    """
    pattern = r'(' + '|'.join(re.escape(field) for field in fields) + r')=.*?' + re.escape(separator)
    return re.sub(pattern, lambda match: f"{match.group(1)}={redaction}{separator}", message)


class RedactingFormatter(logging.Formatter):
    """Formatter class for redacting log messages."""

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        """Initialize with fields to redact."""
        super().__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """
        Redact fields in the log message.

        Args:
            record (logging.LogRecord): Log record instance.

        Returns:
            str: Formatted log message with fields redacted.
        """
        raw_message = super().format(record)
        return filter_datum(self.fields, self.REDACTION, raw_message, self.SEPARATOR)


def get_logger() -> logging.Logger:
    """
    Configure and return a logger instance.

    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    handler = logging.StreamHandler()
    handler.setFormatter(RedactingFormatter(PII_FIELDS))
    logger.addHandler(handler)

    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """
    Connect to the database and return a connection object.

    Returns:
        mysql.connector.connection.MySQLConnection: Database connection.
    """
    conn = mysql.connector.connect(
        user=os.getenv('PERSONAL_DATA_DB_USERNAME', "root"),
        password=os.getenv('PERSONAL_DATA_DB_PASSWORD', ""),
        host=os.getenv('PERSONAL_DATA_DB_HOST', "localhost"),
        database=os.getenv('PERSONAL_DATA_DB_NAME')
    )
    return conn


def main():
    """
    Entry point for retrieving user data and logging it.
    """
    db_connection = get_db()
    logger = get_logger()

    with db_connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users;")
        columns = cursor.column_names

        for record in cursor:
            log_message = "; ".join(f"{col}={val}" for col, val in zip(columns, record)) + ";"
            logger.info(log_message)

    db_connection.close()


if __name__ == "__main__":
    main()
