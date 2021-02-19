import os
#import yaml
import ruamel.yaml
import io
import re
import sys
import time
import json
import subprocess
from os.path import dirname as up
print("Python version")
print (sys.version)
print("Version info.")




import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


#############
############# Helper methods for the API-Server
#############

#convert to utf
def my_unicode_repr(self, data):
    return self.represent_str(data.encode('utf-8'))


#returns full path to a kernel with given name
def return_kernel_path(folder_name):

    kernel_path = os.environ['KERNEL_FOLDER']

    return kernel_path + '/' + folder_name + '/'

#helper for adding a new kernel (step 1)
def prepare_paths_and_names(name):

    kernel_path = os.environ['KERNEL_FOLDER']

    name = re.sub('([A-Z]{1})', r'\1', name).lower()
    name = name.replace(" ", "_")

    kernel_path = kernel_path + "/" + name + "_folder"

    kernel_folder_name = name + "_folder"

    return kernel_path, name, name + "_folder"

#check whether a path exists (avoid overwriting kernels)
def check_path(path):

    return os.path.isdir(path)

#create whole directory structure for given kernel
def prepare_folders(kernel_path, conda_env_name):


    try:
        os.mkdir(kernel_path)
        os.mkdir(kernel_path +'/' + 'scripts')
        os.mkdir(kernel_path + '/' + 'bin')
        os.mkdir(kernel_path + '/' + conda_env_name)
    except OSError:
        print("Creation of the directory  failed:  " + kernel_path )
        logger.debug("Creation of the directory  failed:  " + kernel_path)
        return False
    else:
        print("Successfully created the directory:  " + kernel_path + " and two subfolders")
        return True

#helper for creating the env yaml for conda
def create_conda_env_yaml(folder_name, conda_env_name, extra_conda_channels, language, extra_conda_packages, extra_pip_packages):

    extra_conda_channels = [x.strip() for x in extra_conda_channels.split(',')]

    extra_conda_packages = [x.strip() for x in extra_conda_packages.split(',')]
    extra_pip_packages = [x.strip() for x in extra_pip_packages.split(',')]

    conda_env_name = re.sub('([A-Z]{1})', r'\1', conda_env_name).lower()
    conda_env_name.replace(" ", "_")

    path_for_yaml = os.environ['KERNEL_FOLDER'] + '/' + folder_name

    extra_conda_channels.insert(0, "anaconda")

    #python 3 and 2 require different versions of same packages for a kernel
    if language == "python3":
        print("xxxxxxxxxxx----python3")
        extra_conda_packages.insert(0, "ipython")
        extra_conda_packages.insert(0, "future")
        extra_conda_packages.insert(0, "pycryptodomex")
        extra_conda_packages.insert(0, "jupyter_client")
        extra_conda_packages.insert(0, "python=3.7")
        extra_pip_packages.insert(0, "ipykernel")
    elif language == "python2":
        print("xxxxxxxxxxx----python2")
        extra_pip_packages.insert(0, "IPython==5.8.0")
        extra_conda_packages.insert(0, "jupyter_client=5.3.1")
        extra_conda_packages.insert(0, "pycryptodomex")
        extra_conda_packages.insert(0, "future")
        extra_conda_packages.insert(0, "python=2.7")
        extra_pip_packages.insert(0, "ipykernel==4.10.0")


    extra_conda_packages.append({'pip' : extra_pip_packages})

    extra_pip_packages = list(filter(len, extra_pip_packages))
    extra_conda_channels = list(filter(len, extra_conda_channels))
    extra_conda_packages = list(filter(len, extra_conda_packages))

    yaml_prep = {"name": conda_env_name,
                 "channels": extra_conda_channels,
                 "dependencies": extra_conda_packages}

    yaml = ruamel.yaml.YAML()
    yaml.default_flow_style = False
    yaml.default_style = '"'
    yaml.Representer.represent_key = non_quoted_key
    yaml.indent(mapping=2, sequence=4, offset=2)

    try:
        with open(path_for_yaml + '/' + conda_env_name + '/' + conda_env_name + '.yml', 'w') as f:
            yaml.dump(yaml_prep, f)
    except OSError:
        print("Creation of the yml file for te Conda environment failed")
        return False
    else:
        print("Successfully created yml file for the Conda environment")

    return True

#helper for yaml (allows wished structure)
def non_quoted_key(self, data):
   if isinstance(data, ruamel.yaml.compat.string_types):
       data = ruamel.yaml.scalarstring.PlainScalarString(data)
   return self.represent_data(data)


