import json
import boto3
import os

rds_data_client = boto3.client('rds-data')

cluster_arn = os.environ['CLUSTER_ARN']
secret_arn = os.environ['SECRET_ARN']
database_name = os.environ['DB_NAME']

def lambda_handler(event, context):
    try:
        profile_id = event['pathParameters']['profileId']
        body = json.loads(event['body'])
        title = body.get('title')

        if not title:
            return {
                'statusCode': 400,
                'body': json.dumps('Missing title in request body.')
            }
        database_exists = check_database_exists()
        if database_exists:
            updated = update_profile(profile_id, title)
            if updated:
                return {
                    'statusCode': 200,
                    'body': json.dumps('Profile updated successfully!')
                }
            else:
                return {
                    'statusCode': 404,
                    'body': json.dumps('Profile not found.')
                }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('Database "Profile" does not exist.')
            }
    except Exception as e:
        print(f"Error updating profile: {str(e)}")
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
            sql="SHOW TABLES LIKE 'Profile';"
        )

        return len(response['records']) > 0
    except Exception as e:
        print(f"Error checking database existence: {str(e)}")
        raise

def update_profile(profile_id, title):
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="UPDATE Profile SET title = :title WHERE profileId = :profileId;",
            parameters=[
                {'name': 'title', 'value': {'stringValue': title}},
                {'name': 'profileId', 'value': {'longValue': int(profile_id)}}
            ]
        )
        return response['numberOfRecordsUpdated'] > 0
    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        raise
