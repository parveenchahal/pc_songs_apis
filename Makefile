docker-build:
	if [ -d './build' ]; then rm build -r; fi
	mkdir build
	cp src/* build/ -r
	cp ./Dockerfile build/
	cp ./startup.sh build/
	cp ./python-dependencies.txt build/
	find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf
	sudo docker build ./build -t ${IMG}

docker-push:
	sudo docker push ${IMG}