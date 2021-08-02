#!/bin/bash
# script that runs 
# https://kubernetes.io/docs/setup/production-environment/container-runtime

sudo yum update -y && sudo yum upgrade -y
sudo amazon-linux-extras install docker -y
sudo usermod -a -G docker ec2-user


#yum install -y docker-ce
[ ! -d /etc/docker ] && mkdir /etc/docker

cat > /etc/docker/daemon.json <<EOF
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m"
  },
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ]
}
EOF

mkdir -p /etc/systemd/system/docker.service.d

systemctl daemon-reload
systemctl restart docker
systemctl enable docker