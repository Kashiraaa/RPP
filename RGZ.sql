CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    chat_id INTEGER UNIQUE NOT NULL
);

CREATE TABLE operations (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    sum DECIMAL(10, 2) NOT NULL,
    chat_id INTEGER NOT NULL,
    type_operation VARCHAR(255) NOT NULL,
    FOREIGN KEY (chat_id) REFERENCES users(chat_id)
);