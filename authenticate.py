import boto3

def authenticate_and_get_token(username: str, password: str, 
                               app_client_id: str) -> None:
    client = boto3.client('cognito-idp', region_name='us-east-1')

    resp = client.initiate_auth(
        ClientId=app_client_id,
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            "USERNAME": username,
            "PASSWORD": password
        }
    )

    print("Log in success")
    return resp['AuthenticationResult']['AccessToken']