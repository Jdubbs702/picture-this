CREATE DATABASE picture_this;
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    username VARCHAR(100) NOT NULL,
    hash VARCHAR(100) NOT NULL
);