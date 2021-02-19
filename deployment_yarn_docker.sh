#!/usr/bin bash

#check for docker & docker-compose
docker >/dev/null 2>&1 || { echo >&2 "'docker' required but it's not installed. Exiting..."; exit; }
#docker-compose >/dev/null 2>&1 || { echo >&2  "'docker-compose' required but it's not installed. Exiting..."; exit; }


#create folders for remote kernels
sudo mkdir -p /usr/local/share/jupyter

#makde kernel folder accessible
sudo chmod -R 777 /usr/local/share/jupyter

#copy default kernels
cp -r yarn/default_kernels/kernels /usr/local/share/jupyter

#docker log-in
docker login -u <YOUR-USER-NAME> -p <YOUR-PASSWORD> <YOUR-REGISTRY>

#pull EG and API images
docker pull <YOUR-REGISTRY-JEG:TAG>
docker pull <YOUR-REGISTRY-API-SERVER:TAG>

#run docker-compose (starting both containers)
docker-compose up











