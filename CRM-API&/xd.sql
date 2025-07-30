CREATE TABLE customers (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    created_at TIMESTAMP
);

INSERT INTO customers (id, name, email, created_at)
VALUES
    (1, 'John Doe', 'john.doe@example.com', NOW()),
    (2, 'Jane Smith', 'jane.smith@example.com', NOW()),
    (3, 'Alice Johnson', 'alice.johnson@example.com', NOW()),
    (4, 'Bob Brown', 'bob.brown@example.com', NOW()),
    (5, 'Charlie Davis', 'charlie.davis@example.com', NOW());
    