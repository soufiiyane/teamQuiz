import json
import boto3
import os

rds_data_client = boto3.client('rds-data')

cluster_arn = os.environ['CLUSTER_ARN']
secret_arn = os.environ['SECRET_ARN']
database_name = os.environ['DB_NAME']

def lambda_handler(event, context):
    company_id = event.get('pathParameters', {}).get('companyId')

    if not company_id:
        return {
            'statusCode': 400,
            'body': json.dumps('Company ID is required.')
        }

    try:
        database_exists = check_database_exists()
        if database_exists:
            company = get_company(company_id)
            if company:
                return {
                    'statusCode': 200,
                    'body': json.dumps(company)
                }
            else:
                return {
                    'statusCode': 404,
                    'body': json.dumps('Company not found.')
                }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('Database "Company" does not exist.')
            }
    except Exception as e:
        print(f"Error retrieving company: {str(e)}")
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
            sql="SHOW TABLES LIKE 'Company';"
        )

        return len(response['records']) > 0
    except Exception as e:
        print(f"Error checking database existence: {str(e)}")
        raise

def get_company(company_id):
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="SELECT * FROM Company WHERE companyId = :companyId;",
            parameters=[
                {'name': 'companyId', 'value': {'longValue': int(company_id)}}
            ]
        )

        if response['records']:
            # Convert the response to a dictionary
            record = response['records'][0]
            company = {
                'companyId': record[0]['longValue'],
                'name': record[1]['stringValue'],
                'location': record[2]['stringValue'] if 'stringValue' in record[2] else None,
                'description': record[3]['stringValue'] if 'stringValue' in record[3] else None
            }
            return company
        else:
            return None
    except Exception as e:
        print(f"Error fetching company from database: {str(e)}")
        raise
