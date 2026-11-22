-- schema for academic planner database

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('student', 'advisor'))
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL
);

-- main table, linked to users and courses
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    due_date TEXT NOT NULL,
    priority TEXT NOT NULL CHECK (priority IN ('High', 'Medium', 'Low')),
    status TEXT NOT NULL DEFAULT 'Pending'
        CHECK (status IN ('Pending', 'In Progress', 'Completed')),
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE RESTRICT
);

-- to make searching by student and due date faster
CREATE INDEX IF NOT EXISTS idx_assignments_student_due ON assignments(student_id, due_date);
