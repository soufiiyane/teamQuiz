import json
import boto3
import os

rds_data_client = boto3.client('rds-data')

cluster_arn = os.environ['CLUSTER_ARN']
secret_arn = os.environ['SECRET_ARN']
database_name = os.environ['DB_NAME']


def lambda_handler(event, context):
    profile_id = event['pathParameters']['profileId']
    database_exists = check_database_exists()

    if database_exists:
        if delete_profile(profile_id):
            return {
                'statusCode': 200,
                'body': json.dumps(f'Profile with ID {profile_id} deleted successfully!')
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps(f'Profile with ID {profile_id} not found.')
            }
    else:
        return {
            'statusCode': 404,
            'body': json.dumps('Database "Profile" does not exist.')
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


def delete_profile(profile_id):
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="DELETE FROM Profile WHERE profileId = :profileId;",
            parameters=[
                {'name': 'profileId', 'value': {'stringValue': profile_id}}
            ]
        )

        return response['numberOfRecordsUpdated'] > 0
    except Exception as e:
        print(f"Error deleting profile: {str(e)}")
        raise
