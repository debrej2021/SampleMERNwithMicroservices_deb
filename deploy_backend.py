import boto3

# Initialize Clients
ec2_client = boto3.client('ec2', region_name='us-west-2')
autoscaling_client = boto3.client('autoscaling', region_name='us-west-2')

# Configuration Variables
ECR_URL = "975050024946.dkr.ecr.us-west-2.amazonaws.com"
IMAGE_NAME = "backend_deb_scaling:latest"
AMI_ID = "ami-05d38da78ce859165"  # Replace with your AMI ID
KEY_NAME = "Deb_scaling_deploying"  # Replace with your key pair name
SECURITY_GROUP = "sg-07fc5b1e87a92419b"  # Replace with the SG ID
INSTANCE_TYPE = "t2.micro"
ASG_NAME = "backend-asg"

def create_launch_template():
    print("Creating Launch Template...")
    user_data_script = f"""#!/bin/bash
    sudo apt-get update -y
    sudo apt-get install -y docker.io awscli
    sudo systemctl start docker
    sudo systemctl enable docker
    aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin {ECR_URL}
    docker pull {ECR_URL}/{IMAGE_NAME}
    docker run -d -p 80:80 {ECR_URL}/{IMAGE_NAME}
    """

    response = ec2_client.create_launch_template(
        LaunchTemplateName="backend-launch-template",
        LaunchTemplateData={
            'ImageId': AMI_ID,
            'InstanceType': INSTANCE_TYPE,
            'KeyName': KEY_NAME,
            'UserData': user_data_script.encode('utf-8').decode('ascii'),
            'SecurityGroupIds': [SECURITY_GROUP],
            'TagSpecifications': [
                {
                    'ResourceType': 'instance',
                    'Tags': [{'Key': 'Name', 'Value': 'Backend-Instance'}]
                }
            ]
        }
    )
    template_id = response['LaunchTemplate']['LaunchTemplateId']
    print(f"Launch Template Created: {template_id}")
    return template_id

def create_auto_scaling_group(template_id):
    print("Creating Auto Scaling Group...")
    autoscaling_client.create_auto_scaling_group(
        AutoScalingGroupName=ASG_NAME,
        LaunchTemplate={
            'LaunchTemplateId': template_id,
            'Version': '$Latest'
        },
        MinSize=2,
        MaxSize=5,
        DesiredCapacity=2,
        VPCZoneIdentifier='subnet-03ca36de9a927fe8e',  # Replace with your subnet IDs
        Tags=[
            {'Key': 'Name', 'Value': 'Backend-ASG'}
        ]
    )
    print(f"Auto Scaling Group '{ASG_NAME}' Created.")

def main():
    template_id = create_launch_template()
    create_auto_scaling_group(template_id)

if __name__ == '__main__':
    main()
