import json
import boto3
import os

rds_data_client = boto3.client('rds-data')

cluster_arn = os.environ['CLUSTER_ARN']
secret_arn = os.environ['SECRET_ARN']
database_name = os.environ['DB_NAME']


def lambda_handler(event, context):
    profile_id = event.get('pathParameters', {}).get('profileId')

    if not profile_id:
        return {
            'statusCode': 400,
            'body': json.dumps('Profile ID is required.')
        }

    try:
        database_exists = check_database_exists()
        if database_exists:
            profile = get_profile(profile_id)
            if profile:
                return {
                    'statusCode': 200,
                    'body': json.dumps(profile)
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
        print(f"Error retrieving profile: {str(e)}")
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


def get_profile(profile_id):
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="SELECT * FROM Profile WHERE profileId = :profileId;",
            parameters=[
                {'name': 'profileId', 'value': {'longValue': int(profile_id)}}
            ]
        )

        if response['records']:
            # Convert the response to a dictionary
            record = response['records'][0]
            profile = {
                'id': record[0]['longValue'],
                'title': record[1]['stringValue']
            }
            return profile
        else:
            return None
    except Exception as e:
        print(f"Error fetching profile from database: {str(e)}")
        raise
