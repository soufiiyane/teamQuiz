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
            if delete_job(job_id):
                return {
                    'statusCode': 200,
                    'body': json.dumps(f'Job with ID {job_id} deleted successfully!')
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

def delete_job(job_id):
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="DELETE FROM Job WHERE jobId = :jobId;",
            parameters=[
                {'name': 'jobId', 'value': {'longValue': int(job_id)}}
            ]
        )

        return response['numberOfRecordsUpdated'] > 0
    except Exception as e:
        print(f"Error deleting job: {str(e)}")
        raise
