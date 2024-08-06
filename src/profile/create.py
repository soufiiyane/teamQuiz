import json
import boto3
import os

rds_data_client = boto3.client('rds-data')

cluster_arn = os.environ['CLUSTER_ARN']
secret_arn = os.environ['SECRET_ARN']
database_name = os.environ['DB_NAME']

def lambda_handler(event, context):
    try:
        title = json.loads(event.get('body', '{}')).get('title')

        if not title:
            return {
                'statusCode': 400,
                'body': json.dumps('Title is required.')
            }

        database_exists = check_database_exists()

        if database_exists:
            insert_title(title)
            return {
                'statusCode': 200,
                'body': json.dumps('Title inserted successfully!')
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('Database "Profile" does not exist.')
            }
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps('Internal server error.')
        }

def check_database_exists():
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="SHOW TABLES LIKE 'Profile';"
        )

        return len(response['records']) > 0
    except Exception as e:
        print(f"Error checking database existence: {str(e)}")
        raise

def insert_title(title):
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="INSERT INTO Profile (title) VALUES (:title);",
            parameters=[
                {'name': 'title', 'value': {'stringValue': title}}
            ]
        )
        print(f"Insert response: {response}")
    except Exception as e:
        print(f"Error inserting title: {str(e)}")
        raise