#creaters conda env from yarn
def create_conda_env_from_yaml(kernel_path, conda_env_name):

    env_path_to_yaml = kernel_path + "/" + conda_env_name + "/" + conda_env_name +'.yml'
    env_path = kernel_path + "/"  + conda_env_name
    print("Installing environment...")
    print(kernel_path)
    print(conda_env_name)

    #e.g. if a wrong package name was provided
    try:
        subprocess.check_output("conda env create -f " + env_path_to_yaml +  " -p " + env_path, shell=True)
    except subprocess.CalledProcessError as e:
        return False


   # try:
   #     os.system("conda env create -f " + env_path_to_yaml +  " -p " + env_path)
   # except OSError:
   #     print("Installation of conda env failed")
   #     return False


    print("Environment installed. Zipping....")

    print(kernel_path)
    print("zip -r " + conda_env_name + ".zip "+ conda_env_name)
    try:
        current = os.getcwd()
        os.chdir(kernel_path)
        os.system("pwd")
        os.system("zip -r " + conda_env_name + ".zip "+ conda_env_name)
        os.chdir(current)
        os.system("pwd")
    except OSError:
        print("Zipping failed")
        return False

    print("Zipping finished.")



    return True

#i think it can be deleted
def prepare_kernel_json_template_for_ui(kernel_json):

    return kernel_json

#copy json from a template, modify it and dump
def prepare_kernel_specs_json(newKernelSpec, kernel_path, conda_env_name):
    logger.debug("Prep kernel specs")

    subprocess.call("cp api-server/kernel_templates/python/kernel.json api-server/kernel_templates/python/kernel_" + conda_env_name + ".json",  shell=True)




    with open("api-server/kernel_templates/python/kernel_" +  conda_env_name + ".json") as f:
        kernel_json = json.load(f)

    os.system("rm api-server/kernel_templates/python/kernel_" + conda_env_name + ".json")


    kernel_json['language'] = newKernelSpec["kernelEnvironment-language"]
    kernel_json['display_name'] = newKernelSpec["kernelEnvironment-displayName"]
    spark_home = os.environ['SPARK_HOME'].replace('"', '')
    kernel_json['env']['SPARK_HOME'] = spark_home
    logger.debug("-----------------------------")
    logger.debug( kernel_json['env']['SPARK_HOME'])
    logger.debug("Prep kernek specs -2")
    if newKernelSpec["kernelEnvironment-language"] == 'python2' or newKernelSpec["kernelEnvironment-language"] == 'python3':
        kernel_json['env']['PYSPARK_PYTHON'] = kernel_path + '/' + conda_env_name + '/bin/python'
        kernel_json['env']['PYTHONPATH']  = kernel_path + '/' + conda_env_name + '/bin/python'

        #replace env params from template with new ones
        python_spark_opts = kernel_json['env']['SPARK_OPTS']

        ###Replace significant params with params from UI
        tmp_conf_old = '--conf spark.yarn.appMasterEnv.PYSPARK_PYTHON=py37/py37/bin/python'
        tmp_conf_new = ' --conf spark.yarn.appMasterEnv.PYSPARK_PYTHON=' + conda_env_name + '/' + conda_env_name + '/bin/python'
        python_spark_opts = python_spark_opts.replace(tmp_conf_old, tmp_conf_new)

        ###
        tmp_conf_old = '--conf spark.yarn.appMasterEnv.PATH=.py37/py37/bin:$PATH ${KERNEL_EXTRA_SPARK_OPTS}'
        tmp_conf_new = ' --conf spark.yarn.appMasterEnv.PATH=.' + conda_env_name + '/' + conda_env_name + '/bin:$PATH ${KERNEL_EXTRA_SPARK_OPTS}'
        python_spark_opts = python_spark_opts.replace(tmp_conf_old, tmp_conf_new)

        ###
        tmp_conf_old = '--conf spark.yarn.dist.archives=/usr/local/share/jupyter/kernels/spark_python37/py37.zip#py37 '
        tmp_conf_new = ' --conf spark.yarn.dist.archives=' + kernel_path + '/' + conda_env_name + '.zip#' + conda_env_name
        python_spark_opts = python_spark_opts.replace(tmp_conf_old, tmp_conf_new)

        ###
        tmp_conf_old = '--driver-memory=1024M'
        tmp_conf_new = ' --driver-memory=' + newKernelSpec['kernelEnvironment-driverMemory'] + 'M'
        python_spark_opts = python_spark_opts.replace(tmp_conf_old, tmp_conf_new)

        ###
        tmp_conf_old = '--executor-memory=1024M'
        tmp_conf_new = ' --executor-memory=' + newKernelSpec['kernelEnvironment-executorMemory'] + 'M'
        python_spark_opts = python_spark_opts.replace(tmp_conf_old, tmp_conf_new)

        ###
        tmp_conf_old = '--num-executors=1'
        tmp_conf_new = ' --num-executors=' + newKernelSpec['kernelEnvironment-numExecutors']
        python_spark_opts = python_spark_opts.replace(tmp_conf_old, tmp_conf_new)

        ###
        tmp_conf_old = '--executor-cores=1'
        tmp_conf_new = ' --executor-cores=' + newKernelSpec['kernelEnvironment-executorCores']
        python_spark_opts = python_spark_opts.replace(tmp_conf_old, tmp_conf_new)

        #update json
        kernel_json['env']['SPARK_OPTS'] = python_spark_opts

    if  newKernelSpec["kernelEnvironment-language"] == 'scala':
        logger.debug("not quiete there yet")

    if newKernelSpec["kernelEnvironment-language"] == 'r':
        logger.debug("not quiete there yet")

    logger.debug("Prep kernel specs-3")

    argv = kernel_json['argv']

    #tmp_conf_old = '/usr/local/share/jupyter/kernels/spark_python37/bin/run.sh'
    tmp_conf_new = kernel_path + '/bin/run.sh'
    argv[0] = tmp_conf_new

    #update json
    kernel_json['argv'] = argv

    logger.debug("Prep kernel specs-4")
    #save json at kernels path
    with open(kernel_path + '/kernel.json', 'w') as outfile:
        json.dump(kernel_json, outfile)

    logger.debug("Prep kernel specs-5")
    return True

