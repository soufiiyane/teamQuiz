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
            question = get_question(question_id)
            if question:
                return {
                    'statusCode': 200,
                    'body': json.dumps(question)
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

def get_question(question_id):
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="SELECT * FROM Questions WHERE id = :id;",
            parameters=[
                {'name': 'id', 'value': {'longValue': int(question_id)}}
            ]
        )
        records = response['records']
        if records:
            return {
                'id': records[0][0]['longValue'],
                'profileId': records[0][1]['longValue'],
                'text': records[0][2]['stringValue'],
                'type': records[0][3]['stringValue'],
                'options': json.loads(records[0][4]['stringValue']),
                'answer': json.loads(records[0][5]['stringValue']),
                'createdAt': records[0][6]['stringValue'],
                'updatedAt': records[0][7]['stringValue']
            }
        else:
            return None
    except Exception as e:
        print(f"Error retrieving question: {str(e)}")
        raise
