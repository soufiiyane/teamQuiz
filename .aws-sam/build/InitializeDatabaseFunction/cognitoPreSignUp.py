import json
import boto3
import os

# Initialize the RDS Data Client
rds_data_client = boto3.client('rds-data')

# Environment variables for the RDS cluster
cluster_arn = os.environ['CLUSTER_ARN']
secret_arn = os.environ['SECRET_ARN']
database_name = os.environ['DB_NAME']

def lambda_handler(event, context):
    try:
        # Extract user attributes from the event
        user_attributes = event['request']['userAttributes']
        user_name = event['userName']
        first_name = user_attributes.get('given_name', '')
        last_name = user_attributes.get('family_name', '')
        email = user_attributes.get('email', '')

        # Insert user into the RDS table
        insert_user(user_name, first_name, last_name, email)

        return event
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return event

def insert_user(user_name, first_name, last_name, email):
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="INSERT INTO User (userName, firstName, lastName, email, role, createdAt, updatedAt) VALUES (:userName, :firstName, :lastName, :email, :role, NOW(), NOW());",
            parameters=[
                {'name': 'userName', 'value': {'stringValue': user_name}},
                {'name': 'firstName', 'value': {'stringValue': first_name}},
                {'name': 'lastName', 'value': {'stringValue': last_name}},
                {'name': 'email', 'value': {'stringValue': email}},
                {'name': 'role', 'value': {'stringValue': 'user'}}
            ]
        )
        print(f"Insert response: {response}")
    except Exception as e:
        print(f"Error inserting user: {str(e)}")
        raise
