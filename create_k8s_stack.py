### Script created by Anton Prylypa for the course created by Sander Van Vugt
### Certified Kubernetes Administrator
### initialization kubernetes lab cluster
### 1 master node and 3 worker nodes
### Usage:
### Run from the user which have aws cli access to the cloudformation. Please Google for configure it.
### $ python3 create_k8s_stack.py
### enter your stack name (can be anything what you want) and enter path to the CF script if you have another
### or enter ./k8s-stack.yml
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

### config section ###
## public ips keys 
public_ip_keys = ["PublicIpMasterA", "PublicIpWorkerA", "PublicIpWorkerB", "PublicIpWorkerC"]
### end of config section ###

def create_stack(stack_name, template_path):
    os.system('aws cloudformation create-stack \
                --stack-name {0} \
                --template-body file://{1}'.format(stack_name, template_path))


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


def run_playbooks():
    os.system('cd ansible && ansible-playbook install_environment.yml')


def main():
    stack_name = input('Enter the stack name: ')
    template_path = input('Enter the template full path: ')

    outputs = get_outputs_values(stack_name, values=public_ip_keys)
    create_ansible_host_file(outputs)
    run_playbooks()


if __name__ == '__main__':
    main()