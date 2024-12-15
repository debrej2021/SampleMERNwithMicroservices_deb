import boto3

# Initialize AWS Clients
ec2_client = boto3.client('ec2', region_name='us-west-2')
autoscaling_client = boto3.client('autoscaling', region_name='us-west-2')
lambda_client = boto3.client('lambda', region_name='us-west-2')

def create_vpc():
    print("Creating VPC...")
    response = ec2_client.create_vpc(CidrBlock='10.0.0.0/16')
    vpc_id = response['Vpc']['VpcId']
    print(f"VPC Created with ID: {vpc_id}")
    return vpc_id

def create_subnets(vpc_id):
    print("Creating Subnets...")
    subnet_ids = []
    availability_zones = ['us-west-2a', 'us-west-2b']
    for i, az in enumerate(availability_zones):
        subnet = ec2_client.create_subnet(
            VpcId=vpc_id,
            CidrBlock=f'10.0.{i}.0/24',
            AvailabilityZone=az
        )
        subnet_ids.append(subnet['Subnet']['SubnetId'])
        print(f"Subnet Created in {az} with ID: {subnet['Subnet']['SubnetId']}")
    return subnet_ids

def create_security_group(vpc_id):
    print("Creating Security Group...")
    response = ec2_client.create_security_group(
        GroupName='backend-sg',
        Description='Allow HTTP and SSH',
        VpcId=vpc_id
    )
    sg_id = response['GroupId']
    print(f"Security Group Created with ID: {sg_id}")

    # Add inbound rules
    ec2_client.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
        ]
    )
    print("Inbound rules added.")
    return sg_id

def create_auto_scaling_group(subnet_ids, sg_id):
    print("Creating Auto Scaling Group...")
    launch_config_name = 'backend-launch-config'

    # Create Launch Configuration
    autoscaling_client.create_launch_configuration(
        LaunchConfigurationName=launch_config_name,
        ImageId='ami-05d38da78ce859165',  # Replace with your AMI ID
        InstanceType='t2.micro',
        SecurityGroups=[sg_id],
        KeyName='Deb_scaling_deploying',  # Replace with your key-pair name
    )

    # Create Auto Scaling Group
    autoscaling_client.create_auto_scaling_group(
        AutoScalingGroupName='backend-asg',
        LaunchConfigurationName=launch_config_name,
        MinSize=2,
        MaxSize=5,
        DesiredCapacity=2,
        VPCZoneIdentifier=",".join(subnet_ids),
        Tags=[{'Key': 'Name', 'Value': 'Backend-ASG'}]
    )
    print("Auto Scaling Group Created.")

def create_lambda_function():
    print("Creating AWS Lambda Function...")
    with open('lambda_function.zip', 'rb') as f:
        lambda_code = f.read()
    
    response = lambda_client.create_function(
        FunctionName='MyLambdaFunction',
        Runtime='python3.9',
        Role='arn:aws:iam::975050024946:role/lambda-execution-role',  # Replace with your IAM role ARN
        Handler='lambda_function.lambda_handler',
        Code={'ZipFile': lambda_code},
        Description='A sample Lambda function',
        Timeout=30,
        MemorySize=128
    )
    print(f"Lambda Function Created: {response['FunctionName']}")

def main():
    vpc_id = create_vpc()
    subnet_ids = create_subnets(vpc_id)
    sg_id = create_security_group(vpc_id)
    create_auto_scaling_group(subnet_ids, sg_id)
    # Uncomment the following line if you have a Lambda function
    # create_lambda_function()

if __name__ == '__main__':
    main()
