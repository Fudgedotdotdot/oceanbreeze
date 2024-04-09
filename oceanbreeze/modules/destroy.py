from pathlib import Path
import shutil
import json

from rich.prompt import Confirm

from oceanbreeze.lib import helpers
from oceanbreeze.config import config



def destroy_infra():
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
        helpers.run_command(f"terraform apply -destroy -auto-approve -var 'project_name={config.project}' -var 'sshkey={config.terra_sshkey}' -var 'domain_name={config.phishdomain}'")
        helpers.terra_workspace("select", "default")
        helpers.terra_workspace("delete", config.phishdomain)
    else:
        config.rc.warning("Didn't deploy the state")


def destroy():
    """
    Entry point function for the destroy action
    """
    if helpers.terra_check_workspace(config.phishdomain):
        helpers.terra_workspace("select", config.phishdomain)
    else:
        config.rc.warning("Domain doesn't exist")
        exit()
    destroy_infra()

    # ensure that we are in the default workspace
    helpers.terra_workspace("select", "default")