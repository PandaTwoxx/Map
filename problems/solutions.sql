-- @block 1
SELECT dept_name, COUNT(*) AS num_students
FROM student
GROUP BY dept_name;
-- @block 2 
-- no gender column :()
SELECT * FROM student
-- @block 3
WITH StudentGPA AS (
    SELECT ID, 
           AVG(CASE grade 
                   WHEN 'A' THEN 4.0 
                   WHEN 'A-' THEN 3.7 
                   WHEN 'B+' THEN 3.3 
                   WHEN 'B' THEN 3.0 
                   WHEN 'B-' THEN 2.7 
                   WHEN 'C+' THEN 2.3 
                   WHEN 'C' THEN 2.0 
                   WHEN 'C-' THEN 1.7 
                   WHEN 'D+' THEN 1.3 
                   WHEN 'D' THEN 1.0 
                   WHEN 'F' THEN 0.0 
                   ELSE NULL 
                END) AS GPA
    FROM takes
    GROUP BY ID
)
SELECT student.ID, student.name, student.dept_name
FROM student
JOIN StudentGPA ON student.ID = StudentGPA.ID
WHERE GPA > 3.5;

-- @block 4
-- sadly, this doesnt exsist yet :(
SELECT s.ID, s.name
FROM student s
JOIN takes t ON s.ID = t.ID
JOIN course c ON t.course_id = c.course_id
GROUP BY s.ID, s.name
HAVING COUNT(DISTINCT c.dept_name) > 1;

-- @block 5
SELECT DISTINCT s2.ID, s2.name
FROM takes t1
JOIN takes t2 ON t1.course_id = t2.course_id
               AND t1.sec_id = t2.sec_id
               AND t1.semester = t2.semester
               AND t1.year = t2.year
JOIN student s2 ON t2.ID = s2.ID
WHERE t1.ID = 'student id :)'
  AND s2.ID <> 'same student id :)';

-- @block 6
SELECT dept_name, AVG(salary) AS avg_salary
FROM instructor
GROUP BY dept_name;

-- @block 7
-- sadly, this doesnt exsist yet too :(
SELECT i.ID, i.name
FROM instructor i
JOIN teaches t ON i.ID = t.ID
JOIN course c ON t.course_id = c.course_id
GROUP BY i.ID, i.name
HAVING COUNT(DISTINCT c.dept_name) > 1;


-- @block 8
SELECT i.ID, i.name, i.salary
FROM instructor i
ORDER BY salary DESC
LIMIT 1;

-- @block 9
SELECT i.ID, i.name
FROM instructor i
JOIN teaches t ON i.ID = t.ID
JOIN section s ON t.course_id = s.course_id
                 AND t.sec_id = s.sec_id
                 AND t.semester = s.semester
                 AND t.year = s.year
GROUP BY i.ID, i.name
HAVING COUNT(DISTINCT CONCAT(s.building, '-', s.room_number)) > 1;

-- @block 10
SELECT i.ID, i.name
FROM instructor i
JOIN teaches t ON i.ID = t.ID
GROUP BY i.ID, i.name
HAVING COUNT(DISTINCT t.course_id) > 1;

-- @block 11
SELECT dept_name, COUNT(course_id) AS total_courses
FROM course
GROUP BY dept_name;

-- @block 12
SELECT c.course_id, c.title
FROM course c
JOIN section s ON c.course_id = s.course_id
JOIN takes t ON s.course_id = t.course_id
              AND s.sec_id = t.sec_id
              AND s.semester = t.semester
              AND s.year = t.year
GROUP BY c.course_id, c.title
HAVING COUNT(t.ID) < 10;

-- @block 13
SELECT building, room_number, capacity
FROM classroom
ORDER BY capacity DESC
LIMIT 1;

-- @block 14
SELECT c.course_id, c.title
FROM course c
JOIN teaches t ON c.course_id = t.course_id
                 AND c.sec_id = t.sec_id
                 AND c.semester = t.semester
                 AND c.year = t.year
WHERE t.ID = 'Hi im a professor :)';

-- @block 15
SELECT COUNT(DISTINCT t.ID) AS total_students
FROM takes t
JOIN teaches te ON t.course_id = te.course_id
                 AND t.sec_id = te.sec_id
                 AND t.semester = te.semester
                 AND t.year = te.year
WHERE te.ID = 'Hi im a professor :)';

-- @block 16
SELECT dept_name, COUNT(ID) AS total_students
FROM student
GROUP BY dept_name;

-- @block 17
-- sry no gender here
SELECT * FROM student

-- @block 18
-- you mean courses?
SELECT DISTINCT c.title AS course_title
FROM course c
JOIN department d ON c.dept_name = d.dept_name
WHERE d.dept_name = 'de department';

-- @block 19
SELECT s.dept_name, AVG(
    CASE
        WHEN t.grade = 'A' THEN 4.0
        WHEN t.grade = 'A-' THEN 3.7
        WHEN t.grade = 'B+' THEN 3.3
        WHEN t.grade = 'B' THEN 3.0
        WHEN t.grade = 'B-' THEN 2.7
        WHEN t.grade = 'C+' THEN 2.3
        WHEN t.grade = 'C' THEN 2.0
        WHEN t.grade = 'C-' THEN 1.7
        WHEN t.grade = 'D+' THEN 1.3
        WHEN t.grade = 'D' THEN 1.0
        WHEN t.grade = 'F' THEN 0.0
        ELSE NULL
    END
) AS avg_gpa
FROM student s
JOIN takes t ON s.ID = t.ID
GROUP BY s.dept_name
ORDER BY avg_gpa DESC
LIMIT 1;

-- @block 20
SELECT d.dept_name, SUM(i.salary) AS total_salary
FROM instructor i
JOIN department d ON i.dept_name = d.dept_name
GROUP BY d.dept_name
ORDER BY total_salary DESC
LIMIT 1;
