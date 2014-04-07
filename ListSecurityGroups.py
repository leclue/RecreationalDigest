#!/usr/bin/python
import sys
import os
import boto
import boto.ec2
import boto.vpc

regions_available = ["ap-northeast-1", "ap-southeast-1", "ap-southeast-2", "eu-west-1", "sa-east-1", "us-east-1", "us-west-1", "us-west-2"]

for thisregion in regions_available:
  c = boto.vpc.connect_to_region(thisregion)
  vpc = c.get_all_vpcs(filters=None, dry_run=False)

  for thisvpc in vpc:
    print "Listing security groups for VPC " + thisvpc.id + " in " + thisregion
    sgs = c.get_all_security_groups(filters={'vpc-id': thisvpc.id})
    for thissg in sgs:
      print thissg.id
