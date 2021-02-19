"""Routes for core Flask app."""
import os
import time
import json
from flask import jsonify
from flask import Blueprint, render_template, redirect, flash, url_for
from flask_assets import Environment, Bundle
from flask import current_app as app
from flask_simplelogin import login_required, get_username

import requests

from flask import request
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


from application.forms import NewForm, NewFormClusterRules, NewFormModifyRessources
import application.util as util


############
############ Main module for the Web-UI, contains all endpoints
############


main_bp = Blueprint('main_bp', __name__,
                    template_folder='templates',
                    static_folder='static')

assets = Environment(app)
Environment.auto_build = True
Environment.debug = False

##architecture variable (currently only yarn)
ARCHITECTURE = os.environ['ARCHITECTURE']

##adresses
main_ip = os.environ['EG_ADRESS']
eg_adress ="http://" + main_ip + ":8888"
api_adress ="http://" +  main_ip + ":5000"
yarn_ui_adress = "http://" +  main_ip + ":8088/cluster"
yarn_api_adress = "http://" +  main_ip + ":8088/ws/v1/cluster"



@main_bp.route('/')
@login_required
def home():
    """Landing page."""

    return redirect("/cluster")


#main cluster view
#accesses JEG API, YARN API. Logs and Killing are separate methods
@main_bp.route('/cluster',  methods=['GET', 'POST'])
def cluster():

    connection_eg_success = util.check_eg_connection(eg_adress)
    if connection_eg_success:
        available_kernels  = util.get_available_kernels(eg_adress)
    else:
        available_kernels = "No Kernel Avialable"
        return redirect(url_for('main_bp.main_kernels'))

    print(connection_eg_success)
    print("Done")

    if ARCHITECTURE == 'yarn':

        cluster_info_filtred,cluster_scheduler_filtred,\
        cluster_metrics_filtred, cluster_nodes_filtred, cluster_all_apps_filtred = util.get_cluster_info(yarn_api_adress)
        cluster_info_headers, cluster_scheduler_headers, \
        cluster_metrics_headers, cluster_nodes_headers, cluster_apps_headers = util.prepare_headers()

        return render_template("cluster_yarn.html", succes_cluster_info='True',
                        cluster_info=list(cluster_info_filtred.values()),
                        cluster_scheduler=list(cluster_scheduler_filtred.values()),
                        cluster_metrics=list(cluster_metrics_filtred.values()),
                        cluster_nodes=cluster_nodes_filtred,
                        num_nodes=cluster_metrics_filtred['activeNodes'],
                        cluster_apps=cluster_all_apps_filtred,
                        cluster_info_headers=cluster_info_headers,
                        cluster_scheduler_headers=cluster_scheduler_headers,
                        cluster_metrics_headers=cluster_metrics_headers,
                        cluster_nodes_headers=cluster_nodes_headers,
                        cluster_apps_headers=cluster_apps_headers,
                        connection_eg_success=connection_eg_success,
                        available_kernels=available_kernels)

    return render_template("cluster_yarn.html", succes_cluster_info='False')



#the plain kernel view
#used only after deleting a kernel, uses JEG API
@main_bp.route('/kernels')
@login_required
def main_kernels():

    connection_eg_success = util.check_eg_connection(eg_adress)
    if connection_eg_success:
        available_kernels  = util.get_available_kernels(eg_adress)
    else:
        available_kernels = "No YARN connection"
    print(connection_eg_success)

###test
#    available_kernels = []
#    available_kernels.append("Python")
#    available_kernels.append("Custom Py 37 Cluster Mode")
#    available_kernels.append("Custom Py 27 Cluster Mode")
#    available_kernels.append("Custom Scala Cluster Mode")
#    connection_eg_success = True
#test
    return render_template('base_kernels.html', connection_eg_success=connection_eg_success,
                           available_kernels=available_kernels)

#detailed info about a kernel, uses API-server and JEG API
#shows resources from the kernel.json and env info from  the env yaml
@main_bp.route('/kernels/<string:kernel_folder_name>')
def show_kernel_details(kernel_folder_name):
    connection_eg_success = util.check_eg_connection(eg_adress)
    if connection_eg_success:
        available_kernels  = util.get_available_kernels(eg_adress)
        to_send = {'folder': kernel_folder_name}
        env_details = requests.post(api_adress + "/get_env_info", data=to_send)
        env_details = env_details.text
    else:
        available_kernels = "No Kernel Avialable"
    logger.debug(env_details)
    env_libs_conda = []
    env_libs_pip = []

    #parses jsonfied yaml from yarn
    if(env_details != 'Could not load env information'):
        env_details = json.loads(env_details)
        for l in env_details['dependencies']:
            if ('pip' not in l):
                env_libs_conda.append(l)
            else:
                for pip in l['pip']:
                    env_libs_pip.append(pip)
    else:
        env_libs_conda.append("Problem with getting env info")
    try:
        name, resources, resources_labels = util.get_kernel_spec(kernel_folder_name, eg_adress)
    except:
        return redirect(url_for('main_bp.main_kernels'))

    extra_kernel_infos = " "

    return render_template('show_kernel_details.html', name = name,
                           resources=resources,
                           resources_labels=resources_labels,
                           available_kernels=available_kernels,
                           connection_eg_success=connection_eg_success,
                           env_libs_conda=env_libs_conda,
                           env_libs_pip=env_libs_pip)


