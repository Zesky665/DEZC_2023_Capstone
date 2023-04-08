apt-get update

apt-get install apt-utils

apt-get -y install libpq-dev python3-dev

apt-get -y install build-essential

apt-get -y install postgresql-server-dev-all

apt-get -y remove git-core

apt-get -y autoremove

apt-get -y install git-core
apt-get -y install curl
apt-get -y install sudo
apt-get -y install zip
apt-get -y install unzip
apt-get -y install python3
apt-get -y install awscli

echo 'export PATH=$PATH:~/.local/bin' >>~/.bashrc

echo 'alias aws="awsv2"' >>~/.bashrc

