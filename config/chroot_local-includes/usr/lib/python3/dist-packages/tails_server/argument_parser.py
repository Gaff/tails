import argparse
import sys

from tails_server import import_services


class HelpfulParser(argparse.ArgumentParser):
    """Argument parser that prints the help on error"""
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


class CommandParser(HelpfulParser):
    descriptions = {
        'info': "Print information about the service",
        'status': "Print whether the service is installed and running",
        'install': "Install the service",
        'uninstall': "Uninstall the service",
        'enable': "Enables the service",
        'disable': "Disables the service",
        'get-option': "Print the current value of an option",
        'set-option': "Set an option. If the service is running, the option will be applied "
                      "immediately and, if necessary, the service will be restarted!",
        'reset-option': "Same as set-option, but using the option's default value"
    }

    service_commands = descriptions.keys()

    def add_service_command(self, command_name, *arguments):
        """Add a command to the argument parser"""
        command = self.subparsers.add_parser(command_name,
                                             help=self.descriptions[command_name],
                                             description=self.descriptions[command_name])
        for argument in arguments:
            command.add_argument(**argument)

        command.add_argument(dest="SERVICE", type=str, metavar="SERVICE",
                             choices=import_services.service_names)
        return command

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_argument("--verbose", "-v", action="count")
        self.add_argument("--log-file")

        self.subparsers = self.add_subparsers(dest="command", parser_class=HelpfulParser)

        # Add general commands
        self.subparsers.add_parser("list", help="Print list of available services")
        self.subparsers.add_parser("list-enabled", help="Print list of enabled services")
        self.subparsers.add_parser("restore", help="Install packages and restore files of services "
                                                   "which have the 'persistence' option set to True")
        self.subparsers.add_parser("autostart", help="Enable the services which have the "
                                                     "'autostart' option set to True")

        # Add service commands
        info_parser = self.add_service_command("info")
        info_parser.add_argument("--details", action="store_true")
        self.add_service_command("status")
        self.add_service_command("install")
        self.add_service_command("uninstall")
        self.add_service_command("enable")
        self.add_service_command("disable")
        self.add_service_command("get-option", {"dest": "OPTION", "type": str})
        self.add_service_command("set-option", {"dest": "OPTION", "type": str},
                                 {"dest": "VALUE", "type": str})
        self.add_service_command("reset-option", {"dest": "OPTION", "type": str})



    def parse_args(self, **kwargs):
        args = super().parse_args(**kwargs)

        if not any(vars(args).values()):
            self.print_help()
            self.exit()

        return args


class ServiceParser(CommandParser):
    pass