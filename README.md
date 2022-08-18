## Docker

```
docker build -t <image-name> .

<!-- If you're building this image from Mac with M1 chip -->
docker buildx build --platform=linux/amd64 -t <image-name> . -f Dockerfile

docker run --rm -it <image-name> bash

docker-compose up
docker exec -it <container-name> /bin/sh

<!-- To get what command the docker image ran -->
docker inspect --format='{{.Config.Cmd}}' <image-tag>
```

## AWS ECR
```
aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.ap-southeast-2.amazonaws.com

docker tag <IMAGE_ID> <ACCOUNT_ID>.dkr.ecr.ap-southeast-2.amazonaws.com/php

docker push <ACCOUNT_ID>.dkr.ecr.ap-southeast-2.amazonaws.com/php
```

## CDK
```
cdk init app --language python
pip install -r requirements.txt
python3 -m venv .venv
source .venv/bin/activate
cdk synth
cdk bootstrap
cdk deploy
<!-- If you have more than one stack -->
ckd deploy --all
<!-- To debug if your CloudFormation fails -->
cdk deploy --all --no-rollback
<-- To only deploy the function not CloudFormation template -->
cdk deploy --hotswap 
cdk watch
```
