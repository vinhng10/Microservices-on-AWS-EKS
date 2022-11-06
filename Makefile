CLUSTER := cluster

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

	# Create AWSLoadBalancerControllerIAMPolicy:
	curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.4.4/docs/install/iam_policy.json
	aws iam create-policy \
		--policy-name AWSLoadBalancerControllerIAMPolicy \
		--policy-document file://iam_policy.json
	rm iam_policy.json

install-load-balancer-controller:
	# Get the ARN of AWSLoadBalancerControllerIAMPolicy:
	$(eval LBC_ARN = $(shell aws iam list-policies \
		--query 'Policies[?PolicyName==`AWSLoadBalancerControllerIAMPolicy`].Arn' \
		--output text))
	
	# Create IAM OIDC identity provider for the cluster:
	eksctl utils associate-iam-oidc-provider --cluster $(CLUSTER) --approve
	
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

delete-cluster:
	eksctl delete cluster -f cluster.yaml
	$(eval LBC_ARN = $(shell aws iam list-policies \
		--query 'Policies[?PolicyName==`AWSLoadBalancerControllerIAMPolicy`].Arn' \
		--output text))
	aws iam delete-policy --policy-arn $(LBC_ARN)

all: install lint test