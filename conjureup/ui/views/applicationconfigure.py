""" Application Configuration View

"""

from urwid import Filler, WidgetWrap, Pile, Text

from conjureup.app_config import app
from conjureup.ui.widgets.option_widget import OptionWidget

from ubuntui.widgets.buttons import PlainButton
from ubuntui.widgets.hr import HR
from ubuntui.utils import Padding

import logging

log = logging.getLogger('conjure')


class ApplicationConfigureView(WidgetWrap):
    def __init__(self, application, metadata_controller, controller):
        self.controller = controller
        self.application = application
        self.options_copy = self.application.options.copy()
        self.metadata_controller = metadata_controller
        self.widgets = self.build_widgets()
        super().__init__(self.widgets)
        self.pile.focus_position = 1

    def selectable(self):
        return True

    def build_widgets(self):
        ws = [Text("Configure {}".format(
            self.application.service_name))]
        ws += self.get_option_widgets()
        ws += [HR(), PlainButton("Cancel", self.do_cancel),
               PlainButton("Accept Changes", self.do_commit)]
        self.pile = Pile(ws)
        return Padding.center_90(Filler(self.pile, valign="top"))

    def get_option_widgets(self):
        ws = []
        service_id = self.application.csid.as_str_without_rev()
        options = self.metadata_controller.get_options(service_id)
        metadata = app.config.get('metadata', None)
        if metadata is None:
            return []

        options_whitelist = metadata.get('options-whitelist', None)
        if options_whitelist is None:
            return []

        svc_opts_whitelist = options_whitelist.get(
            self.application.service_name,
            [])

        hidden = [n for n in options.keys() if n not in svc_opts_whitelist]
        log.info("Hiding options not in the whitelist: {}".format(hidden))
        for opname in svc_opts_whitelist:
            opdict = options[opname]
            cv = self.application.options.get(opname, None)
            ow = OptionWidget(opname,
                              opdict['Type'],
                              opdict['Description'],
                              opdict['Default'],
                              current_value=cv,
                              value_changed_callback=self.handle_edit)
            ws.append(ow)
        return ws

    def handle_edit(self, opname, value):
        self.options_copy[opname] = value

    def do_cancel(self, sender):
        self.controller.handle_configure_done()

    def do_commit(self, sender):
        self.application.options = self.options_copy
        self.controller.handle_configure_done()
