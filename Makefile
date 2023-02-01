ifneq (,$(wildcard ./.env))
    include .env
    export
endif

build:
    docker buildx build --platform linux/amd64,linux/arm64/v8 -t $(IMAGE_NAME) . -f Dockerfile.Prod --no-cache
    docker buildx build --load --platform linux/arm64/v8 -t $(IMAGE_NAME)  . -f Dockerfile.Prod
login:
	aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.ap-southeast-2.amazonaws.com
push:
	docker tag $(IMAGE_ID) $(ACCOUNT_ID).dkr.ecr.ap-southeast-2.amazonaws.com/$(REPO_NAME)
	docker push $(ACCOUNT_ID).dkr.ecr.ap-southeast-2.amazonaws.com/$(REPO_NAME)

sshcluster:
	aws ecs execute-command --cluster $(CLUSTER_NAME) \
    --task $(TASK_ID) \
    --container $(CONTAINER_NAME) \
    --interactive \
    --command "bash"

exec:
	aws ecs update-service --cluster $(CLUSTER_NAME) \
    --service $(SERVICE_NAME) \
    --enable-execute-command \
    --force-new-deployment \
    --region ap-southeast-2 \
    --profile work