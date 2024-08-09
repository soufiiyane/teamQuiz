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
        body = json.loads(event.get('body', '{}'))
        text = body.get('text')
        q_type = body.get('type')
        options = body.get('options')
        answer = body.get('answer')

        if not text and q_type is None and options is None and answer is None:
            return {
                'statusCode': 400,
                'body': json.dumps('At least one field (text, type, options, answer) must be provided for update.')
            }

        database_exists = check_table_exists()
        if database_exists:
            updated = update_question(question_id, text, q_type, options, answer)
            if updated:
                return {
                    'statusCode': 200,
                    'body': json.dumps(f'Question with ID {question_id} updated successfully!')
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
        print(f"Error updating question: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps('Internal server error.')
        }

def check_table_exists():
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

def update_question(question_id, text, q_type, options, answer):
    try:
        sql = "UPDATE Questions SET "
        parameters = []

        if text:
            sql += "text = :text, "
            parameters.append({'name': 'text', 'value': {'stringValue': text}})
        if q_type:
            sql += "type = :type, "
            parameters.append({'name': 'type', 'value': {'stringValue': q_type}})
        if options:
            sql += "options = :options, "
            parameters.append({'name': 'options', 'value': {'stringValue': json.dumps(options)}})
        if answer:
            sql += "answer = :answer, "
            parameters.append({'name': 'answer', 'value': {'stringValue': json.dumps(answer)}})

        sql = sql.rstrip(', ')
        sql += " WHERE id = :id;"
        parameters.append({'name': 'id', 'value': {'longValue': int(question_id)}})

        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql=sql,
            parameters=parameters
        )
        return response['numberOfRecordsUpdated'] > 0
    except Exception as e:
        print(f"Error updating question: {str(e)}")
        raise
