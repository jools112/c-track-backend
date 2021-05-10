--
-- File generated with SQLiteStudio v3.3.3 on Mon May 10 10:49:22 2021
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

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
    meal_id INTEGER,
    food_id INT
);


-- Table: meals
DROP TABLE IF EXISTS meals;

CREATE TABLE meals (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name STRING
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
