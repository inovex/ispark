import yaml
import json
import requests
import os
import io
import re
import subprocess
from datetime import datetime

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


############
############ Helper methods for the Web-UI
############

#helper for getting a list of kernels from JEG API
#returns a list of names
def get_available_kernels(eg_adress):

    kernel_specs = requests.get(eg_adress + "/api/kernelspecs", timeout=0.5)
    kernel_specs = json.loads(kernel_specs.text)

    available_kernels_folders, available_kernels_names = [], []

    #except none to avoid accessing nulls
    try:
        for x in kernel_specs["kernelspecs"]:
            # print(kernel_specs["kernelspecs"][x]["spec"]["display_name"])
            available_kernels_names.append(kernel_specs["kernelspecs"][x]["spec"]["display_name"])
            available_kernels_folders.append(x)
    except:
        available_kernels_folders = None
        available_kernels_names = None

    return zip(available_kernels_folders, available_kernels_names)

#helper method for getting kernel.json from JEG
#returns resources and labels (for html template)
def get_kernel_spec(kernel_folder_name, eg_adress):

    kernel_specs = requests.get(eg_adress + "/api/kernelspecs")
    kernel_specs = json.loads(kernel_specs.text)
    resources = []
    resources_labels = []
    try:

        kernel_specs = kernel_specs["kernelspecs"][kernel_folder_name]
        name = kernel_specs['name']
        spark_opts = kernel_specs['spec']['env']['SPARK_OPTS']


        last_char_idx = len(spark_opts) - 1
        last_char = spark_opts[last_char_idx]

        start = spark_opts.find('--driver-memory=')
        finish = spark_opts.find('--', start + 1)
        resources.append(spark_opts[start + len('--driver-memory='):finish])
        resources_labels.append('Driver-memory')

        start = spark_opts.find('--num-executors=')
        finish = spark_opts.find('--', start + 1)
        resources.append(spark_opts[start + len('--num-executors='):finish])
        resources_labels.append('Num-executors')

        start = spark_opts.find('--executor-memory=')
        finish = spark_opts.find('--', start + 1)
        resources.append(spark_opts[start + len('--executor-memory='):finish])
        resources_labels.append('Executor-memory')

        start = spark_opts.find('--executor-cores=')
        finish = spark_opts.find(last_char, start)
        resources.append(spark_opts[start + len('--executor-cores='):finish+1])
        resources_labels.append('Executor-cores')


        # name = kernel_specs['name']
        # spec = kernel_specs['spec']
        # env = kernel_specs['spec']['env']
        #
        # ##iterate over specs of specific kernel, create a list with values and headers
        # spec_list = []
        # spec_list.append(name)
        # labels_list = []
        # labels_list.append('Name')
        # for key in spec:
        #     # print (spec[key])
        #     # print (key)
        #     if type(spec[key]) is list:
        #         tmp_list = spec[key]
        #         for element in tmp_list:
        #             spec_list.append(element)
        #             labels_list.append(key)
        # for key in env:
        #     if (key == 'SPARK_OPTS'):
        #         tmp = env[key].split('--')
        #         for i in range(0, len(tmp)):
        #             labels_list.append('SPARK_OPTS')
        #             spec_list.append(tmp[i])
        #     else:
        #         spec_list.append(env[key].split('--'))
        #         labels_list.append(key)



    except:
        kernel_specs = None
        print("Error, kernel was not found")

    return name, resources, resources_labels

#helper method to check whether JEG is reachable
#returns true if yes
def check_eg_connection(eg_adress):
    try:
        requests.get(eg_adress + "/api/kernelspecs", timeout=0.5)
        connection_success = True

    except:
        connection_success = False
    print(connection_success)
    return connection_success


#getting info from YARN API
#various API endpoints from YARN are involved
#returns dictionaries with various metrics
def get_cluster_info(yarn_api_adress):

    cluster_info = requests.get(yarn_api_adress + '/info', timeout=0.5)
    cluster_info = (cluster_info.json())['clusterInfo']

    logger.debug("get_info")
    print(cluster_info)

    cluster_metrics = requests.get(yarn_api_adress + '/metrics', timeout=0.5)
    cluster_metrics = (cluster_metrics.json())['clusterMetrics']

    cluster_scheduler = requests.get(yarn_api_adress + '/scheduler', timeout=0.5)
    cluster_scheduler = (cluster_scheduler.json())['scheduler']['schedulerInfo']

    cluster_nodes = requests.get(yarn_api_adress + '/nodes', timeout=0.5)
    cluster_nodes = (cluster_nodes.json())['nodes']['node']

    cluster_apps = requests.get(yarn_api_adress + '/apps', timeout=0.5)

    #avoid error if there were no applications executed
    try:
        cluster_apps = (cluster_apps.json())['apps']['app']
    except:
        cluster_apps = []




    return prepare_cluster_infos_yarn(cluster_info, cluster_metrics, cluster_scheduler, cluster_nodes, cluster_apps)



