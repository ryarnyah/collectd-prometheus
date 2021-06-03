# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "geerlingguy/centos7"
  config.vm.box_version = "v1.2.18"

  config.vm.synced_folder ".", "/vagrant", type: "virtualbox", mount_options: ["dmode=775,fmode=500"]
  config.vm.network "private_network", ip: "172.17.177.99"

  config.vm.provision "shell", privileged: true, inline: <<-SHELL
    yum install -y epel-release

    # Collectd installation
    yum install -y python-pip gcc collectd git

    systemctl start collectd
    systemctl enable collectd

    cd /vagrant && pip install .
  SHELL
end
