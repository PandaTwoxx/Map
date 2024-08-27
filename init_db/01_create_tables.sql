DROP DATABASE IF EXISTS map;


CREATE DATABASE map;


USE map;


CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    firstname varchar(255) NOT NULL,
    lastname varchar(255) NOT NULL,
    username varchar(255) NOT NULL,
    PASSWORD varchar(255) NOT NULL,
    email varchar(255),
);


CREATE TABLE locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    -- note, this can be NULL
    name varchar(255),
    -- note, this can be NULL
    description varchar(255),
    location_details_id INT NOT NULL,
    FOREIGN KEY (location_details_id) REFERENCES location_details(id) ON DELETE CASCADE
);


CREATE TABLE location_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    -- results[0]['formatted']
    address varchar(255) NOT NULL,
    -- results[0]['lon']
    longitude DECIMAL(10, 8) NOT NULL,
    -- results[0]['lat']
    latitude DECIMAL(10, 8) NOT NULL,
);


-- think about why did I do this
CREATE TABLE users_locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    location_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE CASCADE
);