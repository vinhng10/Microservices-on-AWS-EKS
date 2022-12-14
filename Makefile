CLUSTER := cluster
SHELL := /bin/bash
PYTHON := .venv/bin/python3

prepare-venv: .venv/bin/activate

setup:
	# Create python virtualenv & source it
	# python3 -m venv .venv
	$(shell source .venv/bin/activate)

install:
	# This should be run from inside a virtualenv
	pip3 install --upgrade pip && pip3 install -r requirements.txt

run-local-dev:
	uvicorn app/main:app --reload

run-docker-dev:
	docker build . -t vinhng10/dot-classification
	docker run --rm -p 80:80 --name dot-classification vinhng10/dot-classification

test:
	# Additional, optional, tests could go here
	# python -m pytest -vv --cov=myrepolib tests/*.py
	# python -m pytest --nbval notebook.ipynb

lint:
	# See local hadolint install instructions:   https://github.com/hadolint/hadolint
	# This is linter for Dockerfiles
	hadolint Dockerfile
	# This is a linter for Python source code linter: https://www.pylint.org/
	# This should be run from inside a virtualenv
	pylint --disable=R,C,W1203,W1202 app.py

configure:
	aws configure

create-cluster:
	# Create cluster using the config file:
	eksctl create cluster -f cluster.yaml
	
	# Persist kubeconfig information for kubectl to communicate with API server:
	aws eks update-kubeconfig --region us-west-2 --name $(CLUSTER)

create-iam-policies:
	# Create AWSLoadBalancerControllerIAMPolicy:
	curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.4.4/docs/install/iam_policy.json
	aws iam create-policy \
		--policy-name AWSLoadBalancerControllerIAMPolicy \
		--policy-document file://iam_policy.json
	rm iam_policy.json

	# Create AWSDynamoDBFullAccessPolicy:
	aws iam create-policy \
		--policy-name AWSDynamoDBFullAccessPolicy \
		--policy-document file://policies/dynamodb.json

create-dynamodb-serviceaccount:
	# Get the ARN of AWSDynamoDBFullAccessPolicy:
	$(eval DB_ARN = $(shell aws iam list-policies \
		--query 'Policies[?PolicyName==`AWSDynamoDBFullAccessPolicy`].Arn' \
		--output text))
	
	# Create IAM role - K8s service account for the AWS Load Balancer Controller 
	eksctl create iamserviceaccount \
		--cluster=$(CLUSTER) \
		--name=aws-dynamodb-full-access \
		--attach-policy-arn=$(DB_ARN) \
		--approve

install-load-balancer-controller:
	# Get the ARN of AWSLoadBalancerControllerIAMPolicy:
	$(eval LBC_ARN = $(shell aws iam list-policies \
		--query 'Policies[?PolicyName==`AWSLoadBalancerControllerIAMPolicy`].Arn' \
		--output text))
	
	# Create IAM role - K8s service account for the AWS Load Balancer Controller 
	eksctl create iamserviceaccount \
		--cluster=$(CLUSTER) \
		--namespace=kube-system \
		--name=aws-load-balancer-controller \
		--role-name "AmazonEKSLoadBalancerControllerRole" \
		--attach-policy-arn=$(LBC_ARN) \
		--approve

	# Install AWS Load Balancer Controller:
	helm repo add eks https://aws.github.io/eks-charts
	helm repo update
	helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
		-n kube-system \
		--set clusterName=$(CLUSTER) \
		--set serviceAccount.create=false \
		--set serviceAccount.name=aws-load-balancer-controller \
		--set image.repository=602401143452.dkr.ecr.us-west-2.amazonaws.com/amazon/aws-load-balancer-controller 

deploy:
	# Create deployment:
	kubectl apply -f manifests/deploys.yaml

	# AWS Load Balancer will automatically create Listeners and Target Groups:
	kubectl apply -f manifests/services.yaml

	# AWS Ingress a.k.a AWS Application Load Balancer:
	kubectl apply -f manifests/ingress.yaml

performance-testing:
	# Create key pair to access EC2:
	aws ec2 create-key-pair \
		--key-name PerfTestKeyPair \
		--query "KeyMaterial" \
		--output text > performance/PerfTestKeyPair.pem
	chmod 400 performance/PerfTestKeyPair.pem

	# Spin up an EC2 instance. At the moment, the instance will be in public 
	# subnet to access the WebUI. Private subnet style will be develop later:
	$(eval SECURITY_GROUP_ID = \
		$(shell aws ec2 describe-security-groups \
			--filter Name=group-name,Values=default \
			--query 'SecurityGroups[*].[GroupId]' \
			--output text ))
	$(eval PUBLIC_SUBNET_ID = \
		$(shell aws ec2 describe-subnets \
			--filter Name=tag:Name,Values=eksctl-cluster-$(CLUSTER)/SubnetPublicUSWEST2A \
			--query 'Subnets[*].[SubnetId]' \
			--output text ))
	aws ec2 run-instances \
		--image-id ami-0ceecbb0f30a902a6\
		--count 1 --instance-type t2.micro --key-name PerfTestKeyPair \
		--security-group-ids $(SECURITY_GROUP_ID) \
		--subnet-id $(PUBLIC_SUBNET_ID)

	# # Install tests in that EC2 instance:
	# aws ec2 ...

	# # Run tests:
	# ssh ...
	# pip3 install -r requirements.txt
	# locust -f performance/stress_tests.py
	# locust -f performance/spike_tests.py
	# locust -f performance/load_tests.py
	# locust -f performance/soak_tests.py
	

init-database:
	# Activate virtual environment (still doesn't work):
	$(SHELL) -c "source .venv/bin/activate"

	# Create DynamoDB table if not exist:
	${PYTHON} data/data.py

delete-cluster:
	eksctl delete cluster -f cluster.yaml
	$(eval LBC_ARN = $(shell aws iam list-policies \
		--query 'Policies[?PolicyName==`AWSLoadBalancerControllerIAMPolicy`].Arn' \
		--output text))
	aws iam delete-policy --policy-arn $(LBC_ARN)

all: install lint test