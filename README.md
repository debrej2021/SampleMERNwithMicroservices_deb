# Sample MERN with Microservices

I created only 1 EC2 instance ( it has been deleted now but I have shared some screen shots Jenkins_setup_EC2.png , EC2_jenkins.png) to prove . Instance iD is i-022cb241646b9dc6b - Deb_scaling_deploying



I was able to install Jenkins through docker in the Ubuntu EC2 , For some reason I did not have access to code Commit to create repo , I created 2 Private ECR repos ( ECR_Repos_CReated.png)

I also installed AWS CLI and configured it in Jenkins and ontainer 

I was also able to set up a webhook in github which would trigger a build when ever there is a commit 

Jenkins URL - http://EC2IP:8080

I also installed docker deamon inside the jenkins container and allow all sockets access ( this was because individual user acccess was creating problem)

I was able to build the code , build the docker image and push it into ECR ( I have also INcluded a successful_build.txt file to show the build )

The boto3 files I have created but not executed as it would have incurred cost and the EC2s are getting terminated 
Following are the boto3 python code files which can be used - 
1.deploy_backend.py
2.Infrastructure.py
3.deploy_frontend.py
4.create_lambda_backup.py
5.configure_route53.py

I have also included the groovy code in the JenkinsFile

I have also created the helm folder structure and the files required 

Architecture.docx and architecture.drawio contains the rough architecture followed , if we were to create 2 EC2s


aws codecommit create-repository --repository-name mern-deb-scaling --region us-west-2
gives error as permission denied

The below commands includes setting up cloudwatch alarms , EKS Clusters , Logging , I have not executed it but have mentioned the commands 
Command to create a Log Group- 
aws logs create-log-group --log-group-name /eks/mern-app

check cloudwatch logs- 
aws logs describe-log-streams --log-group-name /eks/mern-app

CReate CloudWatch Alarms- 

aws cloudwatch put-metric-alarm \
  --alarm-name High-CPU-Utilization \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 75 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=InstanceId,Value=i-1234567890abcdef \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:us-west-2:123456789012:notify-me

  Install CloudWatch Agent on worker nodes - 
  sudo yum install amazon-cloudwatch-agent -y
sudo systemctl start amazon-cloudwatch-agent


command to deploy helm chart - 
helm install mern-release ./mern-app

Verify Deploments - 
kubectl get deployments
kubectl get pods
kubectl get services

CReate EKS cluster - 
eksctl create cluster \
  --name mern-cluster \
  --region us-west-2 \
  --nodegroup-name mern-nodegroup \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 3 \
  --managed
install EKS - 
curl -sL https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_Linux_amd64.tar.gz | tar xz -C /usr/local/bin
eksctl version


Check EKS Cluster - 
aws eks --region us-west-2 describe-cluster --name mern-cluster

Verify kubectl access to nodes 
kubectl get nodes

