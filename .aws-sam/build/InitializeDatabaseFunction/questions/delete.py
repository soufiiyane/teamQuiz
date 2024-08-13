import json
import boto3
import os

rds_data_client = boto3.client('rds-data')

cluster_arn = os.environ['CLUSTER_ARN']
secret_arn = os.environ['SECRET_ARN']
database_name = os.environ['DB_NAME']

def lambda_handler(event, context):
    try:
        question_id = event['pathParameters']['questionsId']
        if check_database_exists():
            if delete_question(question_id):
                return {
                    'statusCode': 200,
                    'body': json.dumps(f'Question with ID {question_id} deleted successfully!')
                }
            else:
                return {
                    'statusCode': 404,
                    'body': json.dumps(f'Question with ID {question_id} not found.')
                }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('Table "Questions" does not exist.')
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
            sql="SHOW TABLES LIKE 'Questions';"
        )
        return len(response['records']) > 0
    except Exception as e:
        print(f"Error checking table existence: {str(e)}")
        raise

def delete_question(question_id):
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="DELETE FROM Questions WHERE id = :id;",
            parameters=[
                {'name': 'id', 'value': {'longValue': int(question_id)}}
            ]
        )
        return response['numberOfRecordsUpdated'] > 0
    except Exception as e:
        print(f"Error deleting question: {str(e)}")
        raise
