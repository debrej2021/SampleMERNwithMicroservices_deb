import boto3

# Initialize AWS Clients
ec2_client = boto3.client('ec2', region_name='us-west-2')
elb_client = boto3.client('elbv2', region_name='us-west-2')
autoscaling_client = boto3.client('autoscaling', region_name='us-west-2')

# Config Variables
VPC_ID = 'vpc-0321f38a7b594180d'  # Replace with your VPC ID
SUBNET_IDS = ['subnet-03ca36de9a927fe8e']  # Replace with your subnet IDs
SECURITY_GROUP = 'sg-07fc5b1e87a92419b'  # Replace with Security Group ID
ASG_NAME = 'backend-asg'  # Auto Scaling Group name

def create_load_balancer():
    print("Creating Application Load Balancer...")
    response = elb_client.create_load_balancer(
        Name='backend-load-balancer',
        Subnets=SUBNET_IDS,
        SecurityGroups=[SECURITY_GROUP],
        Scheme='internet-facing',
        Type='application',
        IpAddressType='ipv4'
    )
    lb_arn = response['LoadBalancers'][0]['LoadBalancerArn']
    print(f"Load Balancer Created with ARN: {lb_arn}")
    return lb_arn

def create_target_group():
    print("Creating Target Group...")
    response = elb_client.create_target_group(
        Name='backend-target-group',
        Protocol='HTTP',
        Port=80,
        VpcId=VPC_ID,
        TargetType='instance',
        HealthCheckProtocol='HTTP',
        HealthCheckPath='/',
        HealthCheckPort='80',
        HealthCheckIntervalSeconds=30,
        HealthCheckTimeoutSeconds=5,
        HealthyThresholdCount=3,
        UnhealthyThresholdCount=2
    )
    target_group_arn = response['TargetGroups'][0]['TargetGroupArn']
    print(f"Target Group Created with ARN: {target_group_arn}")
    return target_group_arn

def register_asg_with_target_group(target_group_arn):
    print("Attaching ASG to Target Group...")
    autoscaling_client.attach_load_balancer_target_groups(
        AutoScalingGroupName=ASG_NAME,
        TargetGroupARNs=[target_group_arn]
    )
    print("ASG attached to Target Group.")

def create_listener(lb_arn, target_group_arn):
    print("Creating Listener...")
    elb_client.create_listener(
        LoadBalancerArn=lb_arn,
        Protocol='HTTP',
        Port=80,
        DefaultActions=[{
            'Type': 'forward',
            'TargetGroupArn': target_group_arn
        }]
    )
    print("Listener Created.")

def main():
    lb_arn = create_load_balancer()
    target_group_arn = create_target_group()
    register_asg_with_target_group(target_group_arn)
    create_listener(lb_arn, target_group_arn)

if __name__ == '__main__':
    main()
