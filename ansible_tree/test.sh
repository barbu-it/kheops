

python  ./ansible_tree/cli.py

$APP lookup profiles -e

lookup profiles  -e "hostgroup=[ 'Tiger/ICN/Tiger/Infra/Prod' ]" -e "hostgroups=[ 'Tiger', 'Tiger/ICN', 'Tiger/ICN/Tiger', 'Tiger/ICN/Tiger/Infra', 'Tiger/ICN/Tiger/Infra/Prod' ]" -e "ansible_fqdn=tiger-ops.it.ms.bell.ca" -e "ansible_dist_name=Rhel" -e "ansible_dist_version=8" -e "tiger_org=ICN"





 -e "hostgroup=[ 'Tiger/ICN/Tiger/Infra/Prod' ]"
 -e "hostgroup=[ 'Tiger/ICN/Tiger/Infra/Prod' ]"
 -e "hostgroup=[ 'Tiger/ICN/Tiger/Infra/Prod' ]"
 -e "hostgroups=[ 'Tiger', 'ICN', 'Tiger', 'Infra', 'Prod' ]"
