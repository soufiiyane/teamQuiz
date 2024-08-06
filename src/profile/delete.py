import json
import boto3
import os

rds_data_client = boto3.client('rds-data')

cluster_arn = os.environ['CLUSTER_ARN']
secret_arn = os.environ['SECRET_ARN']
database_name = os.environ['DB_NAME']


def lambda_handler(event, context):
    print(event)
    profile_id = event['pathParameters']['profileId']

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
