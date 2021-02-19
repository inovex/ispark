#!/usr/bin bash
EG_ENDPOINT=$1

K8S_or_K8SYARN='yarn'
EG_PORT=':8888'
API_PORT=':5000'
HTTP_FOR_ADRESS='http://'
K8S_or_K8SYARN='yarn'
FULL_EG_ADRESS=$HTTP_FOR_ADRESS$EG_ENDPOINT$EG_PORT
FULL_API_ADRESS=$HTTP_FOR_ADRESS$EG_ENDPOINT$API_PORT

echo $K8S_or_K8SYARN
if [[ $K8S_or_K8SYARN != "kubernetes"  &&  $K8S_or_K8SYARN != "yarn" ]] ; then
	echo "Please provide the IP adress of YARN's edge node"
	exit
fi

if [ "$K8S_or_K8SYARN" = "yarn" ] ; then
	if [ "$EG_ENDPOINT" = "" ] ; then
		echo "Please provide the IP from the instance, where Jupyter EG is runnng"
		exit
	fi
fi

#check kubectl
kubectl >/dev/null 2>&1 || { echo >&2 "I require 'kubectl' but it's not installed.  Aborting."; exit 1; }

#check helm
helm >/dev/null 2>&1 || { echo >&2 "I require 'helm' but it's not installed.  Aborting."; exit 1; }

#check tiller, install on cluster if needed
helm version >/dev/null 2>&1 || { echo >&2 "Tiller not installed on Cluster. Installing tiller...";
	kubectl --namespace kube-system create serviceaccount tiller;
	kubectl create clusterrolebinding tiller --clusterrole cluster-admin --serviceaccount=kube-system:tiller;
	helm init --service-account tiller --history-max 100 --wait;
	kubectl patch deployment tiller-deploy --namespace=kube-system --type=json --patch='[{"op": "add", "path": "/spec/template/spec/containers/0/command", "value": ["/tiller", "--listen=localhost:44134"]}]';}

#create kubeyard namespace
kubectl create namespace kubeyard

#create secret for pulling images from private registry
kubectl create secret docker-registry regcred --docker-server=<YOUR-REGISTRY> --docker-username=<YOUR-USER-NAME> --docker-password=<YOUR-PASSWORD> --docker-email=<YOUR-EMAIL> --namespace kubeyard

#patch the secret from above
kubectl patch serviceaccount default -p '{"imagePullSecrets": [{"name": "regcred"}]}' --namespace kubeyard



#deploy web-ui with ENV variable for helm (will be acessed from withinh the web-ui app)
sudo bash kubernetes/web-ui/deploy_web_server.sh $EG_ENDPOINT $K8S_or_K8SYARN


#deploy jupyterHub with EG adress
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/
helm upgrade  --timeout=1200 --install jupyterhub jupyterhub/jupyterhub   --namespace kubeyard  --version=0.8.2 --values kubernetes/jupyterhub/config.yaml --set singleuser.extraEnv.KG_URL=$FULL_EG_ADRESS