#copy launcher and run.sh into correspoding directorires for a new kernel
def provide_rest_files(kernel_path, language):

    if language == 'python3' or language == 'python2':
        os.system("cp api-server/kernel_templates/python/bin/run.sh " + kernel_path + '/bin')
        os.system("cp api-server/kernel_templates/python/scripts/launch_ipykernel.py " + kernel_path + '/scripts')

    if language == 'scala':
        os.system("cp api-server/kernel_templates/scala/bin/run.sh " + kernel_path + '/bin')
        os.system("cp api-server/kernel_templates/python/scripts/launch_ipykernel.py " + kernel_path + '/scripts')

    if language == 'r':
        print ("Note quite there yet")
        return False

    return True

#modifies the resources in the kernel.json
def modify_resources(path, driver_mem, num_exec, exec_mem, exec_cores):
    print("##########################")
    with open(path + "kernel.json", "r") as f:
        kernel_json = json.load(f)


    new_spark_opts = kernel_json['env']['SPARK_OPTS']

    last_char_idx = len(new_spark_opts) - 1
    start = new_spark_opts.find('--driver-memory=')
    finish = new_spark_opts.find(' ', start + 1)
    new_spark_opts = new_spark_opts.replace(new_spark_opts[start:finish], "--driver-memory=" + str(driver_mem) + "M")

    start = new_spark_opts.find('--num-executors=')
    finish = new_spark_opts.find(' ', start + 1)
    new_spark_opts = new_spark_opts.replace(new_spark_opts[start:finish], "--num-executors=" + str(num_exec))
    start = new_spark_opts.find('--executor-memory=')
    finish = new_spark_opts.find(' ', start + 1)
    new_spark_opts = new_spark_opts.replace(new_spark_opts[start:finish], "--executor-memory=" + str(exec_mem) + "M")

    start = new_spark_opts.find('--executor-cores=')
    finish = last_char_idx
    new_spark_opts = new_spark_opts.replace(new_spark_opts[start:finish], "--executor-cores=" + str(exec_cores))

    kernel_json['env']['SPARK_OPTS'] = new_spark_opts
    with open(path + "kernel.json", 'w') as outfile:
        json.dump(kernel_json, outfile)

    return "All good"

#chaning JEG config values (amount of allowed kernels)
def update_jeg_config(rules):

    allowed_kernels = rules['clusterResourceRules-allowedKernelsNumber']

    tmp = open('jupyter_enterprise_gateway_config.py', "r")
    lines = tmp.readlines()
    tmp.close()

    idx = 0
    for line in lines:
        if 'c.EnterpriseGatewayConfigMixin.max_kernels_per_user' in line:
            print(line)
            break;
        idx = idx + 1
    lines[idx] = 'c.EnterpriseGatewayConfigMixin.max_kernels_per_user=' + str(allowed_kernels) + '\n'

    tmp = open('jupyter_enterprise_gateway_config.py', "w+")
    for line in lines:
        tmp.write(line)
    tmp.close()


    return True

#deletes created folders if an error occurs during add new kernel
def clean_up_folders(kernel_path):

    subprocess.call("rm -r " + kernel_path, shell=True)

    return ("Kernel folders removed")