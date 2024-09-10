DROP DATABASE IF EXISTS test_docker_compose;


CREATE DATABASE test_docker_compose;


USE test_docker_compose;


CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    firstname varchar(255) NOT NULL,
    lastname varchar(255) NOT NULL,
    username varchar(255) NOT NULL,
    PASSWORD varchar(255) NOT NULL,
    email varchar(255) NOT NULL,
    CONSTRAINT unique_username UNIQUE(username),
    CONSTRAINT unique_email UNIQUE(email)
);


CREATE TABLE location_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    coordinate POINT NOT NULL
);


CREATE TABLE locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    address varchar(255) NOT NULL,
    name varchar(255) NOT NULL,
    description varchar(255) NOT NULL,
    location_details_id INT NOT NULL,
    FOREIGN KEY (location_details_id) REFERENCES location_details(id) ON DELETE CASCADE
);


-- think about why did I do this
CREATE TABLE users_locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    location_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE CASCADE
);