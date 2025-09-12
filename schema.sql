CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE books (
    id INTEGER PRIMARY KEY,
    title TEXT,
    author TEXT,
    genre TEXT,
    year INTEGER,
    language TEXT,
    comment TEXT,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5 OR rating IS NULL ),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE added_books (
    id INTEGER PRIMARY KEY,
    book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE genres (
    id INTEGER PRIMARY KEY,
    book_id INTEGER,
    genre TEXT,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);