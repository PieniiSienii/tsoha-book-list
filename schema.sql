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
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    user_id INTEGER REFERENCES users(id)
);

CREATE TABLE added_books (
    id INTEGER PRIMARY KEY,
    book_id INTEGER REFERENCES books(id),
    user_id INTEGER REFERENCES users(id)
);

CREATE TABLE genres (
    id INTEGER PRIMARY KEY,
    book_id INTEGER REFERENCES books(id),
    genre TEXT REFERENCES books(genre)
);
