import boto3

# Initialize AWS Route53 Client
route53_client = boto3.client('route53', region_name='us-west-2')

# Config Variables
HOSTED_ZONE_ID = 'Z1234567890ABCDE'  # Replace with your Hosted Zone ID
LOAD_BALANCER_DNS = 'backend-load-balancer-123456789.us-west-2.elb.amazonaws.com'  # Replace with ALB DNS name
DOMAIN_NAME = 'backend.example.com'

def create_dns_record():
    print("Creating Route 53 DNS Record...")
    response = route53_client.change_resource_record_sets(
        HostedZoneId=HOSTED_ZONE_ID,
        ChangeBatch={
            'Changes': [{
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': DOMAIN_NAME,
                    'Type': 'A',
                    'AliasTarget': {
                        'HostedZoneId': 'Z3AADJGX6KTTL2',  # ELB Hosted Zone ID for us-west-2
                        'DNSName': LOAD_BALANCER_DNS,
                        'EvaluateTargetHealth': False
                    }
                }
            }]
        }
    )
    print(f"Route 53 Record Created: {DOMAIN_NAME}")

def main():
    create_dns_record()

if __name__ == '__main__':
    main()
