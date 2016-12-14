"""
.. module:: undocked_window
   :platform: Unix, Windows
   :synopsis: A module that holds the controller un-docked windows as part of the un- and re-dock feature.

.. moduleauthor:: Mahmoud Akl


"""

from rafcon.gui.controllers.utils.extended_controller import ExtendedController
from rafcon.gui.controllers.top_tool_bar import TopToolBarUndockedWindowController


class UndockedWindowController(ExtendedController):
    """Controller handling the un-docked windows

    :param rafcon.gui.models.state_machine_manager.StateMachineManagerModel state_machine_manager_model: The state
        machine manager model, holding data regarding state machines. Should be exchangeable.
    :param rafcon.gui.views.undocked_window.UndockedWindowView view: The GTK View showing the separate window
    """

    def __init__(self, state_machine_manager_model, view, redock_method):
        ExtendedController.__init__(self, state_machine_manager_model, view)

        self.top_tool_bar_undocked_window_controller = TopToolBarUndockedWindowController(state_machine_manager_model,
                                                                                          view.top_tool_bar,
                                                                                          view['undock_window'],
                                                                                          redock_method)

        self.add_controller('top_tool_bar_undocked_window_controller', self.top_tool_bar_undocked_window_controller)

    def hide_window(self):
        self.view['undock_window'].hide()

    def show_window(self):
        self.view['undock_window'].show()