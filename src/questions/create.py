import json
import boto3
import os

rds_data_client = boto3.client('rds-data')

cluster_arn = os.environ['CLUSTER_ARN']
secret_arn = os.environ['SECRET_ARN']
database_name = os.environ['DB_NAME']

def lambda_handler(event, context):
    try:
        if not check_table_exists('Questions'):
            return {
                'statusCode': 500,
                'body': json.dumps('Table does not exist in the database.')
            }

        body = json.loads(event.get('body', '{}'))
        profile_id = body.get('profileId')
        text = body.get('text')
        q_type = body.get('type')
        options = body.get('options')
        answer = body.get('answer')

        if profile_id is None:
            return {
                'statusCode': 400,
                'body': json.dumps('Profile ID is required.')
            }
        if not text:
            return {
                'statusCode': 400,
                'body': json.dumps('Question text is required.')
            }
        if q_type is None:
            return {
                'statusCode': 400,
                'body': json.dumps('Question type is required.')
            }
        if options is None:
            return {
                'statusCode': 400,
                'body': json.dumps('Options are required.')
            }
        if answer is None:
            return {
                'statusCode': 400,
                'body': json.dumps('Answer is required.')
            }

        insert_question(profile_id, text, q_type, options, answer)
        return {
            'statusCode': 200,
            'body': json.dumps('Question created successfully!')
        }
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps('Internal server error.')
        }

def insert_question(profile_id, text, q_type, options, answer):
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="INSERT INTO Questions (profileId, text, type, options, answer) VALUES (:profileId, :text, :type, :options, :answer);",
            parameters=[
                {'name': 'profileId', 'value': {'longValue': profile_id}},
                {'name': 'text', 'value': {'stringValue': text}},
                {'name': 'type', 'value': {'stringValue': q_type}},
                {'name': 'options', 'value': {'stringValue': json.dumps(options)}},
                {'name': 'answer', 'value': {'stringValue': json.dumps(answer)}}
            ]
        )
        print(f"Insert response: {response}")
    except Exception as e:
        print(f"Error inserting question: {str(e)}")
        raise

def check_table_exists(table_name):
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql=f"SHOW TABLES LIKE '{table_name}';"
        )
        return len(response['records']) > 0
    except Exception as e:
        print(f"Error checking table existence: {str(e)}")
        raise
