import json
import boto3
import os
import base64

rds_data_client = boto3.client('rds-data')
s3_client = boto3.client('s3')

cluster_arn = os.environ['CLUSTER_ARN']
secret_arn = os.environ['SECRET_ARN']
database_name = os.environ['DB_NAME']
s3_bucket_name = os.environ['RESUME_BUCKET']


def lambda_handler(event, context):
    print("Event:", event)  # Debugging statement

    try:
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('userId')
        job_id = body.get('jobId')
        resume_file = body.get('resumeFile')  # Assuming resumeFile is base64 encoded

        # Check if fields are provided
        if user_id is None:
            return {
                'statusCode': 400,
                'body': json.dumps('userId is required.')
            }
        if job_id is None:
            return {
                'statusCode': 400,
                'body': json.dumps('jobId is required.')
            }
        if resume_file is None:
            return {
                'statusCode': 400,
                'body': json.dumps('resumeFile is required.')
            }

        # Convert userId and jobId to integers
        try:
            user_id = int(user_id)
            job_id = int(job_id)
        except ValueError:
            return {
                'statusCode': 400,
                'body': json.dumps('userId and jobId must be integers.')
            }

        # Check if user and job exist
        if not check_user_exists(user_id):
            return {
                'statusCode': 404,
                'body': json.dumps('User not found.')
            }

        if not check_job_exists(job_id):
            return {
                'statusCode': 404,
                'body': json.dumps('Job not found.')
            }

        # Upload resume to S3 and get the URL
        resume_url = upload_resume_to_s3(resume_file, user_id, job_id)
        if not resume_url:
            return {
                'statusCode': 500,
                'body': json.dumps('Failed to upload resume.')
            }

        # Create application with the retrieved resumeUrl
        resume_id = upload_resume(user_id, job_id, resume_url)
        if not resume_id:
            return {
                'statusCode': 500,
                'body': json.dumps('Failed to upload resume record.')
            }

        # Create application with the retrieved resumeId
        create_application(user_id, job_id, resume_id)
        return {
            'statusCode': 200,
            'body': json.dumps('Application created successfully!')
        }
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps('Internal server error.')
        }


def upload_resume_to_s3(resume_file, user_id, job_id):
    try:
        # Decode base64 encoded resume file
        resume_file_content = base64.b64decode(resume_file)

        # Generate a unique file name
        resume_file_name = f"resumeteamquiz2024_{user_id}_{job_id}.pdf"  # Adjust the extension based on your file type

        # Upload file to S3
        s3_client.put_object(
            Bucket=s3_bucket_name,
            Key=resume_file_name,
            Body=resume_file_content,
            ContentType='application/pdf'  # Adjust MIME type if necessary
        )

        # Generate the S3 URL
        resume_url = f"https://{s3_bucket_name}.s3.amazonaws.com/{resume_file_name}"
        print(f"Resume uploaded successfully to S3 with URL: {resume_url}")
        return resume_url
    except Exception as e:
        print(f"Error uploading resume to S3: {str(e)}")
        return None


def upload_resume(user_id, job_id, resume_url):
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="INSERT INTO Resume (userId, jobId, resumeUrl) VALUES (:userId, :jobId, :resumeUrl);",
            parameters=[
                {'name': 'userId', 'value': {'longValue': user_id}},
                {'name': 'jobId', 'value': {'longValue': job_id}},
                {'name': 'resumeUrl', 'value': {'stringValue': resume_url}}
            ],
            includeResultMetadata=True
        )
        # Extract resumeId from the response
        resume_id = response['generatedFields'][0]['longValue']
        print(f"Resume record uploaded successfully with resumeId: {resume_id}")
        return resume_id
    except Exception as e:
        print(f"Error uploading resume record: {str(e)}")
        return None


def create_application(user_id, job_id, resume_id):
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="INSERT INTO Application (userId, jobId, resumeId) VALUES (:userId, :jobId, :resumeId);",
            parameters=[
                {'name': 'userId', 'value': {'longValue': user_id}},
                {'name': 'jobId', 'value': {'longValue': job_id}},
                {'name': 'resumeId', 'value': {'longValue': resume_id}}
            ]
        )
        print(f"Application created successfully: {response}")
    except Exception as e:
        print(f"Error creating application: {str(e)}")
        raise


def check_user_exists(user_id):
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="SELECT 1 FROM User WHERE userId = :userId;",
            parameters=[
                {'name': 'userId', 'value': {'longValue': user_id}}
            ]
        )
        return len(response['records']) > 0
    except Exception as e:
        print(f"Error checking user existence: {str(e)}")
        raise


def check_job_exists(job_id):
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="SELECT 1 FROM Job WHERE jobId = :jobId;",
            parameters=[
                {'name': 'jobId', 'value': {'longValue': job_id}}
            ]
        )
        return len(response['records']) > 0
    except Exception as e:
        print(f"Error checking job existence: {str(e)}")
        raise
