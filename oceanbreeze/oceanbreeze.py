import signal
import os
import argparse

from oceanbreeze.config import init_config
from oceanbreeze.modules import deploy, destroy, list

from rich.console import Console

def signal_handler(sig, frame):
    print('Captured CTRL+C or SIGINT, quitting')
    exit()

def create_banner():
    banner = r"""
[turquoise2]   ____                           [/turquoise2][gold3]   ____                             
[turquoise2]  / __ \ _____ ___   ____ _ ____ [/turquoise2][gold3]  / __ ) _____ ___   ___  ____  ___  [/gold3]
[turquoise2] / / / // ___// _ \ / __ `// __ \ [/turquoise2][gold3]/ __  // ___// _ \ / _ \/_  / / _ \ [/gold3]
[turquoise2]/ /_/ // /__ /  __// /_/ // / / [/turquoise2][gold3] / /_/ // /   /  __//  __/ / /_/  __/[gold3]
[turquoise2]\____/ \___/ \___/ \__,_//_/ /_[/turquoise2][gold3] /_____//_/    \___/ \___/ /___/\___/  [/gold3]

[bold grey78]By: 🧀 Fudgedotdotdot ([deep_sky_blue1 link https://twitter.com/fudgedotdotdot]@fudgedotdotdot[/deep_sky_blue1 link https://twitter.com/fudgedotdotdot])
[bold grey78]Version: 1.0.0[/bold grey78]
"""
    Console().print(banner, highlight=False)


def check_env():
    if os.environ.get('DIGITALOCEAN_TOKEN') is None:
        Console().print("[bold red][!] DigitalOcean API key missing[/bold red] - put the key in the [dark_violet]DIGITALOCEAN_TOKEN[/dark_violet] env variable")
        exit()


def main():
    signal.signal(signal.SIGINT, signal_handler)
    check_env()

    parser = argparse.ArgumentParser(description="Manages domain and related infrastructure on DigitalOcean")
    
    subparser = parser.add_subparsers(dest="commands")

    deploy_parser = subparser.add_parser('deploy', help="Deploy infrastructure")
    deploy_parser.add_argument("-d", "--domain", dest="domain_name", help="Domain to manage", required=True, type=str)
    deploy_parser.add_argument("-w", "--website", dest="website", default="socialmedia", help="Upload the selected website template to the droplet")

    list_parser = subparser.add_parser('list', help='List active domain infrastructure')
    list_parser.add_argument("-d", "--domain", dest="domain_name", help="Get details on this workspace/domain", type=str)

    destroy_parser = subparser.add_parser('destroy', help='Destroy infrastructure')
    destroy_parser.add_argument("-d", "--domain", dest="domain_name", required=True, type=str, help="Domain to destroy")

    parser.add_argument('-debug', action='store_true', help="Be verbose plz thanks")
    parser.add_argument('-silent', action='store_true', help="💔 Don't show the banner")
    args = parser.parse_args()

    if not args.silent:
        create_banner()

    if args.commands is None:
        parser.error("Please select an option")

    init_config(args)
   
    if args.commands == "list":
        list.list(args)
    elif args.commands == "destroy":
        destroy.destroy()
    elif args.commands == "deploy":
        deploy.deploy()


if __name__ == "__main__":
    main()