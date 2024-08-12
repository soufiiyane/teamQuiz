import json
import boto3
import os


def table_exists(rds_client, cluster_arn, secret_arn, database_name, table_name):
    query = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{database_name}' AND table_name = '{table_name}'"
    try:
        response = rds_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql=query
        )
        count = response['records'][0][0]['longValue']
        return count > 0
    except Exception as e:
        print(f"Error checking if table {table_name} exists: {str(e)}")
        return False


def lambda_handler(event, context):
    cluster_arn = os.environ['CLUSTER_ARN']
    secret_arn = os.environ['SECRET_ARN']
    database_name = os.environ['DB_NAME']

    rds_client = boto3.client('rds-data')

    tables = {
        "User": """
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
        "Company": """
            CREATE TABLE Company (
                companyId INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                location VARCHAR(255),
                description TEXT
            );
        """,
        "Profile": """
            CREATE TABLE Profile (
                profileId INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL
            );
        """,
        "Job": """
            CREATE TABLE Job (
                jobId INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                requirements TEXT,
                companyId INT,
                FOREIGN KEY (companyId) REFERENCES Company(companyId) ON DELETE SET NULL
            );
        """,
        "Quiz": """
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
        "Questions": """
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
        "Resume": """
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
        "Application": """
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
        "QuizHistory": """
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
    }

    try:
        for table_name, create_statement in tables.items():
            if not table_exists(rds_client, cluster_arn, secret_arn, database_name, table_name):
                response = rds_client.execute_statement(
                    resourceArn=cluster_arn,
                    secretArn=secret_arn,
                    database=database_name,
                    sql=create_statement
                )
                print(f"Created table: {table_name}")
            else:
                print(f"Table {table_name} already exists.")

        return {
            'statusCode': 200,
            'body': json.dumps('Database initialization completed')
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error initializing database: {str(e)}')
        }
