import boto3
import os
import json
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    # Define CORS headers
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'OPTIONS,POST',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization'
    }

    try:
        client = boto3.client('cognito-idp')

        # Handle preflight OPTIONS requests
        if event['httpMethod'] == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': cors_headers
            }

        # Check for required fields and HTTP method
        if 'body' not in event or event['httpMethod'] != 'POST':
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'msg': 'Bad Request'})
            }

        body = json.loads(event["body"])
        if 'email' not in body or "password" not in body:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'msg': 'Missing fields in request body'})
            }

        username = body["email"]
        password = body["password"]

        # Initiate authentication with Cognito
        response = client.initiate_auth(
            ClientId=os.environ['CLIENT_ID'],
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )

        id_token = response['AuthenticationResult']['IdToken']

        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'message': 'Successfully signed in',
                'id_token': id_token,
            })
        }

    except ClientError as e:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps({
                'error': str(e)
            })
        }
