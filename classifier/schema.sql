DROP TABLE IF EXISTS data;

CREATE TABLE data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label VARCHAR(255),
    content TEXT,
    datetime_update DATETIME DEFAULT 'NOW()'
);
