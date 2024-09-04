from pathlib import Path
import json

from rich.prompt import Confirm

from oceanbreeze.lib import helpers
from oceanbreeze.config import config



def configure_infra(ip) -> None:
    """
    Updating the instance with the new domain to be added
    """
    path_caddy = helpers.generate_caddy_file()
    config.rc.info("Running ansible to update the droplet")
    helpers.run_command(f"ansible-playbook -u root -i '{ip},' --private-key {config.local_sshkey} --extra-vars \"fake_website={config.website} domain_name={config.phishdomain}\" update_instance.yml")

    Path.unlink(path_caddy)


def update_infra(ip) -> None:
    """
    Updating an existing instance with a new domain without spawning a new droplet
    """
    terraform_outfile = config.path_terra / f"{config.phishdomain}-terraform-plan"   
    helpers.run_command(f"terraform plan -out={terraform_outfile} -var 'project_name={config.project}' -var 'sshkey={config.terra_sshkey}' -var 'domain_name={config.phishdomain}' -var 'droplet_ip={ip}' -var 'spawn_droplet=0'")
    
    deploy_ok = Confirm.ask("[dark_orange]\[?][/dark_orange] Are OK with the proposed state ?")
    if deploy_ok:
        helpers.run_command(f"terraform apply -auto-approve \"{terraform_outfile}\"")
        helpers.cleanup(terraform_outfile, approve=True)
    else:
        helpers.cleanup(terraform_outfile, approve=False)
        config.rc.warning("Didn't deploy the state")
        exit()
        

def update():
    """
    Entry point function for the update action
    """
    if not (config.path_webserver / "template_website" / config.website).is_dir():
        config.rc.warning(f"Website template [bold purple]{config.website}[/bold purple] is not a valid template")
        exit()
    
    ip = helpers.config_getIP(config.update_domain)
    config.rc.info(f"Adding [bold dodger_blue1]{config.phishdomain}[/bold dodger_blue1] with [bold purple]{config.website}[/bold purple] template to {ip}")
    helpers.terra_workspace("select", "default")
    if helpers.terra_check_workspace(config.phishdomain):
        helpers.terra_workspace("select", f"{config.phishdomain}")
    else:
        helpers.terra_workspace("new", f"{config.phishdomain}")
    
    update_infra(ip)
    configure_infra(ip)
    helpers.update_configfile(ip)
    
    # at the end, make sure to switch back to the neutral workspace
    helpers.terra_workspace("select", "default")



