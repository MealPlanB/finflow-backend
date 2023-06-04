-- 데이터베이스 생성
CREATE DATABASE finflow;

-- 사용할 데이터베이스 선택
USE finflow;

-- 유저 테이블 생성
CREATE TABLE users (
                       id INT PRIMARY KEY AUTO_INCREMENT,
                       name VARCHAR(50) NOT NULL,
                       money INT DEFAULT 0
);

-- 거래 테이블 생성
CREATE TABLE trade (
                       id INT PRIMARY KEY AUTO_INCREMENT,
                       user_id INT NOT NULL,
                       stock_name VARCHAR(255) NOT NULL,
                       quantity INT NOT NULL,
                       price DECIMAL(18, 2) NOT NULL,
                       sold_quantity INT DEFAULT 0,
                       timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 시즌 테이블 생성
CREATE TABLE seasons (
                         id INT PRIMARY KEY AUTO_INCREMENT,
                         start_date DATE NOT NULL,
                         end_date DATE NOT NULL,
                         host VARCHAR(255) DEFAULT ''
);

-- 시즌 데이터 삽입
INSERT INTO seasons (start_date, end_date) VALUES ('2000-01-01', '2000-01-01');
