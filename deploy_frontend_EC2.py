import boto3

# Initialize Boto3 Clients
ec2_client = boto3.client('ec2', region_name='us-west-2')

# Configuration Variables
AMI_ID = "ami-12345678"  # Replace with your AMI ID
KEY_NAME = "my-key-pair"  # Replace with your key pair
SECURITY_GROUP = "frontend-sg"  # Replace with security group allowing HTTP
INSTANCE_TYPE = "t2.micro"
ECR_URL = "975050024946.dkr.ecr.us-west-2.amazonaws.com"
IMAGE_NAME = "frontend_deb_scaling:latest"
SUBNET_ID = "subnet-abc12345"  # Replace with your subnet ID

def launch_frontend_instances():
    print("Launching Frontend EC2 Instances...")
    user_data_script = f"""#!/bin/bash
    sudo apt-get update -y
    sudo apt-get install -y docker.io awscli
    sudo systemctl start docker
    sudo systemctl enable docker
    aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin {ECR_URL}
    docker pull {ECR_URL}/{IMAGE_NAME}
    docker run -d -p 80:80 {ECR_URL}/{IMAGE_NAME}
    """
    response = ec2_client.run_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        MinCount=1,
        MaxCount=2,
        SecurityGroupIds=[SECURITY_GROUP],
        SubnetId=SUBNET_ID,
        UserData=user_data_script,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': 'Frontend-Instance'}]
            }
        ]
    )
    print("Frontend EC2 Instances Launched Successfully.")
    for instance in response['Instances']:
        print(f"Instance ID: {instance['InstanceId']}")

if __name__ == '__main__':
    launch_frontend_instances()
