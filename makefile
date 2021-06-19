APP_NAME=sannin
PORT=5000

build:
	docker build -t $(APP_NAME) .

run:
	docker run -it --rm -p=$(PORT):$(PORT) --name="$(APP_NAME)" $(APP_NAME) flask run -p $(PORT) -h 0.0.0.0

up: build run

stop:
	docker stop $(APP_NAME); docker rm $(APP_NAME)