"""Synthetic adoption-center data used by the offline reference baseline."""

import sqlite3

PETS = [
    ("Sir Barksalot III", "Dog", "Corgi", 4, "Available", "Extreme", 8, 42, "Yes"),
    ("Chairman Meow", "Cat", "Domestic Shorthair", 7, "Available", "Low", 4, 18, "Maybe"),
    ("Dumpster Fire", "Cat", "Orange Tabby", 2, "Available", "Extreme", 10, 78, "No"),
    ("Kevin", "Goat", "Nigerian Dwarf", 3, "Available", "High", 10, 55, "Yes"),
    ("Lasagna", "Dog", "Basset Hound", 6, "Pending", "Low", 2, 10, "Yes"),
    ("Tax Fraud", "Parrot", "African Grey", 18, "Available", "High", 9, 61, "Maybe"),
    ("Princess Murdermittens", "Cat", "Maine Coon", 5, "Available", "Medium", 7, 69, "No"),
    ("Gary", "Dog", "Chihuahua Mix", 9, "Available", "Extreme", 9, 64, "No"),
    ("Potato Supreme", "Rabbit", "Flemish Giant", 4, "Available", "Low", 3, 12, "Yes"),
    ("Beef Wellington", "Dog", "English Bulldog", 5, "Adopted", "Low", 2, 8, "Yes"),
    ("Reverend Bitey", "Cat", "Siamese", 8, "Available", "Medium", 8, 73, "No"),
    ("Crouton", "Dog", "Great Dane", 2, "Available", "High", 7, 28, "Yes"),
    ("Wi-Fi Password", "Ferret", "Ferret", 3, "Available", "Extreme", 10, 47, "Maybe"),
    ("Linda from Accounting", "Cat", "Tortoiseshell", 11, "Available", "Low", 6, 31, "Maybe"),
    ("Meatball", "Pig", "Mini Pig", 4, "Available", "Medium", 8, 36, "Yes"),
]

APPLICATION_COUNTS = {
    "Sir Barksalot III": 6,
    "Chairman Meow": 5,
    "Dumpster Fire": 1,
    "Kevin": 11,
    "Lasagna": 14,
    "Tax Fraud": 6,
    "Princess Murdermittens": 3,
    "Gary": 2,
    "Potato Supreme": 8,
    "Beef Wellington": 9,
    "Reverend Bitey": 2,
    "Crouton": 10,
    "Wi-Fi Password": 2,
    "Linda from Accounting": 4,
    "Meatball": 7,
}


def create_database(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE pets (
            name TEXT PRIMARY KEY,
            species TEXT NOT NULL,
            breed TEXT NOT NULL,
            age INTEGER NOT NULL,
            status TEXT NOT NULL,
            energy TEXT NOT NULL,
            chaos INTEGER NOT NULL,
            behavior_risk INTEGER NOT NULL,
            good_with_kids TEXT NOT NULL
        );
        CREATE TABLE applications (
            pet_name TEXT PRIMARY KEY REFERENCES pets(name),
            application_count INTEGER NOT NULL
        );
        """
    )
    connection.executemany(
        "INSERT INTO pets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", PETS
    )
    connection.executemany(
        "INSERT INTO applications VALUES (?, ?)", APPLICATION_COUNTS.items()
    )