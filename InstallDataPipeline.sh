#!/bin/bash --login

#Intended for standard Amazon Linux AMI. Installs Data Pipeline CLI tools.

# Install RVM
\curl -sSL https://get.rvm.io | bash -s stable

# Reload login scripts
source /home/ec2-user/.profile 
echo '[[ -s "$HOME/.rvm/scripts/rvm" ]] && source "$HOME/.rvm/scripts/rvm"' >> /home/ec2-user/.bashrc

# Install ruby 1.9.3
rvm install 1.9.3 

# Get credentials
echo "Provide AWS Access Key, followed by [ENTER]:"
read access

echo "Provide AWS Secret Key, followed by [ENTER]:"
read secret

# Activate New ruby version
rvm use 1.9.3

# Install Ruby Gems
wget http://rubyforge.org/frs/download.php/76729/rubygems-1.8.25.tgz
tar -xzvf rubygems-1.8.25.tgz
sudo ruby ./rubygems-1.8.25/setup.rb

# Install Gems
gem install uuidtools json httparty bigdecimal nokogiri

# Download EDP CLI
wget https://s3.amazonaws.com/datapipeline-us-east-1/software/latest/DataPipelineCLI/datapipeline-cli.zip 

# Extract EDP CLI
unzip datapipeline-cli.zip 

#(insert credentials)
echo '{
  "access-id": "'$access'",
  "private-key": "'$secret'"
}' > /home/ec2-user/credentials.json 

echo "Testing Data Pipeline CLI..."
./datapipeline-cli/datapipeline --list-pipelines
