-- Ініціалізація бази даних
\c contacts_db;

-- Створення enum типу для ролей
CREATE TYPE userrole AS ENUM ('user', 'admin');

-- Створення таблиці користувачів
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    avatar_url VARCHAR(255),
    role userrole NOT NULL DEFAULT 'user',
    is_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Створення таблиці контактів з зв'язком до користувачів
CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    birth_date DATE NOT NULL,
    additional_data TEXT,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
);

-- Створення індексів
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_contacts_first_name ON contacts(first_name);
CREATE INDEX IF NOT EXISTS idx_contacts_last_name ON contacts(last_name);
CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);
CREATE INDEX IF NOT EXISTS idx_contacts_owner_id ON contacts(owner_id);

-- Тестовий адмін користувач (пароль: adminpassword)
INSERT INTO users (username, email, hashed_password, role, is_verified) 
VALUES (
    'admin', 
    'admin@example.com', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAuuNXIz.3m',  -- adminpassword
    'admin',
    TRUE
) ON CONFLICT (email) DO NOTHING;

-- Тестовий звичайний користувач (пароль: testpassword)
INSERT INTO users (username, email, hashed_password, role, is_verified) 
VALUES (
    'testuser', 
    'test@example.com', 
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  -- testpassword
    'user',
    TRUE
) ON CONFLICT (email) DO NOTHING;

-- Тестові контакти для тестового користувача
INSERT INTO contacts (first_name, last_name, email, phone_number, birth_date, additional_data, owner_id) 
SELECT 
    'Іван', 'Петренко', 'ivan.petrenko@example.com', '+380501234567', '1990-05-15', 'Тестовий контакт', u.id
FROM users u WHERE u.email = 'test@example.com'
ON CONFLICT DO NOTHING;

INSERT INTO contacts (first_name, last_name, email, phone_number, birth_date, additional_data, owner_id) 
SELECT 
    'Марія', 'Коваленко', 'maria.kovalenko@example.com', '+380671234567', '1985-12-25', 'Новорічний контакт', u.id
FROM users u WHERE u.email = 'test@example.com'
ON CONFLICT DO NOTHING;

INSERT INTO contacts (first_name, last_name, email, phone_number, birth_date, additional_data, owner_id) 
SELECT 
    'Олександр', 'Сидоренко', 'alex.sydorenko@example.com', '+380991234567', '1992-08-22', 'Літній контакт', u.id
FROM users u WHERE u.email = 'test@example.com'
ON CONFLICT DO NOTHING;

-- Тестові контакти для адмін користувача
INSERT INTO contacts (first_name, last_name, email, phone_number, birth_date, additional_data, owner_id) 
SELECT 
    'Анна', 'Шевченко', 'anna.shevchenko@example.com', '+380631234567', '1988-03-10', 'Адмін контакт', u.id
FROM users u WHERE u.email = 'admin@example.com'
ON CONFLICT DO NOTHING;