#cleaning and filtering of dictionaries containing cluster info from above method
#returns only specific parameters, the rest is dropped
def prepare_cluster_infos_yarn(cluster_info, cluster_metrics, cluster_scheduler, cluster_nodes, cluster_apps):

    #prepare data from request /infos
    cluster_info_labels = ['state', 'haState', 'resourceManagerVersion', 'hadoopVersion',
                                'haZooKeeperConnectionState']
    cluster_info_filtred = {}
    for label in cluster_info_labels:
        cluster_info_filtred[label] = cluster_info[label]

    #prepare ddata from /scheduler
    cluster_scheduler_labels = ['type', 'capacity', 'usedCapacity']
    cluster_scheduler_filtred = {}
    for label in cluster_scheduler_labels:
        cluster_scheduler_filtred[label] = cluster_scheduler[label]

    #prepare data from request /metrics
    cluster_metrics_labels = ['totalMB', 'availableMB', 'reservedMB', 'allocatedMB', 'totalVirtualCores',
                              'availableVirtualCores','reservedVirtualCores',
                              'allocatedVirtualCores', 'totalNodes', 'activeNodes']

    cluster_metrics_filtred = {}
    for label in cluster_metrics_labels:
        cluster_metrics_filtred[label] = cluster_metrics[label]

    #prepare data from /nodes
    cluster_nodes_labels = ['nodeHostName', 'state', 'nodeHTTPAddress', 'availMemoryMB', 'usedMemoryMB',
                            'availableVirtualCores', 'usedVirtualCores']

    cluster_nodes_filtred = []
    for i in range(0, len(cluster_nodes)):
        tmp = []
        for label in cluster_nodes_labels:
            tmp.append(cluster_nodes[i][label])
        cluster_nodes_filtred.append(tmp)

    cluster_apps_labels = ['id', 'user', 'name', 'queue', 'state', 'finalStatus', 'progress', 'applicationType',
                           'allocatedMB', 'reservedMB', 'allocatedVCores', 'reservedVCores', 'runningContainers']

    cluster_apps__running_filtred = []
    cluster_apps__new_filtred = []
    cluster_apps__submitted_filtred = []
    cluster_apps__accepted_filtred = []
    cluster_apps__finished_filtred = []
    cluster_apps__failed_filtred = []
    cluster_apps__killed_filtred = []
    cluster_all_apps_filtred = []

    if len(cluster_apps) > 0:

        for i in range(0, len(cluster_apps)):
            tmp = []
            if cluster_apps[i]['state'] == 'RUNNING':
                for label in cluster_apps_labels:
                    tmp.append(cluster_apps[i][label])
                cluster_apps__running_filtred.append(tmp)
            elif cluster_apps[i]['state'] == 'NEW':
                for label in cluster_apps_labels:
                    tmp.append(cluster_apps[i][label])
                cluster_apps__new_filtred.append(tmp)
            elif cluster_apps[i]['state'] == 'SUBMITED':
                for label in cluster_apps_labels:
                    tmp.append(cluster_apps[i][label])
                cluster_apps__submitted_filtred.append(tmp)
            elif cluster_apps[i]['state'] == 'ACCEPTED':
                for label in cluster_apps_labels:
                    tmp.append(cluster_apps[i][label])
                cluster_apps__accepted_filtred.append(tmp)
            elif cluster_apps[i]['state'] == 'FINISHED':
                for label in cluster_apps_labels:
                    tmp.append(cluster_apps[i][label])
                cluster_apps__finished_filtred.append(tmp)
            elif cluster_apps[i]['state'] == 'FAILED':
                for label in cluster_apps_labels:
                    tmp.append(cluster_apps[i][label])
                cluster_apps__failed_filtred.append(tmp)
            elif cluster_apps[i]['state'] == 'KILLED':
                for label in cluster_apps_labels:
                    tmp.append(cluster_apps[i][label])
                cluster_apps__killed_filtred.append(tmp)
            elif cluster_apps[i]['state'] == '-':
                for label in cluster_apps_labels:
                    tmp.append(cluster_apps[i][label])
                cluster_apps__running_filtred.append(tmp)
        cluster_all_apps_filtred.append(cluster_apps__running_filtred)
        cluster_all_apps_filtred.append(cluster_apps__new_filtred)
        cluster_all_apps_filtred.append(cluster_apps__submitted_filtred)
        cluster_all_apps_filtred.append(cluster_apps__finished_filtred)
        cluster_all_apps_filtred.append(cluster_apps__failed_filtred)
        cluster_all_apps_filtred.append(cluster_apps__killed_filtred)

    else:
        cluster_all_apps_filtred = [[['-', '-', '-', '-', '-', '-', '-', '-',
                           '-', '-', '-', '-', '-']]]


    #cluster_all_apps_filtred = [x for x in cluster_all_apps_filtred if x != []]


    return cluster_info_filtred,cluster_scheduler_filtred, cluster_metrics_filtred, cluster_nodes_filtred, cluster_all_apps_filtred


