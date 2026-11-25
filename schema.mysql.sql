-- MySQL schema (mirrors backend/models.py). SQLAlchemy creates these tables automatically
-- when DATABASE_URL points at MySQL; this file is for documentation / manual setup.
CREATE DATABASE IF NOT EXISTS timetable;
USE timetable;

CREATE TABLE faculty (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) NOT NULL);
CREATE TABLE batch   (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(50) NOT NULL, size INT NOT NULL);
CREATE TABLE room    (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(50) NOT NULL,
                      capacity INT NOT NULL, is_lab BOOLEAN NOT NULL DEFAULT FALSE);
CREATE TABLE slot    (id INT AUTO_INCREMENT PRIMARY KEY, day INT NOT NULL, period INT NOT NULL);

CREATE TABLE subject (
  id INT AUTO_INCREMENT PRIMARY KEY,
  code VARCHAR(20) NOT NULL, name VARCHAR(100) NOT NULL,
  faculty_id INT NOT NULL, batch_id INT NOT NULL,
  lectures_per_week INT NOT NULL DEFAULT 3, is_lab BOOLEAN NOT NULL DEFAULT FALSE,
  FOREIGN KEY (faculty_id) REFERENCES faculty(id),
  FOREIGN KEY (batch_id) REFERENCES batch(id)
);

CREATE TABLE faculty_unavailable (
  id INT AUTO_INCREMENT PRIMARY KEY, faculty_id INT NOT NULL, slot_id INT NOT NULL,
  FOREIGN KEY (faculty_id) REFERENCES faculty(id), FOREIGN KEY (slot_id) REFERENCES slot(id)
);

CREATE TABLE entry (   -- the generated timetable: one row per scheduled lecture
  id INT AUTO_INCREMENT PRIMARY KEY,
  subject_id INT NOT NULL, slot_id INT NOT NULL, room_id INT NOT NULL,
  FOREIGN KEY (subject_id) REFERENCES subject(id),
  FOREIGN KEY (slot_id) REFERENCES slot(id), FOREIGN KEY (room_id) REFERENCES room(id)
);
