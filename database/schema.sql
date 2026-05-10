CREATE DATABASE IF NOT EXISTS traffic_ai;
USE traffic_ai;

CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS traffic_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    time TIME NOT NULL,
    location VARCHAR(150) NOT NULL,
    lat DECIMAL(10, 7) NOT NULL,
    lng DECIMAL(10, 7) NOT NULL,
    weather VARCHAR(80) NOT NULL,
    traffic_density FLOAT NOT NULL,
    vehicle_count INT NOT NULL,
    speed FLOAT NOT NULL,
    road_condition VARCHAR(80) NOT NULL,
    accident ENUM('Low Risk', 'Medium Risk', 'High Risk') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    location VARCHAR(150) NOT NULL,
    risk_level ENUM('Low Risk', 'Medium Risk', 'High Risk') NOT NULL,
    message TEXT NOT NULL,
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_traffic_date ON traffic_records(date);
CREATE INDEX idx_traffic_risk ON traffic_records(accident);
CREATE INDEX idx_alert_active ON alerts(is_active);
