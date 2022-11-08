#!/usr/bin/env python3

time_difference = 2 # length in minutes of the log search - I intend to run this as a cron job every 2 minutes, so only want to looks at the previous 2 minutes worth of logs
palo_ips = ["10.0.0.1","10.0.0.2"] #both IP's from your HA pair (can also be hostnames)
meraki_org_id = ""
meraki_network_ids=[''] # The network ID(s) of your Meraki VPN Hub
# Better to define these API keys as environment variables, for security reasons - if left blank, the script will get environment variables of the same name
palo_api_key = ""
meraki_api_key = ""

#---------------------------------------------------------------------------------------------------------------------------#
import meraki, requests, xmltodict, os
from datetime import datetime, timedelta

# Get environment variables
if palo_api_key == '':
    palo_api_key = os.getenv('palo_api_key')
if meraki_api_key == '':
    meraki_api_key = os.getenv('meraki_api_key')

# Get the time for the filter in the query
date = datetime.today() - timedelta(minutes=time_difference)
date = datetime.strftime(date, '%Y/%m/%d %H:%M:%S')

# Make initial request for logs
ha_member = 0
palo_url = f"https://{palo_ips[ha_member]}/api/?key={palo_api_key}&type=log&log-type=system&query=(receive_time geq '{date}') and (subtype eq ha) and (eventid eq state-change)"
try:
    ha_query = requests.get(palo_url, verify=False, timeout=5)
except:
    try:
        ha_member = 1
        palo_url = f"https://{palo_ips[ha_member]}/api/?key={palo_api_key}&type=log&log-type=system&query=(receive_time geq '{date}') and (subtype eq ha) and (eventid eq state-change)"
        ha_query = requests.get(palo_url, verify=False, timeout=5)
    except:
        print('Failed to reach firewalls')
        exit()
# If results aren't returned instantly, request the job results TODO: sort method for if the job still isn't complete after the second request
ha_query = xmltodict.parse(ha_query.content, dict_constructor=dict)
ha_query = ha_query['response']['result']['job']
try:
    int(ha_query)
    job_url = f"https://{palo_ips[ha_member]}/api/?key={palo_api_key}&type=log&action=get&job-id={ha_query}"
    job = requests.get(job_url, verify=False, timeout=5)
    job = xmltodict.parse(job.content, dict_constructor=dict)
except:
    job = ha_query

# Get the network ID's and uplink Ips of the affected networks from Meraki
if job['response']['result']['log']['logs']['@count'] != '0':
    dashboard = meraki.DashboardAPI(meraki_api_key, suppress_logging=True)
    vpn_status = dashboard.appliance.getOrganizationApplianceVpnStatuses(meraki_org_id, total_pages='all', networkIds=[meraki_network_ids])
    unreachable = []
    for network in vpn_status:
        for network_ID in network['merakiVpnPeers']:
            if network_ID['reachability'] == 'unreachable':
                unreachable.append(network_ID['networkId'])
    uplinks = dashboard.appliance.getOrganizationApplianceUplinkStatuses(meraki_org_id, total_pages='all', networkIds=[unreachable])
    affected_ips = []
    for network in uplinks:
        for uplink in network['uplinks']:
            if uplink['status'] == 'active':
                affected_ips.append(uplink['publicIp'])
# Clear the relevant sessions on the Palo's
    for ip in affected_ips:
        clear_url = f"https://{palo_ips[ha_member]}/api/?type=op&cmd=<clear><session><all><filter><destination>{ip}</destination></filter></all></session></clear>&key={palo_api_key}"
        try:
            requests.post(clear_url, verify=False, timeout=5)
        except:
            print("session clear failed")
            exit()
    print("sessions cleared")
else:
    print('No HA failover events found')
    exit()