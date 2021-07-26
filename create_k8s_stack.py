### Script created by Anton Prylypa for the course created by Sander Van Vugt
### Certified Kubernetes Administrator
### initialization kubernetes lab cluster
### 1 master node and 3 worker nodes
### Usage:
### Run from the user which have aws cli access to the cloudformation. Please Google for configure it.
### $ python3 create_k8s_stack.py
### enter your stack name (can be anything what you want) 
###
###
### https://github.com/TonyNihao
### aprylypa@gmail.com
### 
### Thanks for using)

import os
import argparse
import sys
import subprocess
from time import sleep

### config section ###
## public ips keys 
public_ip_keys = ["PublicIpMasterA", "PublicIpWorkerA", "PublicIpWorkerB", "PublicIpWorkerC"]
private_ip_keys = ["PrivateIpMasterA", "PrivateIpWorkerA", "PrivateIpWorkerB", "PrivateIpWorkerC"]
##
## default CF template path
template_path = './k8s_stack.yml'
##
## local domain name
local_domain = 'aprylypa.local'
##
### end of config section ###

def create_stack(stack_name, template_path):
    os.system('aws cloudformation create-stack \
                --stack-name {0} \
                --template-body file://{1}'.format(stack_name, template_path))
    sleep(3)
    run = True
    while run:
        check_completion_command = "aws cloudformation describe-stacks \
                            --stack-name {0} | \
                            jq -r '.Stacks[] | .StackStatus'".format(stack_name)
        check_completion = subprocess.check_output(check_completion_command, text=True, shell=True).replace('\n', '')
        if  check_completion == 'CREATE_IN_PROGRESS':
            print(check_completion)
            print('stack creation in progress wait...')
            sleep(5)
        elif check_completion == 'CREATE_COMPLETE':
            print(check_completion)
            print('stack created successfuly')
            run = False
        else:
            print(check_completion)
            exit(1)

def get_outputs_values(stack_name, values):
    
    outputs_values = {}
    for i in values:    
        describe_command = "aws cloudformation describe-stacks \
                    --stack-name {0} | \
                    jq -r '.Stacks[0].Outputs[] | \
                    select(.OutputKey==\"{1}\") |\
                    .OutputValue'".format(stack_name, i)
        
        ip = subprocess.check_output(describe_command, shell=True, text=True)
        outputs_values[i] = ip.replace('\n','')

    return outputs_values


def create_ansible_host_file(public_ips):
    docker = '[docker]\n'
    master = '[master]\n'
    docker_vars = '[docker:vars]\n'
    f = open('ansible/hosts', 'w')
    # write master group
    f.write(master)
    for key in public_ips:
        if 'Master' in key:
            f.write(key + ' ansible_host=' + public_ips[key] + '\n')
    
    #write docker group
    f.write(docker)
    for key in public_ips:
        f.write(key + ' ansible_host=' + public_ips[key] + '\n')
    

    f.close()


def create_system_hosts_file(private_ips):
    f = open('ansible/files/hosts', 'w')
    local = '127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4 \\n \
             ::1         localhost6 localhost6.localdomain6 \n'
    f.write(local)
    
    for key in private_ips:
        f.write(private_ips[key] + ' {0}.{1}} \n'.format(key.lower().replace('privateip', ''), local_domain))

    f.close()

def run_playbooks():
    os.system('cd ansible && ansible-playbook install_environment.yml')


def main():
    stack_name = input('Enter the stack name: ')

    print('Start create stack')
    create_stack(stack_name=stack_name, template_path=template_path)
    outputs = get_outputs_values(stack_name, values=public_ip_keys)
    private_ips = get_outputs_values(stack_name, values=private_ip_keys)
    create_ansible_host_file(outputs)
    create_system_hosts_file(private_ips)
    run_playbooks()
    print(outputs, private_ips)


if __name__ == '__main__':
    main()