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
        database_exists = check_database_exists()

        if database_exists:
            job_details = get_job(job_id)
            if job_details:
                return {
                    'statusCode': 200,
                    'body': json.dumps(job_details)
                }
            else:
                return {
                    'statusCode': 404,
                    'body': json.dumps(f'Job with ID {job_id} not found.')
                }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('Database table "Job" does not exist.')
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
            sql="SHOW TABLES LIKE 'Job';"
        )
        return len(response['records']) > 0
    except Exception as e:
        print(f"Error checking database existence: {str(e)}")
        raise

def get_job(job_id):
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="SELECT * FROM Job WHERE jobId = :jobId;",
            parameters=[
                {'name': 'jobId', 'value': {'longValue': int(job_id)}}
            ]
        )

        records = response.get('records', [])
        if records:
            record = records[0]
            return {
                'jobId': record[0].get('longValue', 'N/A') if 'longValue' in record[0] else 'N/A',
                'title': record[1].get('stringValue', 'N/A') if 'stringValue' in record[1] else 'N/A',
                'description': record[2].get('stringValue', 'N/A') if 'stringValue' in record[2] else 'N/A',
                'requirements': record[3].get('stringValue', 'N/A') if 'stringValue' in record[3] else 'N/A',
                'companyId': record[4].get('longValue', 'N/A') if 'longValue' in record[4] else 'N/A'
            }
        else:
            return None
    except Exception as e:
        print(f"Error retrieving job details: {str(e)}")
        raise
