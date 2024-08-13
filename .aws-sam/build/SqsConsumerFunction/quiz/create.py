import json
import boto3
import os
import random

rds_data_client = boto3.client('rds-data')

cluster_arn = os.environ['CLUSTER_ARN']
secret_arn = os.environ['SECRET_ARN']
database_name = os.environ['DB_NAME']


def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        profile_id = body.get('profileId')
        number_questions = body.get('numberQuestions')
        timer = body.get('timer')
        user_id = body.get('userId')
        job_id = body.get('jobId')

        if profile_id is None:
            return {
                'statusCode': 400,
                'body': json.dumps('Profile ID is required.')
            }
        if number_questions is None:
            return {
                'statusCode': 400,
                'body': json.dumps('Number of questions is required.')
            }
        if timer is None:
            return {
                'statusCode': 400,
                'body': json.dumps('Timer must be either 20 or 30 minutes.')
            }
        if user_id is None:
            return {
                'statusCode': 400,
                'body': json.dumps('User ID is required.')
            }
        if job_id is None:
            return {
                'statusCode': 400,
                'body': json.dumps('Job ID is required.')
            }

        questions = get_random_question_details(profile_id, number_questions)
        if not questions:
            return {
                'statusCode': 404,
                'body': json.dumps('Not enough questions found for the specified profile.')
            }

        question_ids = [q['id'] for q in questions]
        quiz_id = create_quiz(profile_id, job_id, question_ids, user_id, timer, number_questions)

        quiz_details = {
            'quizId': quiz_id,
            'profileId': profile_id,
            'jobId': job_id,
            'questions': questions,
            'userId': user_id,
            'timer': timer,
            'numberQuestions': number_questions
        }

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Quiz created successfully!', 'quizDetails': quiz_details})
        }
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps('Internal server error.')
        }


def get_random_question_details(profile_id, number_questions):
    try:
        query = """
        SELECT id, text, type, options, answer 
        FROM Questions 
        WHERE profileId = :profileId 
        ORDER BY RAND() 
        LIMIT :limit
        """

        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql=query,
            parameters=[
                {'name': 'profileId', 'value': {'longValue': profile_id}},
                {'name': 'limit', 'value': {'longValue': number_questions}}
            ]
        )

        all_questions = [
            {
                'id': record[0]['longValue'],
                'text': record[1]['stringValue'],
                'type': record[2]['stringValue'],
                'options': json.loads(record[3]['stringValue']),
                'answer': json.loads(record[4]['stringValue'])
            }
            for record in response['records']
        ]

        return all_questions if len(all_questions) == number_questions else None

    except Exception as e:
        print(f"Error retrieving questions: {str(e)}")
        raise


def create_quiz(profile_id, job_id, question_ids, user_id, timer, number_questions):
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="INSERT INTO Quiz (profileId, jobId, questionIds, userId, timer, numberQuestions) VALUES (:profileId, :jobId, :questionIds, :userId, :timer, :numberQuestions);",
            parameters=[
                {'name': 'profileId', 'value': {'longValue': profile_id}},
                {'name': 'jobId', 'value': {'longValue': job_id}},
                {'name': 'questionIds', 'value': {'stringValue': json.dumps(question_ids)}},
                {'name': 'userId', 'value': {'longValue': user_id}},
                {'name': 'timer', 'value': {'longValue': timer}},
                {'name': 'numberQuestions', 'value': {'longValue': number_questions}}
            ]
        )
        return response['generatedFields'][0]['longValue']
    except Exception as e:
        print(f"Error creating quiz: {str(e)}")
        raise
