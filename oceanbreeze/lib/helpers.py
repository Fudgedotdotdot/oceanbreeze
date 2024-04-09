import subprocess
import time
import socket
from pathlib import Path
import re
import json

from oceanbreeze.config import config



def run_command(cmd: str, return_output=False):
    """
    Helper fonction to run terraform and ansible commands
    """
    if cmd.startswith('terraform workspace'):
        style = config.color_default
        cwd = config.path_terra
        cmd = "TF_CLI_ARGS=\"-no-color\" " + cmd # remove terraform's colors
    elif cmd.startswith('terraform') :
        style = config.color_terra
        cwd = config.path_terra
        cmd = "TF_CLI_ARGS=\"-no-color\" " + cmd # remove terraform's colors
    elif cmd.startswith('ansible'):
        style = config.color_ansible
        cwd = config.path_ansible
    else:
        style = config.color_default
        cwd = "."

    try:
        if return_output:
            return subprocess.run(cmd, cwd=cwd, shell=True, text=True, check=True, stdout=subprocess.PIPE).stdout
        else:
            with subprocess.Popen(cmd, cwd=cwd, shell=True, text=True, stdout=subprocess.PIPE, bufsize=1) as p:
                for line in p.stdout:
                    config.rc.print(line, end='', style=style, highlight=False)
                p.communicate() # sets the returncode
                if p.returncode != 0:
                    raise subprocess.CalledProcessError(p.returncode, cmd)
    except subprocess.CalledProcessError as e: 
        config.rc.print(e)
        if cmd.startswith('ansible'):
            config.rc.info(f"You can run the playbook manually with :  {cmd}")
        exit()


def terra_check_workspace(workspace: str) -> bool:
    """
    Checks if workspace already exists (ie: canceled ansible, but terraform has a state for a workspace)
    Returns True is exist, False if not
    """
    if workspace in terra_list_workspace():
        return True
    else:
        return False


def terra_list_workspace() -> list[str]:
    """
    Lists the workspaces created by terraform
    Returns a list of workspaces
    """
    workspace_dir = config.path_terra / "terraform.tfstate.d/"
    return [x.parts[-1] for x in Path(workspace_dir).glob("*")]



def terra_state() -> list[dict]:
    """
    Prints the terraform state sort of like the real terraform show command
    Returns a list of all the resources deployed in the state
    """
    managed_rsrc = []
    state = json.loads(run_command("terraform state pull", return_output=True))
    for rsrc in state['resources']:
        if rsrc['mode'] == "managed":
            managed_rsrc.append(rsrc)
    
    return managed_rsrc


def terra_workspace(*args) -> None:
    """
    Helper fonction to manage terraform workspaces
    """
    need_args = ["delete", "select", "new"]
    if args[0] in need_args:
        if len(args) != 2:
            exit(f"invalid {args[0]} command: {args}")
    if "show" in args[0]:
        run_command(f"terraform workspace show")
    if "list" in args[0]:
        run_command(f"terraform workspace list")
    elif "select" in args[0]:
        run_command(f"terraform workspace select {args[1]}")        
    elif "delete" in args[0]:
        run_command(f"terraform workspace delete {args[1]}")   
    elif "new" in args[0]:
        run_command(f"terraform workspace new {args[1]}") 
    else:
        print(f"unknown command: {args[0]}")


def generate_caddy_file() -> Path:
    config.rc.debug("Writing caddy file...", higlight=False)
    with open(config.path_webserver / "caddy/Caddyfile.template", "r") as f:
        tmp_caddy = f.read()
        
    tmp_caddy = re.sub("DOMAIN", f"{config.phishdomain}", tmp_caddy)
    path_caddy = config.path_webserver / "caddy/Caddyfile"
    with open(path_caddy, "w") as f:
        f.write(tmp_caddy)

    return path_caddy


def check_port(ip: str) -> None:
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        try:
            s.connect((ip, 22))
            s.close()
            break
        except:
            time.sleep(5)


def resolve_domain(domain: str, ip: str) -> None:
    while True:
        try:
            domain_ip = socket.gethostbyname(domain)
            if domain_ip == ip:
                break
        except socket.gaierror:
            time.sleep(30)


