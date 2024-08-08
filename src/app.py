def lambda_handler(event, context):
    print("i got triggered !")
    print(event)
    return event
