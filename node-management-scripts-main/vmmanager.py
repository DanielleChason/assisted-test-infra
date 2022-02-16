import os

from flask import Flask
from flask import request, redirect
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import subprocess
import re
import validators

# A simple web ui which allows users easily create nodes for https://github.com/openshift-assisted/assisted-ui-lib
# for testing purposes. The intended audience are UX designers/researchers which need to be able to go over the whole
# flow easily but the resulting cluster is not meant to be actually used.

# dependencies:
# pip install flask
# pip install Flask-HTTPAuth

app = Flask(__name__)
auth = HTTPBasicAuth()

os.chdir("/home/dchason/projects/assisted-test-infra")

users = {
}


def init_users():
    with open("node-management-scripts-main/users", "r") as usersfile:
        users_and_pass = usersfile.readlines()
        for user_and_pass in users_and_pass:
            (user, password) = user_and_pass.strip().split('=')
            users[user] = password


init_users()


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@app.route('/logout', methods=['GET'])
def logout():
    return redirect(f'http://.:.@{request.host}')


@app.route('/', methods=['GET', 'POST'])
@auth.login_required
def create_vms():
    def get_running_vms():
        vm_list = subprocess.check_output(['node-management-scripts-main/host_scripts/get_running_vms.sh']).decode(
            "utf-8").strip().split()
        return f'{len(vm_list)} VMs running. <a href="/manage">Manage</a>'

    def get_status():
        wget = subprocess.check_output(
            ['node-management-scripts-main/host_scripts/get_running_process_count.sh', 'wget']).decode("utf-8").strip()
        virt_install = subprocess.check_output(
            ['node-management-scripts-main/host_scripts/get_running_process_count.sh', 'virt-install']).decode(
            "utf-8").strip()

        if wget != "2":
            return "<div>An image is being downloaded</div>"
        elif virt_install != "2":
            return "<div>The VM(s) are being created</div> <br/>"
        return ""

    def start_vms_on_background(cluster_id, num_of_masters, num_of_workers, pull_secret):
        # subprocess.check_output("make deploy_nodes",
        #                         env={'CLUSTER_ID': cluster_id, 'NUM_MASTERS': num_of_masters,
        #                              'NUM_WORKERS': num_of_workers, 'PULL_SECRET': pull_secret})
        subprocess.Popen(['make', 'deploy_nodes'], shell=True, env={'CLUSTER_ID': cluster_id, 'NUM_MASTERS': num_of_masters,
                                                     'NUM_WORKERS': num_of_workers, 'PULL_SECRET': pull_secret}, executable='/bin/bash')

    refresher = """
        <head>
            <title>Node Creator 4000</title>
            <meta http-equiv="refresh" content="5">
        </head>
    """

    title = """
        <head>
            <title>Node Creator 4000</title>
        </head>
    """

    dont_resubmit = """
        <script>
        if ( window.history.replaceState ) {
            window.history.replaceState( null, null, window.location.href );
        }
        </script>
    """

    submit_form = """
        <div>
            <form action="/" method="post" id="vm_create_form">
                <label for="clusterid">Paste the cluster ID from the url</label>
                <br />
                <textarea id="clusterid" name="clusterid" rows="4" cols="150"></textarea>
                <br />
                <label for="pullsecret">enter pull secret </label>
                <br />
                <textarea id="pullsecret" name="pullsecret" rows="4" cols="150"></textarea>
                <br />
                <label for="numofmasters">Number of control plane nodes you want to create</label>
                <br />
                <input type="text" id="numofmasters" name="numofmasters" value="3">
                <br />
                <label for="numofworkers">Number of workers you want to create</label>
                <br />
                <input type="text" id="numofworkers" name="numofworkers" value="">

            </form>
            <button type="submit" form="vm_create_form" value="Submit">Submit</button>
        <div>
        <br />
    """

    logout_button = """
        <br/ ><a href="/logout">logout</a>
    """

    vm_create_screen = title + submit_form + get_running_vms() + logout_button

    status = get_status()
    in_progress_message = "Host creation in progress. Please wait until the process finished before submitting a next " \
                          "request. Current status: " + status

    if status != "":
        vm_create_screen = in_progress_message + refresher + logout_button
    if request.method == 'POST':
        if get_status() != "":
            return in_progress_message + logout_button + dont_resubmit + refresher

        num_of_masters = request.form['numofmasters'].strip()
        if num_of_masters == "":
            num_of_masters = "3"
        elif not num_of_masters.isnumeric():
            return "The number of nodes have to be a number" + dont_resubmit + title

        cluster_id = request.form['clusterid']
        cluster_id = cluster_id.strip()

        pull_secret = request.form['pullsecret'];

        num_of_workers = request.form['numofworkers']

        start_vms_on_background(cluster_id, num_of_masters, num_of_workers, pull_secret)
        return "<div>The host creation has been submitted. The hosts should start showing up in the wizard in few " \
               "minutes</div><br /> Current status: " + get_status() + dont_resubmit + refresher
    else:
        return vm_create_screen


@app.route('/manage', methods=['GET', 'POST'])
@auth.login_required
def manage_vms():
    def delete_vms_on_background(vms):
        subprocess.run(['node-management-scripts-main/host_scripts/delete_vms.sh'] + vms)

    def get_running_vms():
        form_header = """
            <form action="/manage" method="post" id="vm_delete_form">
        """
        form_footer = """
            <br /> <button type="submit" form="vm_delete_form" value="Submit">Delete selected VMs</button>
        </form>
        """

        vm_list = subprocess.check_output(['node-management-scripts-main/host_scripts/get_running_vms.sh']).decode(
            "utf-8").strip().split()
        vm_checkboxes = [f'<input type="checkbox" id="{vm}" name="vmname" value="{vm}"><label for="{vm}">{vm}</label>'
                         for vm in vm_list]
        vms_joined = "<br />".join(vm_checkboxes)

        return form_header + vms_joined + form_footer

    back_button = """
        <br/ ><a href="/">Back</a> to vm creation form
    """

    if request.method == 'POST':
        vm_list = request.form.getlist('vmname')
        if len(vm_list) > 0:
            delete_vms_on_background(vm_list)

    return get_running_vms() + back_button

# if __name__ == '__main__':
#    app.run("0.0.0.0", 5001)
