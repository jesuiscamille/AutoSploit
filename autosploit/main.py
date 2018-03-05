import sys

import psutil

from lib.cmdline.cmd import AutoSploitParser
from lib.term.terminal import AutoSploitTerminal
from lib.output import (
    info,
    warning,
    error,
    prompt,
    misc_info
)
from lib.settings import (
    logo,
    load_api_keys,
    check_services,
    cmdline,
    EXPLOIT_FILES_PATH,
    START_APACHE_PATH,
    START_POSTGRESQL_PATH,
    SERVICE_NAMES
)
from lib.jsonize import load_exploits


def main():

    opts = AutoSploitParser().optparser()

    logo()
    info("welcome to autosploit, give us a little bit while we configure")
    misc_info("checking for disabled services")
    # according to ps aux, postgre and apache2 are the names of the services
    #SERVICE_NAMES = ("postgres", "apache2")
    for service in list(SERVICE_NAMES):
        while not check_services(service):
            choice = prompt(
                "it appears that service {} is not enabled, would you like us to enable it for you[y/N]".format(
                    service[0].title()
                )
            )
            if choice.lower().startswith("y"):
                try:
                    if "postgre" in service:
                        cmdline("sudo bash {}".format(START_POSTGRESQL_PATH))
                    else:
                        cmdline("sudo bash {}".format(START_APACHE_PATH))
                    # moving this back because it was funky to see it each run
                    info("services started successfully")
                # this tends to show up when trying to start the services
                # I'm not entirely sure why, but this fixes it
                except psutil.NoSuchProcess:
                    pass
            else:
                error(
                    "service {} is required to be started for autosploit to run successfully (you can do it manually "
                    "by using the command `sudo service {} start`), exiting".format(
                        service.title(), service
                    )
                )
                sys.exit(1)

    if len(sys.argv) > 1:
        info("attempting to load API keys")
        loaded_tokens = load_api_keys()
        AutoSploitParser().parse_provided(opts)
        misc_info("checking if there are multiple exploit files")
        loaded_exploits = load_exploits(EXPLOIT_FILES_PATH)
        AutoSploitParser().single_run_args(opts, loaded_tokens, loaded_exploits)
    else:
        warning("no arguments have been parsed, defaulting to terminal session. press 99 to quit and help to get help")
        misc_info("checking if there are multiple exploit files")
        loaded_exploits = load_exploits(EXPLOIT_FILES_PATH)
        info("attempting to load API keys")
        loaded_tokens = load_api_keys()
        terminal = AutoSploitTerminal(loaded_tokens)
        terminal.terminal_main_display(loaded_exploits)
