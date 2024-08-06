import json
import boto3
import os

rds_data_client = boto3.client('rds-data')

cluster_arn = os.environ['CLUSTER_ARN']
secret_arn = os.environ['SECRET_ARN']
database_name = os.environ['DB_NAME']

def lambda_handler(event, context):
    try:
        company_id = event['pathParameters']['companyId']
        body = json.loads(event['body'])
        name = body.get('name')
        location = body.get('location')
        description = body.get('description')

        if not name and not location and not description:
            return {
                'statusCode': 400,
                'body': json.dumps('At least one field (name, location, description) must be provided for update.')
            }

        database_exists = check_database_exists()
        if database_exists:
            updated = update_company(company_id, name, location, description)
            if updated:
                return {
                    'statusCode': 200,
                    'body': json.dumps('Company updated successfully!')
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
        print(f"Error updating company: {str(e)}")
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

def update_company(company_id, name, location, description):
    try:
        sql = "UPDATE Company SET "
        parameters = []

        if name:
            sql += "name = :name, "
            parameters.append({'name': 'name', 'value': {'stringValue': name}})
        if location:
            sql += "location = :location, "
            parameters.append({'name': 'location', 'value': {'stringValue': location}})
        if description:
            sql += "description = :description, "
            parameters.append({'name': 'description', 'value': {'stringValue': description}})

        # Remove trailing comma and space
        sql = sql.rstrip(', ')
        sql += " WHERE companyId = :companyId;"
        parameters.append({'name': 'companyId', 'value': {'longValue': int(company_id)}})

        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql=sql,
            parameters=parameters
        )
        return response['numberOfRecordsUpdated'] > 0
    except Exception as e:
        print(f"Error updating company: {str(e)}")
        raise
