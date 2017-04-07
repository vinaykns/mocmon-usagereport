import keystonerc_admin
import keystoneauth1.identity
import keystoneauth1.session
import os
import sys
import novaclient.client
import keystoneclient.v2_0.client
import neutronclient.v2_0.client
import  glanceclient
from cinderclient import client
import datetime
import subprocess
import json
import affi
import calculation
import pdb

username=keystonerc_admin.OS_USERNAME
password=keystonerc_admin.OS_PASSWORD
tenant_name=keystonerc_admin.OS_TENANT_NAME
auth_url=keystonerc_admin.OS_AUTH_URL
auth = keystoneauth1.identity.v2.Password(username=username, password=password, tenant_name=tenant_name, 
                                          auth_url=auth_url)
session = keystoneauth1.session.Session(auth=auth)
nova = novaclient.client.Client('2',session=session)
keystone = keystoneclient.v2_0.client.Client(session=session)
glance = glanceclient.Client('2', session=session)
cinder = client.Client('2', username , password , tenant_name , auth_url)
neutron = neutronclient.v2_0.client.Client(session=session)  

def evaluation(self):	
  tname_dict = {}
  tname = set()
  tenants = keystone.tenants.list()
  t_dict = {}

  # Get The mapping of tenant_ids to tenant_names
  for tenant in tenants:
      t_dict[tenant.id] = tenant.name
      tname_dict[tenant.name] = tenant.id
      tname.add(tenant.name)
      all_1hour=[0,0,0,0,0,0]

  #Default give the image and volumes values as zero for all tenants.
  results = {}
  for tenant_name in t_dict.values():
      results[tenant_name] = [0, 0, 0]

  #Get the list of images for the tenants
  g = glance.images.list()
  for i in g:
    try:
      results[t_dict[i['owner']]][0] += 1
    except:
      pass

  #Get the list of volumes for the tenants
  volumes = cinder.volumes.list(search_opts = {'all_tenants': 1})
  for i in range(len(volumes)):
    try:
      conversion = volumes[i].to_dict()
      con = conversion['os-vol-tenant-attr:tenant_id']
      results[t_dict[con.encode('ascii','ignore')]][1] +=1
    except:
      pass

  #Get the list of floating ip's for all the tenants
  floatings = neutron.list_floatingips().values()[0]
  for fl in floatings:
    try:
      results[t_dict[fl['tenant_id']]][2] +=1
    except KeyError:
      continue
 

  # Collect the total list of users.
  total_users = set()
  users = keystone.users.list()

  for user in users:
    #try:
      extracted = user.to_dict() 
      total_users.add(extracted['name'])

  
  #Initialize the dictionary for each user.
  user_projects = {}

  for user in total_users: 
    user_projects[user] = {}
               
  #Store the projects for corresponding users.
  for tenant in tenants:
    #try:
      raw_user = keystone.users.list(tenant.id)
      if len(raw_user) == 1:

        user = raw_user[0].to_dict()

        user_projects[user['username']][tenant.id] = tenant.name

      elif len(raw_user) > 1:
        for index in range(len(raw_user)):
          user = raw_user[index].to_dict()

          user_projects[user['name']][tenant.id] = tenant.name

  
  #Add the user to the affiliation based on the projects he is involved.
  affi_dict = affi.affi
  results_affi={}
  aff = set()
  for tenant in tenants:
    try:
      t_name = tenant.name
      aff.add(affi_dict[t_name])
    except KeyError:
      print "Update the affiliations file"
      pdb.set_trace()
      continue  

  for affiliation in aff:
    results_affi[affiliation] = set()
  
  for user,projects in user_projects.viewitems():
    for t_id,t_name in projects.viewitems():
      try:
        if (t_name !="False"):  
          affiliation = affi_dict[t_name]
          results_affi[affiliation].add(user)  
        elif (t_name == "False"):
          print "These projects doesn't have keystone authentication"
          print t_id 
      except KeyError:
        print "Update the affiliation file"
        continue 

  return results_affi
    
