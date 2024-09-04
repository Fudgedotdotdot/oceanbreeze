from pathlib import Path
import json

from oceanbreeze.lib import helpers
from oceanbreeze.config import config



def list(args):
    """
    Entry point function for the list action
    Gets active terraform state and prettyprints it.  
    """

    if args.domain_name:
        if helpers.terra_check_workspace(config.phishdomain):
            helpers.terra_workspace("select", config.phishdomain)
            for rsrc in helpers.terra_state():
                config.rc.print(f"# {rsrc['type']}.{rsrc['name']}", style="italic")
                config.rc.print(f"resource \"{rsrc['type']}\"", style="italic")
                config.rc.print_json(json.dumps(rsrc['instances'][0]['attributes'])) 
                config.rc.print()
        else:
            config.rc.warning("Domain doesn't exist")
        helpers.terra_workspace("select", "default")

    else:
        config.rc.info("Fetching active domains")
        if not helpers.terra_list_workspace():
            config.rc.warning("Didn't find any deployed infrastructure...", highlight=False)
        else:
            for workspace in helpers.terra_list_workspace():
                instances = config.instances.items()
                if instances:
                    for k, v in instances:
                        if workspace in v:
                            config.rc.print(f"[green]-->[/green] {workspace} ({k})")
                else:
                    config.rc.print(f"[green]-->[/green] {workspace} (no IP)")

        config.rc.info("Template websites")
        websites = Path(config.path_webserver / "template_website/")
        for website in websites.glob("*"):
            if website.is_dir(): config.rc.print(f"[green]-->[/green] {website.parts[-1]}")
        