#returns headers for parameters from  prepare_cluster_infos_yarn()
#needed to display said params nicely in html
def prepare_headers():
    cluster_metrics_headers = ['Total memory in MB', 'Available memory in MB', 'Reserved memory in MB', 'Allocated memory in MB',
                               'Total vCPUs', 'Available vCPUs', 'Reserved vCPUs', 'Allocated vCPUs',
                               'Total nodes', 'Active nodes']

    cluster_nodes_headers = ['Host name of the node', 'Current state', 'HTTP Adress', 'Memory', 'Cores']

    cluster_scheduler_headers = ['Scheduler type', 'Scheduler capacity', 'Used capacity']

    cluster_info_headers = ['RM state', 'Hadoop state', 'RM version', 'Hadoop version',
                                'Hadoop ZooKeeper']

    cluster_apps_headers = ['id', 'user', 'name', 'queue', 'state', 'finalStatus', 'progress', 'applicationType',
                           'allocatedMB', 'reservedMB', 'allocatedVCores', 'reservedVCores', 'runningContainers']

    return cluster_info_headers, cluster_scheduler_headers, cluster_metrics_headers, cluster_nodes_headers, cluster_apps_headers


#saves cluster and admin limits to the json with limits
def write_rules_to_json(rules_form):

    #save json at kernels path
    with open('./cluster-rules/cluster_rules.json', 'w') as outfile:
        json.dump(rules_form, outfile)

    return True

#used for admin view
#returns true if specified resources are  within cluster limts, otherwise false
#error number can be optimized for showing specyfing errors
def check_with_yarn(rules, nodes_num, memory, cores):

    msg = 'Cluster does not have enough ressources for this spec. Nodes: ' + str(nodes_num) +  ', memory per node:' + str(memory) + ', cores: ' + str(cores)
    error = 0

    if(int(rules['clusterResourceRules-allowedDriverMemory']) > int(memory)):
        error = 3
    if(int(rules['clusterResourceRules-allowedNumExecutors']) > int(nodes_num)):
        error = 3
    if(int(rules['clusterResourceRules-allowedExecutorMemory']) > int(memory)):
        error = 3
    if(int(rules['clusterResourceRules-allowedExecutorCores']) > int(cores)):
        error = 3
    if(int(rules['clusterResourceRules-defaultDriverMemory']) > int(memory)):
        error = 3
    if(int(rules['clusterResourceRules-defaultNumExecutors']) > int(nodes_num)):
        error = 3
    if(int(rules['clusterResourceRules-defaultExecutorMemory']) > int(memory)):
        error = 3
    if(int(rules['clusterResourceRules-defaultExecutorCores']) > int(cores)):
        error = 3

    if error == 3:
        return False, msg

    msg = 'Rules updated...'

    return True, msg

#checks with jeson limits for adding new kernel or modifying resources
#returns true if specified resources are  within admin limts, otherwise false
def check_with_json(driver_mem, num_exec, exec_mem, exec_cores):

    with open('./cluster-rules/cluster_rules.json', 'r') as f:
        rules_json = json.load(f)

    error = 0
    if(int(driver_mem) > int(rules_json['clusterResourceRules-allowedDriverMemory'])):
        error = 1
    if(int(num_exec) > int(rules_json['clusterResourceRules-allowedNumExecutors'])):
        error = 1
    if(int(exec_mem) > int(rules_json['clusterResourceRules-allowedExecutorMemory'])):
        error = 1
    if(int(exec_cores) > int(rules_json['clusterResourceRules-allowedExecutorCores'])):
        error = 1


    if error == 1:
        return False, 'These resources exceed set limits. Maximally allowed are: -driver mem: ' + str(rules_json['clusterResourceRules-allowedDriverMemory']) + \
                        ' -num executors:' + str(rules_json['clusterResourceRules-allowedNumExecutors']) + ' -executor mem:' + str(rules_json['clusterResourceRules-allowedExecutorMemory']) + \
                        ' -executor cores:' + str(rules_json['clusterResourceRules-allowedExecutorCores'])

    return True, "Sucess"