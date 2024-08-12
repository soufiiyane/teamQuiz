import json
import boto3
import os

rds_data_client = boto3.client('rds-data')
sns_client = boto3.client('sns')

sns_topic_arn = os.environ['SNS_TOPIC_ARN']
cluster_arn = os.environ['CLUSTER_ARN']
secret_arn = os.environ['SECRET_ARN']
database_name = os.environ['DB_NAME']


def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        quiz_id = body.get('quizId')
        user_id = body.get('userId')
        responses = body.get('responses', [])
        message = {'message': 'Hello from Lambda'}
        sns_client.publish(
            TopicArn=sns_client,
            Message=json.dumps(message)
        )
        if quiz_id is None:
            return {
                'statusCode': 400,
                'body': json.dumps('Quiz ID is required.')
            }
        if user_id is None:
            return {
                'statusCode': 400,
                'body': json.dumps('User ID is required.')
            }
        if not responses:
            return {
                'statusCode': 400,
                'body': json.dumps('Responses are required.')
            }

        quiz_details = get_quiz_details(quiz_id)
        if not quiz_details:
            return {
                'statusCode': 404,
                'body': json.dumps('Quiz not found.')
            }

        questions = get_questions_by_ids(quiz_details['questionIds'])
        if not questions:
            return {
                'statusCode': 404,
                'body': json.dumps('Questions not found.')
            }

        results, correct_count, total_questions = check_answers(responses, questions)

        passing_percentage = 0.70
        score_percentage = (correct_count / total_questions) * 100
        passed = score_percentage >= passing_percentage * 100

        store_quiz_history(user_id, quiz_id, score_percentage, 'Pass' if passed else 'Fail', correct_count,
                           total_questions, total_questions - correct_count, results)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Answers checked successfully!',
                'results': results,
                'scorePercentage': score_percentage,
                'totalQuestions': total_questions,
                'correctAnswers': correct_count,
                'notAnsweredOrFalse': total_questions - correct_count,
                'status': 'Pass' if passed else 'Fail'
            })
        }
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps('Internal server error.')
        }


def get_quiz_details(quiz_id):
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="SELECT questionIds FROM Quiz WHERE id = :quizId",
            parameters=[
                {'name': 'quizId', 'value': {'longValue': quiz_id}}
            ]
        )
        records = response['records']
        if not records:
            return None
        question_ids = json.loads(records[0][0]['stringValue'])
        return {'questionIds': question_ids}
    except Exception as e:
        print(f"Error retrieving quiz details: {str(e)}")
        raise


def get_questions_by_ids(question_ids):
    try:
        ids_placeholder = ','.join([f':id{i}' for i in range(len(question_ids))])
        query = f"SELECT id, text, answer FROM Questions WHERE id IN ({ids_placeholder})"

        parameters = [{'name': f'id{i}', 'value': {'longValue': q_id}} for i, q_id in enumerate(question_ids)]

        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql=query,
            parameters=parameters
        )

        questions = [
            {
                'id': record[0]['longValue'],
                'text': record[1]['stringValue'],
                'answer': json.loads(record[2]['stringValue'])
            }
            for record in response['records']
        ]

        return questions
    except Exception as e:
        print(f"Error retrieving questions: {str(e)}")
        raise


def check_answers(responses, questions):
    question_map = {q['id']: q['answer'] for q in questions}
    results = []
    correct_count = 0
    total_questions = len(question_map)
    answered_questions = set()

    for response in responses:
        question_id = response['questionId']
        user_answer = response['answer']
        correct_answer = question_map.get(question_id)

        if question_id in answered_questions:
            continue

        if correct_answer is None:
            result = {'questionId': question_id, 'correct': False, 'message': 'Question not found.'}
        else:
            is_correct = user_answer == correct_answer
            if is_correct:
                correct_count += 1
            result = {'questionId': question_id, 'correct': is_correct,
                      'message': 'Correct' if is_correct else 'Incorrect'}

        results.append(result)
        answered_questions.add(question_id)

    return results, correct_count, total_questions


def store_quiz_history(user_id, quiz_id, score_percentage, status, correct_answers, total_questions,
                       not_answered_or_false, results):
    try:
        response = rds_data_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="INSERT INTO QuizHistory (userId, quizId, score, status, correctAnswers, totalQuestions, scorePercentage, notAnsweredOrFalse, results) VALUES (:userId, :quizId, :score, :status, :correctAnswers, :totalQuestions, :scorePercentage, :notAnsweredOrFalse, :results)",
            parameters=[
                {'name': 'userId', 'value': {'longValue': user_id}},
                {'name': 'quizId', 'value': {'longValue': quiz_id}},
                {'name': 'score', 'value': {'doubleValue': score_percentage}},
                {'name': 'status', 'value': {'stringValue': status}},
                {'name': 'correctAnswers', 'value': {'longValue': correct_answers}},
                {'name': 'totalQuestions', 'value': {'longValue': total_questions}},
                {'name': 'scorePercentage', 'value': {'doubleValue': score_percentage}},
                {'name': 'notAnsweredOrFalse', 'value': {'longValue': not_answered_or_false}},
                {'name': 'results', 'value': {'stringValue': json.dumps(results)}}
            ]
        )
        print("Quiz history stored successfully.")
    except Exception as e:
        print(f"Error storing quiz history: {str(e)}")
        raise
