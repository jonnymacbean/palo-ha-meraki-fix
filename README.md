# palo-ha-meraki-fix
Script to fix Meraki auto VPNs after a PAN-OS failover event

This is a quick and dirty script and I am a novice coder, so don't rely on this script for anything critical. Any constructive feedback welcome.

-----------------------------------------------------------------------
To run, edit the variables above the line in the script:

**time_difference**: integer in minutes of how far back you want to search the firewall logs for failover events

**palo_ips**: list of strings containing the IPs/Hostnames of the Palo firewall HA pair

**meraki_org_id**: string obtained from the Meraki API, see https://developer.cisco.com/meraki/api-latest/#!getting-started/find-your-organization-i*d

**meraki_network_ids**: list of strings. To get the IDs use the Meraki API, see https://developer.cisco.com/meraki/api-latest/#!getting-started/find-your-network-id
(My environment only had one affected network, so I haven't tested this with multiple network_ids)

**palo_api_key**: string containing your API key for your firewalls. To obtain it see https://docs.paloaltonetworks.com/pan-os/9-1/pan-os-panorama-api/get-started-with-the-pan-os-xml-api/get-your-api-key (if using environment variable, leave blank)

**meraki_api_key**: string containing your API key for the Meraki dashboard. You can generate a new key from your profile in the Meraki dashboard (if using environment variable, leave blank)

------------------------------------------------------------------------


I run this as a cron job every 2 minutes from a Linux server. here's the excerpt from my crontab file:

`*/2 * * * * . /home/<user>/.bash_profile; /<directory>/palo-ha-meraki-fix.py`

Make sure to make the file executable by using chmod +x
