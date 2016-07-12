import logging
import threading
import time

from gi.repository import GLib, Gtk

from tails_server import tor_util
from tails_server.exceptions import TorIsNotRunningError
from tails_server.gui.config_panel import ServiceConfigPanel
from tails_server.gui.service_status import Status, ServiceStatus


class ServiceDecorator(object):

    status_row = None

    def __init__(self, gui, service):
        self.gui = gui
        self.service = service
        self.status = ServiceStatus(self)
        try:
            self.config_panel = ServiceConfigPanel(self.gui, self)
        except AttributeError as e:
            # XXX: This is a workaround for a bug in Python which blames all AttributeErrors on
            # __getattr__, if a custom __getattr__ was defined.
            raise Exception(e)

    def __getattr__(self, item):
        return getattr(self.service, item)

    def install(self):
        if not tor_util.tor_has_bootstrapped():
            self.status.emit("update", Status.tor_is_not_running)
            while not tor_util.tor_has_bootstrapped():
                time.sleep(1)
        self.status.emit("update", Status.installing)
        self.service.install()
        self.status.emit("update", Status.installed)
        GLib.idle_add(self.config_panel.on_service_installed)

    def uninstall(self):
        self.status.emit("update", Status.uninstalling)
        self.stop_status_monitor()
        self.service.uninstall()
        self.config_panel = None

    def enable(self):
        self.status.emit("update", Status.starting)
        try:
            self.service.enable(skip_add_onion=True)
            self.add_onion()
        except TorIsNotRunningError:
            self.status.emit("update", Status.tor_is_not_running)

    def add_onion(self):
        self.status.emit("update", Status.publishing)
        self.service.add_onion()
        if self.service.is_running:
            self.status.emit("update", Status.online)
        else:
            logging.debug("Removing newly created onion address because service %r stopped",
                          self.name)
            self.remove_onion()

    def activate_status_monitor(self):
        self.status.dbus_monitor.run()
        self.status.tor_dbus_monitor.run()

    def stop_status_monitor(self):
        self.status.dbus_monitor.stop()
        self.status.tor_dbus_monitor.stop()

    def run_threaded(self, function, *args):
        thread = threading.Thread(target=self.run_with_exception_handling,
                                  args=(function,) + args)
        thread.daemon = True
        thread.start()

    def run_threaded_when_idle(self, function, *args):
        thread = threading.Thread(target=self.run_with_exception_handling,
                                  args=(GLib.idle_add, function) + args)
        thread.daemon = True
        thread.start()

    def run_with_exception_handling(self, function, *args):
        try:
            function(*args)
        except:
            self.status.emit("update", Status.error)
            raise
