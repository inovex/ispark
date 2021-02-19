#!/usr/bin bash
export -f conda
export -f __conda_activate
export -f __conda_reactivate
export -f __conda_hashr

#check for conda
conda >/dev/null 2>&1 || { echo >&2 "I require 'conda' but it's not installed. Exiting..."; exit; }

#create conda env for flask and JEG and install needed components (flask should be compiled against python3, otherwiese pyyaml problematic)

ENVS=$(conda env list | awk '{print $1}' )
if [[ $ENVS = *"jeg_flask"* ]]; then
	echo "Conda env jeg_flask already installed. Activating..."	
	conda activate jeg_flask
else 
	echo "Conda env jeg_flask not installed. Installing..."
	conda create --name jeg_flask python=3.7 --yes
	conda activate jeg_flask
	conda activate jeg_flask
	conda install -c conda-forge jupyter_enterprise_gateway --yes
	conda install -c conda-forge ruamel.yaml --yes
	sudo apt update
	sudo apt install python3-pip
	pip3 install flask 
	pip3 install pyyaml
fi;


#create folders for remote kernels
sudo mkdir -p /usr/local/share/jupyter

#makde kernel folder accessible
sudo chmod -R 777 /usr/local/share/jupyter

#copy default kernels
cp -r default_kernels/kernels /usr/local/share/jupyter

#create env variable for kernels path
export KERNELS_FOLDER=/usr/local/share/jupyter/kernels

#create env variable for web_ui adress
export WEB_UI_ADRESS=$1


#start api_server


 
FLASK_APP=api-server/app/routes.py flask run --host=0.0.0.0 --with-threads

jupyter enterprisegateway --ip=0.0.0.0 --port_retries=0 








