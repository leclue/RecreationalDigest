#!/bin/bash

# This script will configure an Ubuntu instance in AWS as a master instance for "Bees With Machine Guns"
# Recommended for use with "ami-35dbde5c" in US-EAST-1

# Update our repositories
sudo apt-get update

# Install dependent packages
sudo apt-get install build-essential python-pip python-dev --assume-yes

# Install "Bees With Machine Guns"
sudo pip install beeswithmachineguns

# Get Keypair Name
keypair=`curl -s http://169.254.169.254/latest/meta-data/public-keys/`
keypairname=`echo $keypair | awk -F "=" '{print $2}'`

# Get credentials
echo "Provide AWS Access Key, followed by [ENTER]:"
read access

echo "Provide AWS Secret Key, followed by [ENTER]:"
read secret

# Get Keypair Contents and create PEM file
echo "Paste the contents of the AWS Key-Pair $keypairname PEM file, and hit ENTER then CTRL-D when done:"
while read LINE
do
	echo $LINE >> ./.ssh/$keypairname.pem
	if [ "$LINE" = "^A" ];then
		break
	fi
done

chmod 0600 ./.ssh/$keypairname.pem

# insert credentials into .boto file
echo '[Credentials]
AWS_ACCESS_KEY_ID='$access'
AWS_SECRET_ACCESS_KEY='$secret > ./.boto

# Get security group name associated with this instance
securitygroup=`curl -s http://169.254.169.254/latest/meta-data/security-groups`

echo "Bees With Machine Guns has been installed and is ready to use..."
echo -e "Start bees using below syntax:\n\tbees up -s<amount of nodes> -g <security group name> -k <key-pair name>\ne.g."
echo "bees up -s2 -g $securitygroup -k $keypairname"
echo "Run \"bees -h\" for more info!"
