IMAGE_NAME = chats:latest
DOCKER_REGISTRY = radisbyio
TARGET_PLATFORM = linux/amd64

.PHONY: build push

build:
	docker build --platform $(TARGET_PLATFORM) -t $(DOCKER_REGISTRY)/$(IMAGE_NAME) .

push:
	docker push $(DOCKER_REGISTRY)/$(IMAGE_NAME)

run:
	docker run -p 8080:8080 --env-file .env  $(DOCKER_REGISTRY)/$(IMAGE_NAME)

all: build push

