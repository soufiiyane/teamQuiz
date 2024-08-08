import json
import boto3
import os

rds_data_client = boto3.client('rds-data')

cluster_arn = os.environ['CLUSTER_ARN']
secret_arn = os.environ['SECRET_ARN']
database_name = os.environ['DB_NAME']

def lambda_handler(event, context):
    try:
        job_id = event['pathParameters']['jobId']
        body = json.loads(event['body'])
        title = body.get('title')
        description = body.get('description')
        requirements = body.get('requirements')
        company_id = body.get('companyId')

        if not title and not description and not requirements and company_id is None:
            return {
                'statusCode': 400,
                'body': json.dumps('At least one field (title, description, requirements, companyId) must be provided for update.')
            }

        database_exists = check_database_exists()
        if database_exists:
            updated = update_job(job_id, title, description, requirements, company_id)
            if updated:
                return {
                    'statusCode': 200,
                    'body': json.dumps(f'Job with ID {job_id} updated successfully!')
                }
            else:
                return {
                    'statusCode': 404,
                    'body': json.dumps(f'Job with ID {job_id} not found.')
                }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('Database "Job" does not exist.')
            }
    except Exception as e:
        print(f"Error updating job: {str(e)}")
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
            sql="SHOW TABLES LIKE 'Job';"
        )
        return len(response['records']) > 0
    except Exception as e:
        print(f"Error checking database existence: {str(e)}")
        raise

def update_job(job_id, title, description, requirements, company_id):
    try:
        sql = "UPDATE Job SET "
        parameters = []

        if title:
            sql += "title = :title, "
            parameters.append({'name': 'title', 'value': {'stringValue': title}})
        if description:
            sql += "description = :description, "
            parameters.append({'name': 'description', 'value': {'stringValue': description}})
        if requirements:
            sql += "requirements = :requirements, "
            parameters.append({'name': 'requirements', 'value': {'stringValue': requirements}})
        if company_id is not None:
            sql += "companyId = :companyId, "
            parameters.append({'name': 'companyId', 'value': {'longValue': int(company_id)}})

        # Remove trailing comma and space
        sql = sql.rstrip(', ')
        sql += " WHERE jobId = :jobId;"
        parameters.append({'name': 'jobId', 'value': {'longValue': int(job_id)}})

        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql=sql,
            parameters=parameters
        )
        return response['numberOfRecordsUpdated'] > 0
    except Exception as e:
        print(f"Error updating job: {str(e)}")
        raise
