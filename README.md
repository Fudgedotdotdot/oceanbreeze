![banner](assets/banner.png)


![Python minimum version](https://img.shields.io/badge/Python-3.10%2B-brightgreen)

![WSL](https://img.shields.io/badge/WSL-2-blue)


# Description

OceanBreeze is a infrastructure management tool to deploy and manage domains on DigitalOcean for pentesting engagements. 

You can use the tool to help mature recently bought domains and help them get categorized by adding website templates in the *webserver/template_website* directory and selecting a template when running the tool. 

# Prerequisites
**This tool only works on WSL (tested on WSL2)**

1. Install [Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli) and make it accessible in your PATH. 

2. Install [Ansible with Pipx](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-and-upgrading-ansible-with-pipx)

3. Clone this repository : `git clone https://github.com/Fudgedotdotdot/oceanbreeze`

4. Install the tool with [Pipx](https://pipx.pypa.io/stable/installation/) with `pipx install .` from within the cloned repository. 


Since the tool uses DigitalOcean, there a few things prepare there as well. 

1. Create a project that will house the ressources deployed with this tool.
2. Create and add an SSH key to DigitalOcean. This key will be added to the droplet during the deployement process and used by Ansible.
3. Create an [API key]([https://docs.digitalocean.com/reference/api/create-personal-access-token/]) on DigitalOcean and save it in the `DIGITALOCEAN_TOKEN` environment variable

# Usage
When first running the tool, a configuration menu will prompt you for information to setup the tool. 

You can then deploy, list and destroy infrastructure :
```bash
❯ oceanbreeze -h
usage: oceanbreeze [-h] [-silent] {deploy,list,destroy} ...

Manages domain and related infrastructure on DigitalOcean

positional arguments:
  {deploy,list,destroy}
    deploy              Deploy infrastructure
    list                List active domain infrastructure
    destroy             Destroy infrastructure

options:
  -h, --help            show this help message and exit
  -silent               💔 Don't show the banner
```

