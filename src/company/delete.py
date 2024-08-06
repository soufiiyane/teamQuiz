import json
import boto3
import os

rds_data_client = boto3.client('rds-data')

cluster_arn = os.environ['CLUSTER_ARN']
secret_arn = os.environ['SECRET_ARN']
database_name = os.environ['DB_NAME']

def lambda_handler(event, context):
    company_id = event['pathParameters']['companyId']
    database_exists = check_database_exists()

    if database_exists:
        if delete_company(company_id):
            return {
                'statusCode': 200,
                'body': json.dumps(f'Company with ID {company_id} deleted successfully!')
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps(f'Company with ID {company_id} not found.')
            }
    else:
        return {
            'statusCode': 404,
            'body': json.dumps('Database "Company" does not exist.')
        }

def check_database_exists():
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="SHOW TABLES LIKE 'Company';"
        )

        return len(response['records']) > 0
    except Exception as e:
        print(f"Error checking database existence: {str(e)}")
        raise

def delete_company(company_id):
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="DELETE FROM Company WHERE companyId = :companyId;",
            parameters=[
                {'name': 'companyId', 'value': {'longValue': int(company_id)}}
            ]
        )

        return response['numberOfRecordsUpdated'] > 0
    except Exception as e:
        print(f"Error deleting company: {str(e)}")
        raise
