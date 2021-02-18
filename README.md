# Platform for interactive data science on distributed resources

## About...
The platform included in this repository allows working interactively on distributed resources. It offers  It offers a Web-UI for  monitoring of cluster usage (including running jobs and utilized resources) and a  simple management (killing jobs, creating and managing new interactive environments).  

It offers JupyterLab with the possibiltiy to start Spark (cluster-mode) notebooks out-of-the-box) and use predefined environments, i.e. kernels,  previously created via the Web-UI. This includes self-specyfied resources or additional conda and PIP packages.  

Every running notebook has access to shared HDFS storage and every notebook-user has his own personal storage. 

The JupyterHub together with single Jupyter-Lab instances are running within a Kubernetes Cluster while the kernels of every notebook are subject to YARN resource managers running within a Hadoop cluster.  An API server allows communication of the Kubernetes and Hadoop cluster. In result, following componenets are given:

 - Web-UI (Kubernetes)
 - JupyterHub with JupyterLab instances (Kubernetes)
 - Jupyter Enterprise Gateway for remote kernels (Hadoop)
 - remote kernels (Hadoop)

## Requirements

1. A Kubernetes cluster with at least 1 node. A single machine with about 32GB and 10CPUs should be sufficient for about 30 simultaneous users.  For testing, smaller machine is ok: 6-8GB and 4 CPUs. It was testes with Kubernetes 1.15.12.

2. A Hadoop YARN Cluster with a Edge (Master) node and at least one worker. The size of the worker node depends on the number of users and on the kernels they are working with, hence it varies. For testing, at least 4GB and 2 CPUs are needed. It was tested with Debian 10, Hadoop 2.10 and Spark 2.4. It may not work out-of-the-box for significantly different versions. In this case, the Docker image of Jupyter Enterprise Gateway and the API-server needs to be build with consideration of said versions.

3. Both clusters should be able to communicate with each other. E.g. by placing them in the same network. It is sufficient that the Edge node is reachable from the Kubernetes cluster. Allowing the Kubernetes pod IP-range for in- and out-going traffic should be enough.

4. Local terminal with *kubectl* installed and connected with correct Kuberenetes cluster. *Helm* should be installed as well.  Ubuntu as OS is recommended, no guarantee for Windows. 
5. While building images of Jupyter Enterprise Gateway and the API-server, it is imporant to mount proper paths. They should lead to the actual Hadoop and Spark files residing on the Hadoop Cluster. This is discussed in *Bulding Images* more in detail. 


## Content

The *kubernetes* directory contains all relevant files and software for the Kubernetes cluster, whereas *yarn* the ones needed for the Hadoop cluster.

The Python files of the Web-UI are located in */kubernetes/web-ui/app/application*. The ones of the API-server: /yarn/api-server/api-server/app*.

*deployment_k8s.sh*  is the deployment script for the Kubernetes cluster (from local terminal via *kubectl* and *Helm*). While starting it, it is necessary to provide the IP-address of the YARN Edge-Node, e.g. *bash deployment_k8s.sh 13.44.127.127*.

*deployment_yarn_docker.sh* is the deployment script used on the YARN side. It needs to be executed from the YARN Edge node. No input-parameters are needed.

## Building Images

### Web-UI

 1. Replace the build and push registries by desired registries in /software/kubernetes/web-ui/deploy_local_code.sh*. It should look like this <registry:tag>
2. Execute the script from step 1 (sudo migh be needed). This builds and puses the Web-UI image to the desired registry.
 3. Reference the pushed image in the Helm chart of the Web-UI: */software/kubernetes/web-ui/helm-flask/values.yaml* (line 8-9). Again in the form: <registry:tag>

### API-server
 1.  Execute following command from */yarn/api-server* (provide you own registry and tag):
```
sudo docker build \
-f ./docker/Dockerfile \
-t <registry:tag> \
--build-arg API_PORT=5000 \
--build-arg HADOOP_HOME=/usr/bin/hadoop \
--build-arg PYTHON_HOME=/opt/conda/default/bin/python \
--build-arg KERNEL_FOLDER=/usr/local/share/jupyter/kernels \
--build-arg PYTHON_VERSION=3.7 \
--build-arg HADOOP_VERSION=2.10.0 \
-f docker/Dockerfile \
.
```

It is important that the *--build-arg* refer to actual cluster paths. Adjust them if needed.  

2. Push the locally build image into registry of choice: *sudo docker push <registry:tag>*

### Jupyter Enterprise Gateway

 1.  Execute following command from */yarn/api-server* (provide you own registry and tag):
```
sudo docker build \
-f ./docker/Dockerfile \
-t <registry:tag> \
--build-arg GATEWAY_VERSION=2.2.0 \
--build-arg GATEWAY_PORT=8888 \
--build-arg SPARK_HOME=/usr/lib/spark \
--build-arg HADOOP_HOME=/usr/bin/hadoop \
--build-arg PYTHON_HOME=/opt/conda/default/bin/python \
--build-arg KERNEL_FOLDER=/usr/local/share/jupyter/kernels \
--build-arg PYTHON_VERSION=3.7 \
--build-arg SPARK_VERSION=2.4.6 \
--build-arg HADOOP_VERSION=2.7 \
.
```
2. Push the locally build image into registry of choice: *sudo docker push <registry:tag>*

## Deployment on Kubernetes 

1. Provide your Docker credentials in */software/deployment_k8s.sh* (line 42)
2.  Execute *deployment_k8s.sh* script with the address of the YARN-Edge node as input parameter, e.g. *bash deployment_k8s.sh 13.23.127.254*
3. You will be asked for your sudo password. Provide it.
4. Depending on your OS, it may happen, that the wait commands from the script does not work and you will get a *tiller not ready* error. In this case wait 20 seconds and try again, it should work now.

## Deployment on Hadoop 
1. Go to the Edge node (e.g. via SSH).
2. Activate impersonation (for notebook users). Add following in the *core-site.xml*: 

```
  <property>
    <name>hadoop.proxyuser.root.hosts</name>
    <value>*</value>
  </property>
  <property>
    <name>hadoop.proxyuser.root.groups</name>
    <value>*</value>
  </property>
```
3.  Restart YARN: *sudo systemctl restart hadoop-yarn-resourcemanager.service*
4.  Pull the repository.
5. Referene the Jupyter Enterprise Gateway and API-server images in *docker-compose.yml* (line 5 and 19)
6. Provide Docker credentials in */software/deployment_yarn_docker.sh* (line 18) and again the images, as in step 5 (line 21 and 22)
7. Execute the *deployment_yarn_docker.sh* script

## Accessing the platform

The ingress resources are available, however, they are left out (out-commented or deactivated), since setting ingress is very specific and depending e.g. on available host etc. If you want to use it, activate ingress for the JupyterHub (*config.yml*) and for the Web-UI (*values.yml*) and provide your own configuration.

You can, however, access the platform with port-forwarding. From the local terminal (with *kubectl*), you can port-forward the Web-UI and the JupyterHub as presented:

1. *kubectl port-forward --namespace kubeyard <`webui-pod> 5000*
2. *kubectl port-forward --namespace kubeyard <`proxy-pod> 8000* 

Now, under *localhost:5000* and *localhost:8000* corespondingly you can access the Web-UI and JupyterHub from your browser.

While visting the Web-UI, you need to log-in. For testing pourposes,  you can use following credentials:

Username: *Guest*, PW: *guest* (this can also be used for logging in into JupyterHub)
Username: *Admin*, PW: *admin*  (the admin user is more privileged) 