#the add new kernel functionality, uses API-Server
@main_bp.route('/add_kernel', methods=['GET', 'POST'])
def add_kernel():

    form = NewForm()

    requests.post(api_adress + "/get_kernel_files", data='hey')

    with open('./cluster-rules/cluster_rules.json', 'r') as f:
        rules_json = json.load(f)


    if form.validate_on_submit():
        test = request.form.to_dict()

        #compare to limits
        status, msg = util.check_with_json(test['kernelEnvironment-driverMemory'],
                                           test['kernelEnvironment-numExecutors'],
                                           test['kernelEnvironment-executorMemory'],
                                           test['kernelEnvironment-executorCores'])

        if status:
            msg_from_api = requests.post(api_adress + "/new_kernel_specs", data=test)
            if msg_from_api.text == 'finish':
                flash("Adding kernel finished", 'success')
            else:
                flash(msg_from_api.text, 'error')

            time.sleep(1)
            return redirect(url_for('main_bp.main_kernels'))
        else:
            flash(msg, 'error')

        time.sleep(1)
    else:
        if form.errors:
            flash('Please provide valid inputs', 'error')


    return render_template('add_kernel.html', form=form, rules_json = rules_json)

#modal for showing logs, uses API-Server
@main_bp.route('/cluster/logs/<string:application_id>', methods=['GET', 'POST'])
def show_logs(application_id):

    logs = requests.get(api_adress + '/logs?application_id=' + application_id, timeout=8)

    return render_template('show_logs.html', logs=logs.text)


#modal for chaning resoucre, uses API-Server
@main_bp.route('/kernels/<string:folder>/modify/<string:driver_mem>/<string:num_exec>/<string:exec_mem>/<string:exec_cores>', methods=['GET', 'POST'])
def modify_resources(folder, driver_mem, num_exec, exec_mem, exec_cores):

    form = NewFormModifyRessources()


    if form.validate_on_submit():
        test = request.form.to_dict()
        status, msg = util.check_with_json(test['modifyRessources-driverMemory'],
                                           test['modifyRessources-numExecutors'],
                                           test['modifyRessources-executorMemory'],
                                           test['modifyRessources-executorCores'])

        if status:
            flash(msg, 'success')
            test['modifyRessources-folder'] = folder
            requests.post(api_adress + "/modify_kernel_specs", data=test)
            time.sleep(1)
            return redirect(url_for('main_bp.main_kernels'))
        else:
            flash(msg)

        time.sleep(1)
    else:
        if form.errors:
            flash('Please provide valid inputs', 'error')
            logger.debug("m resources 1")
        logger.debug("m resources 2")


    return render_template('modify_resources.html',form=form,
                           num_exec=num_exec,
                           driver_mem=driver_mem,
                           exec_mem=exec_mem,
                           exec_cores=exec_cores)


#the admin view, for chaning user limits
#uses API-Server for accessing the JEG config file (amout of allowed notebooks)
@main_bp.route('/admin', methods=['GET', 'POST'])
@login_required(username='Admin')
def admin_view():

    #YARN specs needed to check whether admins limits dont exceed acutal cluster limits
    cluster_info_filtred, cluster_scheduler_filtred, \
    cluster_metrics_filtred, cluster_nodes_filtred, cluster_all_apps_filtred = util.get_cluster_info(yarn_api_adress)

    form = NewFormClusterRules()

    with open('./cluster-rules/cluster_rules.json', 'r') as f:
        rules_json = json.load(f)

    if form.validate_on_submit():

        rules = request.form.to_dict()

        if 'allow_users' not in rules:
            rules['allow_users'] = 'False'
        else:
            rules['allow_users'] = 'True'


        status, msg = util.check_with_yarn(rules, cluster_metrics_filtred['totalNodes'], (int(cluster_nodes_filtred[0][3])+int(cluster_nodes_filtred[0][4])),
                                           (int(cluster_nodes_filtred[0][5])+int(cluster_nodes_filtred[0][6])))
        if status == True:
            status_write_to_json = util.write_rules_to_json(rules)

            flash(msg, 'success')
            requests.post(api_adress + "/update_cluster_rules", data=rules)
            time.sleep(3)
            return redirect(url_for('main_bp.admin_view'))

        flash(msg)


    else:
        if form.errors:
            flash('Please provide valid inputs', 'error')


    return render_template('admin_view.html', form=form,
                                            rules_json=rules_json)

#modal for deleting a kernek, uses API-Server
@main_bp.route('/kernels/<string:folder>/delete_kernel', methods=['GET', 'POST'])
def delete_kernel(folder):
    form = NewForm()

    to_send = {'folder':folder}
    logger.debug(to_send)

    if request.method == 'POST':
        requests.post(api_adress + "/delete_kernel", data=to_send)
        flash('Deleting done...', 'success')

        return redirect(url_for('main_bp.cluster'))


    return render_template('delete_kernel.html',form=form,
                           folder=folder)

#modal for killing an application, uses API-Server
@main_bp.route('/cluster/kill_application/<string:application_id>', methods=['GET', 'POST'])
def kill_application(application_id):
    form = NewForm()

    to_send = {'application_id': application_id}
    logger.debug(to_send)

    if request.method == 'POST':
        requests.post(api_adress + "/kill_application", data=to_send)



    return render_template('kill_application.html',form=form,
                           application_id=application_id)
