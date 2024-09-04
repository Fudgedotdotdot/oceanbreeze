from pathlib import Path
import shutil
import json

from rich.prompt import Confirm

from oceanbreeze.lib import helpers
from oceanbreeze.config import config



def update_configfile(ip: str, domain: str) -> None:
    """
    Update the configuration file by removing the domain for the terraform state we deleted
    """
    with open(config.configfile, 'r') as f:
        conf = json.load(f)
    config.rc.debug(f"Deleting {domain} from {ip}")
    conf['instances'][ip].remove(domain)
    if len(conf['instances'][ip]) == 0:
        del conf['instances'][ip]
                
    with open(config.configfile, 'w') as f:
        json.dump(conf, f, indent=2)


def destroy_infra(ip: str, domain: str):
    """
    Destroys the selected terraform state. 
    """
    state = helpers.terra_state()
    for rsrc in state:
        config.rc.print(f"# {rsrc['type']}.{rsrc['name']} will be [bold red]destroyed[/bold red]", style="italic")
        config.rc.print(f"resource \"{rsrc['type']}\"", style="italic")
        config.rc.print_json(json.dumps(rsrc['instances'][0]['attributes'])) # there's an terminal injection here, the :droplet: is shown as 💧
        config.rc.print()

    destroy_ok = Confirm.ask("[dark_orange]\[?][/dark_orange] Are OK with the proposed state ? ([bold red]this will auto-approve[bold red])")
    if destroy_ok:
        helpers.run_command(f"terraform apply -destroy -auto-approve -var 'project_name={config.project}' -var 'sshkey={config.terra_sshkey}' -var 'domain_name={domain}'")
        helpers.terra_workspace("select", "default")
        helpers.terra_workspace("delete", domain)
        update_configfile(ip, domain)
    else:
        config.rc.warning("Didn't deploy the state")


def destroy():
    """
    Entry point function for the destroy action
    """
    ip = helpers.config_getIP(config.phishdomain)
    if not ip: config.rc.warning("Domain doesn't exist"); exit()

    linked_domains = config.instances[ip]
    if len(linked_domains) > 1:
        config.rc.warning("Found domains linked to the same instance !")
        destroy_ok = Confirm.ask(f"[dark_orange]\[?][/dark_orange] This will destroy these domains : [bold red]{linked_domains}[/bold red] - Is that what you want ?")
        if not destroy_ok: exit()

    delete_domains = linked_domains if len(linked_domains) > 1 else [config.phishdomain]

    for domain in delete_domains:
        if helpers.terra_check_workspace(domain):
            helpers.terra_workspace("select", domain)
            print(ip, domain)
            destroy_infra(ip, domain)
        else:
            config.rc.warning("Domain doesn't exist")
            exit()


    # # ensure that we are in the default workspace
    helpers.terra_workspace("select", "default")