from pathlib import Path
import json
from dataclasses import dataclass
import subprocess

from oceanbreeze.lib import custom_print, digitalocean

from rich.console import Console
from rich.prompt import Prompt



@dataclass
class Config:
    configfile: Path
    phishdomain: str
    rootdomain: str
    instances: dict
    update_domain: str
    rc: Console
    project: str
    path_terra: Path
    path_ansible: Path
    path_webserver: Path
    local_sshkey: Path
    terra_sshkey: str
    website: str = "socialmedia"
    if_subdomain: bool = False
    color_terra: str = "sky_blue1 italic"
    color_ansible: str = "medium_turquoise italic"
    color_default: str = "grey62 italic"

config = Config # I don't think this is how you initialize a dataclass, but it works so whatever


def init_config(args):
    """
    Inits the config by performing basic checks and then by calling use_config() to finish the configuration
    """
    config.rc = custom_print.CustomPrint()
    if args.debug:
        config.rc.set_log_level(config.rc.DEBUG)  


    config.phishdomain = args.domain_name
    if args.commands != "list":        
        config.rootdomain = '.'.join(config.phishdomain.split('.')[-2:])
        if config.phishdomain != config.rootdomain:
            config.if_subdomain = True
            config.rc.warning("Use the root domain, not a subdomain")
            exit()

    if args.commands == "deploy" or args.commands == "update":
        if args.website:
            config.website = args.website

    if args.commands == "update":
        config.update_domain = args.instance

    config_file = Path.home() / ".config/oceanbreeze/config.json"
    config.configfile = config_file
    
    if config_file.is_file():
        read_config(config_file)
    else:
        create_config(config_file)


def read_config(config_file):
    """
    Reads the configuration file and setup the config dataclass
    """
    config_json = json.loads(config_file.read_text())
    directory = Path(config_json['directory'])

    config.project = config_json['project']
    config.instances = config_json['instances']

    config.terra_sshkey = config_json['sshkey_terra']
    config.local_sshkey = config_json['sshkey_local']

    config.path_terra = directory / "terraform/"
    config.path_ansible = directory / "ansible/"
    config.path_webserver = directory / "webserver/"
    
    config.color_ansible = config_json['color_ansible']
    config.color_terra = config_json['color_terra']
    config.color_default = config_json['color_default']


    config.rc.debug(f"Content of the config file: ")
    if config.rc.log_level == config.rc.DEBUG:
        config.rc.print_json(config_file.read_text())


def create_config(config_file):
    """
    Creates the configuration file and writes it to disk
    """
    config.rc.info(f"First launch detected, creating config file")
            
    directory = Path(Prompt.ask("[dark_orange]\[?][/dark_orange] Enter the directory where this tool is installed")).expanduser()
    while not directory.is_dir():
        directory = Path(Prompt.ask("[dark_orange]\[?][/dark_orange] Not a directory - Enter the directory where this tool is installed")).expanduser()
        
    active_tfstate = directory / "terraform/terraform.tfstate.d/"
    if list(active_tfstate.glob("*")):
       config.rc.warning(f"Found active terraform state, please remove it before changing the configuration (location: {active_tfstate})")
       config.rc.warning("If you deleted the configuration file, you can use [italic]terraform workspace[/italic] and [italic]terraform destroy[/italic] manually to destroy the active state and workspace")
       exit()
    
    config.rc.info("Initializing Terraform")
    terra_init = subprocess.run("terraform init", cwd=directory / "terraform/", shell=True, text=True, check=True, stdout=subprocess.PIPE).stdout
    config.rc.print(terra_init, highlight=False)

    config.rc.info("Fetching projects from DigitalOcean")
    project = digitalocean.get_project(config)
    config.rc.info("Fetching SSH Keys from DigitalOcean")
    do_sshkey = digitalocean.get_key(config)

    local_sshkey = Path(Prompt.ask(f"[dark_orange]\[?][/dark_orange] Enter the local path to the {do_sshkey} private ssh key")).expanduser()
    while not local_sshkey.is_file():
        local_sshkey = Path(Prompt.ask(f"[dark_orange]\[?][/dark_orange] Not a file - Enter the local path to the {do_sshkey} private ssh key")).expanduser()
                   
    config_json = {"directory": str(directory), 
                    "project": project,
                    "instances": dict(),
                    "sshkey_terra": do_sshkey,
                    "sshkey_local": str(local_sshkey),
                    "color_terra": config.color_terra, "color_ansible": config.color_ansible, "color_default": config.color_default,}
    
    config_file.parent.mkdir(exist_ok=True, parents=True)
    config_file.write_text(json.dumps(config_json))

    config.rc.info(f"Configuration file : {config_file} (you can change the colors by editing the json): ")
    config.rc.print_json(json.dumps(config_json))
    config.rc.info("You can now use [turquoise2]Ocean[/turquoise2][gold3 italic]Breeze[/gold3 italic] !")
    exit()

