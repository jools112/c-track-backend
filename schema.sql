--
-- File generated with SQLiteStudio v3.1.1 on Tue May 18 13:15:36 2021
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: calendar_entries
CREATE TABLE calendar_entries (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    meal_id  INT,
    food_id  INTEGER,
    date     DATE,
    quantity INTEGER
);


-- Table: food
CREATE TABLE food (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     STRING,
    calories INTEGER
);


-- Table: meal_food
CREATE TABLE meal_food (
    meal_id  INTEGER,
    food_id  INT,
    quantity INTEGER
);


-- Table: meals
CREATE TABLE meals (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name STRING
);

-- Table: measurements
CREATE TABLE measurements (
    date   DATE PRIMARY KEY,
    weight REAL
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
