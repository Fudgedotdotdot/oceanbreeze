from pathlib import Path
import shutil
import json
import datetime

from rich.prompt import Confirm

from oceanbreeze.lib import helpers
from oceanbreeze.config import config



def configure_infra() -> str:
    """
    Configuring the terraform deployed infra with ansible
    Returns the IP of the instance for convenience
    """
    ip = helpers.terra_getIP()
    with config.rc.status(f"[bold green]Waiting for SSH on {ip}", spinner_style="green") as x:
            helpers.check_port(ip)
    path_caddy = helpers.generate_caddy_file()
    config.rc.info("Running ansible to configure the droplet")
    helpers.run_command(f"ansible-playbook -u root -i '{ip},' --private-key {config.local_sshkey} --extra-vars \"fake_website={config.website} domain_name={config.phishdomain}\" main.yml")

    Path.unlink(path_caddy)
    return ip


def deploy_infra() -> None:
    """
    Deploying infrastructure with terraform
    """
    terraform_outfile = config.path_terra / f"{config.phishdomain}-terraform-plan"   
    helpers.run_command(f"terraform plan -out={terraform_outfile} -var 'project_name={config.project}' -var 'sshkey={config.terra_sshkey}' -var 'domain_name={config.phishdomain}'")
    
    deploy_ok = Confirm.ask("[dark_orange]\[?][/dark_orange] Are OK with the proposed state ?")
    if deploy_ok:
        helpers.run_command(f"terraform apply -auto-approve \"{terraform_outfile}\"")
        helpers.cleanup(terraform_outfile, approve=True)
    else:
        helpers.cleanup(terraform_outfile, approve=False)
        config.rc.warning("Didn't deploy the state")
        exit()
        

def deploy():
    """
    Entry point function for the deploy action
    """

    if not (config.path_webserver / "template_website" / config.website).is_dir():
        config.rc.warning(f"Website template [bold purple]{config.website}[/bold purple] is not a valid template")
        exit()
        
    config.rc.info(f"Deploying infra for [bold dodger_blue1]{config.phishdomain}[/bold dodger_blue1] with [bold purple]{config.website}[/bold purple] template")
    helpers.terra_workspace("select", "default")
    if helpers.terra_check_workspace(config.phishdomain):
        helpers.terra_workspace("select", f"{config.phishdomain}")
    else:
        helpers.terra_workspace("new", f"{config.phishdomain}")
    
    deploy_infra()
    #ip = configure_infra()
    ip = helpers.terra_getIP()
    helpers.update_configfile(ip)

    # # at the end, make sure to switch back to the neutral workspace
    helpers.terra_workspace("select", "default")