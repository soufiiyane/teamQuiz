import json
import boto3
import os

def lambda_handler(event, context):
    cluster_arn = os.environ['CLUSTER_ARN']
    secret_arn = os.environ['SECRET_ARN']
    database_name = os.environ['DB_NAME']

    rds_client = boto3.client('rds-data')

    sql_statements = [
        """
        CREATE TABLE User (
            userId INT AUTO_INCREMENT PRIMARY KEY,
            firstName VARCHAR(255) NOT NULL,
            lastName VARCHAR(255) NOT NULL,
            userName VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            role VARCHAR(50) NOT NULL,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE Company (
            companyId INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            location VARCHAR(255),
            description TEXT
        );
        """,
        """
        CREATE TABLE Profile (
            profileId INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL
        );
        """,
        """
        CREATE TABLE Job (
            jobId INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            requirements TEXT,
            companyId INT,
            FOREIGN KEY (companyId) REFERENCES Company(companyId) ON DELETE SET NULL
        );
        """,
        """
        CREATE TABLE Quiz (
            id INT AUTO_INCREMENT PRIMARY KEY,
            profileId INT,
            description TEXT,
            jobId INT,
            questionIds TEXT,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            userId INT,
            timer INT,
            numberQuestions INT,
            FOREIGN KEY (profileId) REFERENCES Profile(profileId) ON DELETE SET NULL,
            FOREIGN KEY (jobId) REFERENCES Job(jobId) ON DELETE SET NULL,
            FOREIGN KEY (userId) REFERENCES User(userId) ON DELETE SET NULL
        );
        """,
        """
        CREATE TABLE Questions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            profileId INT,
            text TEXT NOT NULL,
            type VARCHAR(50),
            options TEXT,
            answer TEXT,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (profileId) REFERENCES Profile(profileId) ON DELETE SET NULL
        );
        """,
        """
        CREATE TABLE Resume (
            resumeId INT AUTO_INCREMENT PRIMARY KEY,
            userId INT,
            jobId INT,
            resumeUrl VARCHAR(255),
            uploadedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (userId) REFERENCES User(userId) ON DELETE CASCADE,
            FOREIGN KEY (jobId) REFERENCES Job(jobId) ON DELETE SET NULL
        );
        """,
        """
        CREATE TABLE Application (
            applicationId INT AUTO_INCREMENT PRIMARY KEY,
            userId INT,
            jobId INT,
            resumeId INT,
            status VARCHAR(50),
            submittedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (userId) REFERENCES User(userId) ON DELETE CASCADE,
            FOREIGN KEY (jobId) REFERENCES Job(jobId) ON DELETE SET NULL,
            FOREIGN KEY (resumeId) REFERENCES Resume(resumeId) ON DELETE SET NULL
        );
        """,
        """
        CREATE TABLE QuizHistory (
            historyId INT AUTO_INCREMENT PRIMARY KEY,
            userId INT,
            quizId INT,
            score DECIMAL(5, 2),
            status VARCHAR(50),
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (userId) REFERENCES User(userId) ON DELETE CASCADE,
            FOREIGN KEY (quizId) REFERENCES Quiz(id) ON DELETE CASCADE
        );
        """
    ]

    try:
        for statement in sql_statements:
            response = rds_client.execute_statement(
                resourceArn=cluster_arn,
                secretArn=secret_arn,
                database=database_name,
                sql=statement
            )
        return {
            'statusCode': 200,
            'body': json.dumps('Database initialized successfully')
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error initializing database: {str(e)}')
        }
