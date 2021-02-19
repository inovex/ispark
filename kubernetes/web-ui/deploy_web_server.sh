#!/usr/bin/env bash
mkdir kubernetes/web-ui/helm-flask/files
cp ~/.kube/config kubernetes/web-ui/helm-flask/files/config
helm del --purge webui-ispark
helm install kubernetes/web-ui/helm-flask --set data.eg_adress=$1 --set data.architecture=$2 --namespace=kubeyard --name=webui-ispark #--dry-run --debug
rm kubernetes/web-ui/helm-flask/files/config
