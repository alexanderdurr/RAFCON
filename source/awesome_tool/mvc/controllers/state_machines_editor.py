import pango

import gtk

from mvc.controllers.extended_controller import ExtendedController
from mvc.views.graphical_editor import GraphicalEditorView
from mvc.controllers.graphical_editor import GraphicalEditorController
from mvc.models.state_machine_manager import StateMachineManagerModel
from mvc.models.state_machine import StateMachineModel
from utils import log
logger = log.get_logger(__name__)


def create_tab_close_button(callback, *additional_parameters):
    closebutton = gtk.Button()
    image = gtk.Image()
    image.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
    image_w, image_h = gtk.icon_size_lookup(gtk.ICON_SIZE_SMALL_TOOLBAR)
    closebutton.set_relief(gtk.RELIEF_NONE)
    closebutton.set_focus_on_click(True)
    closebutton.add(image)

    style = gtk.RcStyle()
    style.xthickness = 0
    style.ythickness = 0
    closebutton.modify_style(style)

    closebutton.connect('released', callback, *additional_parameters)

    return closebutton


def create_tab_header(title, close_callback, *additional_parameters):
    hbox = gtk.HBox()
    hbox.set_size_request(width=-1, height=14)  # safe two pixel
    label = gtk.Label(title)
    hbox.add(label)

    fontdesc = pango.FontDescription("Serif Bold 12")
    label.modify_font(fontdesc)

    # add close button
    close_button = create_tab_close_button(close_callback, *additional_parameters)
    hbox.add(close_button)
    hbox.show_all()

    return hbox, label


class StateMachinesEditorController(ExtendedController):

    def __init__(self, sm_manager_model, view, states_editor_ctrl):
        ExtendedController.__init__(self, sm_manager_model, view)

        assert isinstance(sm_manager_model, StateMachineManagerModel)
        self.add_controller('states_editor_ctrl', states_editor_ctrl)

        self.tabs = {}
        self.act_model = None
        self._view = view
        self.registered_state_machines = {}

    def register_view(self, view):
        self.view.notebook.connect('switch-page', self.on_switch_page)
        for sm_id, sm in self.model.state_machines.iteritems():
            self.add_graphical_state_machine_editor(sm)

    def on_switch_page(self, notebook, page, page_num):
        logger.debug("switch to page number %s (for page %s)" % (page_num, page))
        page = notebook.get_nth_page(page_num)
        for identifier, meta in self.tabs.iteritems():
            if meta['page'] is page:
                model = meta['state_machine_model']
                logger.debug("state machine id of current state machine page %s" % model.state_machine.state_machine_id)
                if not model.state_machine.state_machine_id == self.model.selected_state_machine_id:
                    self.model.selected_state_machine_id = model.state_machine.state_machine_id
                return

    def add_graphical_state_machine_editor(self, state_machine_model):

        assert isinstance(state_machine_model, StateMachineModel)

        sm_identifier = state_machine_model.state_machine.state_machine_id
        logger.debug("Create new graphical editor for state machine model with sm id %s" % str(sm_identifier))

        graphical_editor_view = GraphicalEditorView()

        graphical_editor_ctrl = GraphicalEditorController(state_machine_model, graphical_editor_view)
        self.add_controller(sm_identifier, graphical_editor_ctrl)
        (event_box, new_label) = create_tab_header(state_machine_model.root_state.state.name,
                                                   self.on_close_clicked,
                                                   state_machine_model, 'refused')
        graphical_editor_view.get_top_widget().title_label = new_label

        idx = self._view.notebook.append_page(graphical_editor_view['main_frame'], event_box)
        page = self._view.notebook.get_nth_page(idx)
        page.show_all()

        self.tabs[sm_identifier] = {'page': page,
                                    'state_machine_model': state_machine_model,
                                    'ctrl': graphical_editor_ctrl,
                                    'connected': False}

        graphical_editor_view.show()
        self._view.notebook.show()

        self.registered_state_machines[state_machine_model.state_machine.state_machine_id] = graphical_editor_ctrl
        return idx

    @ExtendedController.observe("selected_state_machine_id", assign=True)
    def notifcation_selected_sm_changed(self, model, prop_name, info):
        page = self.tabs[self.model.selected_state_machine_id]['page']
        idx = self.view.notebook.page_num(page)
        # print idx, self.view.notebook.get_current_page()
        if not self.view.notebook.get_current_page() == idx:
            self.view.notebook.set_current_page(idx)

    @ExtendedController.observe("state_machines", after=True)
    def model_changed(self, model, prop_name, info):
        logger.debug("State machine model changed!")
        for sm_id, sm in self.model.state_machine_manager.state_machines.iteritems():
            if sm_id not in self.registered_state_machines:
                self.add_graphical_state_machine_editor(self.model.state_machines[sm_id])

    def on_close_clicked(self, event, state_machine_model, result):
        """ Callback for the "close-clicked" emitted by custom TabLabel widget. """
        # print event, state_model, result

        sm_identifier = state_machine_model.state_machine.state_machine_id
        self.remove_controller(self.registered_state_machines[sm_identifier])

        del self.registered_state_machines[sm_identifier]

        page = self.tabs[sm_identifier]['page']
        current_idx = self.view.notebook.page_num(page)

        self.view.notebook.remove_page(current_idx)  # current_idx)  # utils.find_tab(self.notebook, page))
        del self.tabs[sm_identifier]

        # TODO: Should the state machine be removed here?
        self.model.state_machine_manager.remove_state_machine(sm_identifier)
        sm_keys = self.model.state_machine_manager.state_machines.keys()
        if len(sm_keys) > 0:
            self.model.selected_state_machine_id = \
                self.model.state_machine_manager.state_machines[sm_keys[0]].state_machine_id
        else:
            logger.warn("No state machine left to be the selected state machine. "
                        "The selected state machine id will be None!")
            self.model.selected_state_machine_id = None

    def close_all_tabs(self):
        """
        Closes all tabs of the state machines editor
        :return:
        """
        state_machine_model_list = []
        for s_id, tab in self.tabs.iteritems():
            state_machine_model_list.append(tab['state_machine_model'])
        for state_model in state_machine_model_list:
            self.on_close_clicked(None, state_model, None)
