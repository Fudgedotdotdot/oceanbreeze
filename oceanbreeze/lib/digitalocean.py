
from rich.prompt import Prompt
import os
import requests


def get_project(config):
        """
        Gets the list of projects in DigitalOcean
        """
        # Prompt for the project where the ressources will be organized
        resp = _make_api_call("https://api.digitalocean.com/v2/projects")
        project_list = [x['name'] for x in resp['projects']]
        for project in project_list:
            config.rc.print(f"[green]-->[/green] {project}")

        project = Prompt.ask("[dark_orange]\[?][/dark_orange] Select the project in which all the created ressouces will be placed")
        while project not in project_list:
            project = Prompt.ask("[dark_orange]\[?][/dark_orange] Invalid project, please select one that exists")
            if project in project_list: break
        return project


def get_key(config):
    """
    Gets the ssh keys in DigitalOcean
    """

    # Prompt for the SSH key that will be added to the spawned droplet
    resp = _make_api_call("https://api.digitalocean.com/v2/account/keys")
    key_list = [x['name'] for x in resp['ssh_keys']]
    for key in key_list:
        config.rc.print(f"[green]-->[/green] {key}")

    key = Prompt.ask("[dark_orange]\[?][/dark_orange] Select SSH key that will be added to the droplet")
    while key not in key_list:
        key = Prompt.ask("[dark_orange]\[?][/dark_orange] Invalid key, please select one that exists")
        if key in key_list: break
    return key


def _make_api_call(url):
    headers = {"Authorization": f"Bearer {os.environ['DIGITALOCEAN_TOKEN']}",
                "Content-Type": "application/json",
                "User-Agent": "OceanBreeze"
            }
    resp = requests.get(url, headers=headers).json()
    return resp