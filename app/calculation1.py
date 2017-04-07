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
import json
import affi
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

def calculation(start,end):	
  startdate = start.strftime('%m/%d/%Y')
  enddate = end.strftime('%m/%d/%Y')
  startdate = datetime.datetime.strptime(startdate, "%m/%d/%Y")
  enddate = datetime.datetime.strptime(enddate, "%m/%d/%Y") 
  tenants = keystone.tenants.list() 
  t_dict = {}

  # Get The mapping of tenant_ids to tenant_names
  for tenant in tenants:
      t_dict[tenant.id] = tenant.name
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

  #Get the affiliations for each tenant usage  and store them according to the affiliations.
  usage_objects = nova.usage.list(start=startdate, end=enddate+datetime.timedelta(days=1), detailed=True)
  usages = [x.to_dict() for x in usage_objects]
  affi_dict = affi.affi
  affiliations = set()
  affiliations1 = set()
  for tenant in tenants:
    try:
      t_name=t_dict[tenant.id]
      affiliations.add(affi_dict[t_name])
      affiliations1.add(affi_dict[t_name])
    except KeyError:
      continue

  #print affiliations
  affi_tenants = {}
  alltenants = {}

  for i in range(len(affiliations)):
      affi_tenants[affiliations.pop()] = []
      alltenants[affiliations1.pop()] = set()

  for usage in usages:
      try:
          for key in affi_tenants.viewkeys():
              if key == affi_dict[t_dict[usage['tenant_id']]]:
                  affi_tenants[key].append(usage)

      except KeyError:
          continue

  #Get the list of all tenants from keystone based on the university to sort out the the list of non-usage tenants.
  for tenant in tenants:
      tenant_name = t_dict[tenant.id]
      for key in affi_dict.viewkeys():
          if tenant_name == key:
               alltenants[affi_dict[key]].add(tenant_name)

  FORMATTER = "{tenant},{Diskvalue},{Memoryvalue},{CPUvalue},{Users}"
  resource_names = ['DiskGB','Memoryvalue','CPUvalue']
  #resource_values = []
  timedelta = 1
  total = {}
  sizes = []
  results1 = {}
  tenants_with_usage = {}
  total_Diskvalue = 0
  total_Memoryvalue = 0
  total_CPUvalue = 0
  total_Users = 0
  no_users ={}
  for category in affi_tenants.viewkeys():
      tenants_with_usage[category] = set()
      total[category] = [0,0,0]
      for usage in affi_tenants[category]:
          try:
              tenant_name = t_dict[usage['tenant_id']]
          except KeyError:
              continue
          tenants_with_usage[category].add(tenant_name)
          tenant_name = tenant_name.replace(" ", "-").replace(".","_")
          images=0
          volumes=0
          ips=0
          reqkey=t_dict[usage['tenant_id']]
          for key in results.viewkeys():
              if key == reqkey:
                  images = results[key][0]
                  volumes = results[key][1]
                  ips = results[key][2]
          resource_values = [usage['total_local_gb_usage'],usage['total_memory_mb_usage'],usage['total_vcpus_usage']]
          total[category][0] += resource_values[0]
          total[category][1] += resource_values[1]
          total[category][2] += resource_values[2]

      results1[category] = dict(Diskvalue = total[category][0], Memoryvalue = total[category][1], CPUvalue = total[category][2], Projects = len(affi_tenants[category]))

      #Calculate the sum of resources used by the keystone projects.     
      total_Diskvalue += total[category][0]
      total_Memoryvalue += total[category][1]
      total_CPUvalue += total[category][2]
      total_Users += len(affi_tenants[category])

      #results1['Total'] = dict(Diskvalue = total_Diskvalue, Memoryvalue = total_Memoryvalue, CPUvalue = total_CPUvalue, Users = total_Users)    
      sizes.append(total[category])
 
      tenant_without_usage_raw = alltenants[category].difference(tenants_with_usage[category])
  results1['Aggregation_Affiliations'] = dict(Diskvalue = total_Diskvalue, Memoryvalue = total_Memoryvalue, CPUvalue = total_CPUvalue, Projects = total_Users)
  return results1
