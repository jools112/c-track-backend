--
-- File generated with SQLiteStudio v3.3.3 on Tue May 11 16:35:57 2021
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: calendar_entries
DROP TABLE IF EXISTS calendar_entries;

CREATE TABLE calendar_entries (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    meal_id  INT,
    food_id  INTEGER,
    date     DATE,
    quantity INTEGER
);


-- Table: food
DROP TABLE IF EXISTS food;

CREATE TABLE food (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     STRING,
    calories INTEGER
);


-- Table: meal_food
DROP TABLE IF EXISTS meal_food;

CREATE TABLE meal_food (
    meal_id  INTEGER,
    food_id  INT,
    quantity INTEGER
);


-- Table: meals
DROP TABLE IF EXISTS meals;

CREATE TABLE meals (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name STRING
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
