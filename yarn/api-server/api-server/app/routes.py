from flask import Flask
from flask import jsonify
from flask import request
import sys
import util
import ruamel.yaml
import os
import subprocess

import json
import requests
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

#############
############# Main module of the API-Server, all endpoints are defined here
#############


#web_ui_adress = os.environ['WEB_UI_ADRESS']
#main_ip = web_ui_adress + ":5000"

#WEB_UI_ADRESS = 'http://10.52.0.6:5000'


#creates a new kernel specification on behalf of the web-ui
#returns a confirmation message (if error, it is returned at which point)
@app.route('/new_kernel_specs', methods=['POST'])
def get_new_kernel_specs():
    logger.debug("Adding a new Kernel...")
    print(sys.version)
    newKernelSpec = request.form.to_dict()

    for s in newKernelSpec:
        newKernelSpec[s] = "{0}".format(newKernelSpec[s])


    #step 1, names and paths for folders are prepared
    kernel_path, conda_env_name, folder_name = util.prepare_paths_and_names(newKernelSpec['kernelEnvironment-displayName'])

    if util.check_path(kernel_path):
        logger.debug("Folder exists already. Aborting...")
        return "Folder exists already. Aborting..."

    #step 2, creating actual folders
    prepare_folders_success = util.prepare_folders(kernel_path, conda_env_name)

    if prepare_folders_success == False:
        util.clean_up_folders(kernel_path)
        logger.debug("Error while creating folder structure")
        return "Error while creating folder structure"

    #step 3, creating a yaml file for the conda env, dict with params from UI as input
    create_yaml_success = util.create_conda_env_yaml(folder_name,
                                conda_env_name,
                                newKernelSpec['kernelEnvironment-extraCondaChannels'],
                                newKernelSpec['kernelEnvironment-language'],
                                newKernelSpec['kernelEnvironment-extraCondaPackages'],
                                newKernelSpec['kernelEnvironment-extraPIPPackages'])


    if create_yaml_success == False:
        util.clean_up_folders(kernel_path)
        logger.debug("Error while creating yml env file for Conda")
        return "Error while creating yml env file for Conda"

    #step 4, installing conda env from created yaml
    install_and_zip_env_success = util.create_conda_env_from_yaml(kernel_path, conda_env_name)

    if install_and_zip_env_success == False:
        util.clean_up_folders(kernel_path)
        logger.debug("Error while install & zip environment")
        return "Error while install & zip environment"

    #step 5, creating the JSON file (copy and modify a template)
    create_kernel_json__success = util.prepare_kernel_specs_json(newKernelSpec, kernel_path, conda_env_name)

    if create_kernel_json__success == False:
        logger.debug("Error with creating kernel JSON file")
        util.clean_up_folders(kernel_path)
        return "Error with creating kernel JSON file"

    #step 6, copy other files, e.g. launcher or run.sh
    util.provide_rest_files(kernel_path, newKernelSpec['kernelEnvironment-language'])


    print("Adding kernel finished...")

    return "finish"

#endpoint for getting logs
#return logs for provided application ID
@app.route('/logs', methods=['GET', 'POST'])
def get_app_logs():

    application_id = str(request.args['application_id'])

    logs = subprocess.run(['yarn', 'logs',  '--applicationId', application_id], stdout=subprocess.PIPE)

    return logs.stdout

#endpoint for updating JEG config (amount of allowed kernels)
@app.route('/update_cluster_rules', methods=['GET', 'POST'])
def update_cluster_rules():

    rules = request.form.to_dict()
    util.update_jeg_config(rules)

    return 'Config updated'

#endpoint for modifying a kernel resource specs
@app.route('/modify_kernel_specs', methods=['GET', 'POST'])
def modify_kernel():
    new_kernel_specs = request.form.to_dict()
    print(new_kernel_specs)

    path = util.return_kernel_path(new_kernel_specs['modifyRessources-folder'])


    util.modify_resources(path, new_kernel_specs['modifyRessources-driverMemory'],
                          new_kernel_specs['modifyRessources-numExecutors'],
                          new_kernel_specs['modifyRessources-executorMemory'],
                          new_kernel_specs['modifyRessources-executorCores'],
                          )
    msg = 'Kernel specs modified successfully'
    #except:
    #    msg = 'Kernel specs modification error'

    return msg

#endpoint for deleting a kernel
@app.route('/delete_kernel', methods=['GET', 'POST'])
def delete_kernel():
    folder_to_delete = request.form.to_dict()
    logger.debug(folder_to_delete)
    full_path_to_delete = util.return_kernel_path(folder_to_delete['folder'])

    try:
        subprocess.call("rm -r " + full_path_to_delete,  shell=True)
        msg = "Deleting completed"
    except:
        msg = "Error with deleting kernel"

    return msg

#endpoint for killing an application
@app.route('/kill_application', methods=['GET', 'POST'])
def kill_application():
    application_to_delete = request.form.to_dict()
    logger.debug(application_to_delete['application_id'])

    try:
        subprocess.call("yarn application -kill  " + application_to_delete['application_id'],  shell=True)
        msg = "Application deleted"
    except:
        msg = "Error with deleting application"

    return msg

#this endpoint provides env info for deteiled kernel view of the web-ui
#env yaml is retuned
@app.route('/get_env_info', methods=['GET', 'POST'])
def get_env_info():

    folder_with_yml = request.form.to_dict()
    logger.debug(folder_with_yml)
    full_path_kernel = util.return_kernel_path(folder_with_yml['folder'])
    env_name = folder_with_yml['folder'][:-7]
    try:
        with open(full_path_kernel + env_name + '/' + env_name + '.yml', 'r') as stream:
            env = ruamel.yaml.safe_load(stream)
    except:
        return "Could not load env information"

    return json.dumps(env)