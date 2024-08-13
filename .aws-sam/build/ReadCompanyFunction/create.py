import json
import boto3
import os

rds_data_client = boto3.client('rds-data')

cluster_arn = os.environ['CLUSTER_ARN']
secret_arn = os.environ['SECRET_ARN']
database_name = os.environ['DB_NAME']

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        name = body.get('name')
        location = body.get('location', '')
        description = body.get('description', '')

        database_exists = check_database_exists()

        if database_exists:
            insert_company(name, location, description)
            return {
                'statusCode': 200,
                'body': json.dumps('Company inserted successfully!')
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('Database "Company" does not exist.')
            }
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps('Error processing request')
        }

def check_database_exists():
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="SHOW TABLES LIKE 'Company';"
        )
        return len(response['records']) > 0
    except Exception as e:
        print(f"Error checking database existence: {str(e)}")
        raise

def insert_company(name, location, description):
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="INSERT INTO Company (name, location, description) VALUES (:name, :location, :description);",
            parameters=[
                {'name': 'name', 'value': {'stringValue': name}},
                {'name': 'location', 'value': {'stringValue': location}},
                {'name': 'description', 'value': {'stringValue': description}}
            ]
        )
        print(f"Insert response: {response}")
    except Exception as e:
        print(f"Error inserting company: {str(e)}")
        raise
