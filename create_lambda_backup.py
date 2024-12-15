import os
import boto3
import zipfile
from datetime import datetime

# Initialize Boto3 Clients
lambda_client = boto3.client('lambda', region_name='us-west-2')
s3_client = boto3.client('s3', region_name='us-west-2')
iam_client = boto3.client('iam', region_name='us-west-2')

# Config Variables
LAMBDA_FUNCTION_NAME = "DBBackupFunction"
S3_BUCKET_NAME = "db-backup-bucket"
LAMBDA_ROLE_NAME = "LambdaExecutionRole"
DB_NAME = "mydatabase"  # Replace with your DB name
BACKUP_SCRIPT = """
import boto3
import datetime

def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    backup_file_name = f"db-backup-{timestamp}.sql"

    # Simulating DB backup (replace this logic with real DB dump logic)
    backup_content = "Database backup content"

    # Upload the backup to S3
    s3_client.put_object(
        Bucket="{bucket_name}",
        Key=backup_file_name,
        Body=backup_content
    )

    return {
        'statusCode': 200,
        'body': f"Backup successful: {backup_file_name}"
    }
""".replace("{bucket_name}", S3_BUCKET_NAME)

def create_lambda_zip():
    print("Creating Lambda Deployment Package...")
    os.makedirs("lambda_package", exist_ok=True)
    with open("lambda_package/lambda_function.py", "w") as f:
        f.write(BACKUP_SCRIPT)
    with zipfile.ZipFile("lambda_function.zip", "w") as z:
        z.write("lambda_package/lambda_function.py", arcname="lambda_function.py")
    print("Lambda Deployment Package Created: lambda_function.zip")

def create_lambda_role():
    print("Creating IAM Role for Lambda...")
    assume_role_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }
    role = iam_client.create_role(
        RoleName=LAMBDA_ROLE_NAME,
        AssumeRolePolicyDocument=json.dumps(assume_role_policy)
    )
    print("IAM Role Created.")
    return role['Role']['Arn']

def create_lambda_function(role_arn):
    print("Creating Lambda Function...")
    with open("lambda_function.zip", "rb") as f:
        zip_content = f.read()
    lambda_client.create_function(
        FunctionName=LAMBDA_FUNCTION_NAME,
        Runtime="python3.9",
        Role=role_arn,
        Handler="lambda_function.lambda_handler",
        Code={"ZipFile": zip_content},
        Timeout=120
    )
    print(f"Lambda Function '{LAMBDA_FUNCTION_NAME}' Created.")

def main():
    create_lambda_zip()
    role_arn = create_lambda_role()
    create_lambda_function(role_arn)
    print("AWS Lambda Function Deployed Successfully.")

if __name__ == '__main__':
    main()
