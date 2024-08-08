import json
import boto3
import os

rds_data_client = boto3.client('rds-data')

cluster_arn = os.environ['CLUSTER_ARN']
secret_arn = os.environ['SECRET_ARN']
database_name = os.environ['DB_NAME']

def lambda_handler(event, context):
    try:
        # Ensure the table exists
        if not check_database_exists():
            return {
                'statusCode': 500,
                'body': json.dumps('Table does not exist in the database.')
            }

        body = json.loads(event.get('body', '{}'))
        title = body.get('title')
        description = body.get('description')
        requirements = body.get('requirements')
        company_id = int(body.get('companyId'))

        if not title:
            return {
                'statusCode': 400,
                'body': json.dumps('Title is required.')
            }

        insert_job(title, description, requirements, company_id)
        return {
            'statusCode': 200,
            'body': json.dumps('Job created successfully!')
        }
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps('Internal server error.')
        }

def insert_job(title, description, requirements, company_id):
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="INSERT INTO Job (title, description, requirements, companyId) VALUES (:title, :description, :requirements, :companyId);",
            parameters=[
                {'name': 'title', 'value': {'stringValue': title}},
                {'name': 'description', 'value': {'stringValue': description}},
                {'name': 'requirements', 'value': {'stringValue': requirements}},
                {'name': 'companyId', 'value': {'longValue': company_id}}
            ]
        )
        print(f"Insert response: {response}")
    except Exception as e:
        print(f"Error inserting job: {str(e)}")
        raise

def check_database_exists():
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="SHOW TABLES LIKE 'Job';"
        )
        return len(response['records']) > 0
    except Exception as e:
        print(f"Error checking database existence: {str(e)}")
        raise
