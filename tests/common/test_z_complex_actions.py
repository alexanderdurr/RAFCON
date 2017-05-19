"""Every test function of this module should later be improved in a separate module to secure all functionality of the 
every respective feature."""
import threading

# gui elements
import rafcon.gui.singleton
from rafcon.gui.controllers.main_window import MainWindowController
from rafcon.gui.views.main_window import MainWindowView

# core elements
import rafcon.core.singleton
from rafcon.core.states.hierarchy_state import HierarchyState
from rafcon.core.states.execution_state import ExecutionState
from rafcon.core.states.barrier_concurrency_state import BarrierConcurrencyState, UNIQUE_DECIDER_STATE_ID
from rafcon.core.state_machine import StateMachine

# general tool elements
from rafcon.utils import log

# test environment elements
import testing_utils
from testing_utils import call_gui_callback
import pytest

logger = log.get_logger(__name__)


def create_models(*args, **kargs):

    state1 = HierarchyState('State1', state_id="State1")
    state2 = ExecutionState('State2', state_id="State2")

    ctr_state = HierarchyState(name="Root", state_id="Root")
    ctr_state.add_state(state1)
    ctr_state.add_state(state2)
    ctr_state.name = "Container"

    sm = StateMachine(ctr_state)

    # add new state machine
    rafcon.core.singleton.state_machine_manager.add_state_machine(sm)
    # select state machine
    rafcon.gui.singleton.state_machine_manager_model.selected_state_machine_id = sm.state_machine_id


def test_state_type_change(caplog):
    pass


def test_substitute_state(caplog):
    pass


def test_group_states(caplog):
    pass


def test_ungroup_state(caplog):
    pass


@log.log_exceptions(None, gtk_quit=True)
def trigger_repetitive_group_ungroup(*args):
    import rafcon.gui.helpers.state as gui_helper_state
    import rafcon.gui.singleton as gui_singletons
    import time
    sm_manager_model = args[0]
    main_window_controller = args[1]
    logger = args[2]

    states_machines_editor_controller = main_window_controller.get_controller('state_machines_editor_ctrl')
    graphical_editor_controller = states_machines_editor_controller.get_child_controllers()[0]
    call_gui_callback(graphical_editor_controller.view.editor.set_size_request, 500, 500)

    sm_id = gui_singletons.state_machine_manager_model.state_machines.values()[0].state_machine.state_machine_id
    gui_singletons.state_machine_manager_model.selected_state_machine_id = sm_id
    sm_m = gui_singletons.state_machine_manager_model.get_selected_state_machine_model()
    print "select: ", sm_m.root_state.states.values()
    call_gui_callback(sm_m.selection.set, sm_m.root_state.states.values())
    # time.sleep(1)
    call_gui_callback(gui_helper_state.group_selected_states_and_scoped_variables)
    sm_m.root_state.states.values()[0].state.name = "Stage 1"

    print "select: ", sm_m.root_state.states.values()
    call_gui_callback(sm_m.selection.set, sm_m.root_state.states.values()[0].states.values())
    # time.sleep(1)
    call_gui_callback(gui_helper_state.group_selected_states_and_scoped_variables)
    sm_m.root_state.states.values()[0].states.values()[0].state.name = "Stage 2"

    print "select: ", sm_m.root_state.states.values()
    call_gui_callback(sm_m.selection.set, sm_m.root_state.states.values()[0].states.values()[0].states.values())
    # time.sleep(1)
    call_gui_callback(gui_helper_state.group_selected_states_and_scoped_variables)
    sm_m.root_state.states.values()[0].states.values()[0].states.values()[0].state.name = "Stage 3"

    # time.sleep(5)

    # raw_input("press enter")
    call_gui_callback(sm_m.selection.set, sm_m.root_state.states.values()[0].states.values()[0])
    # time.sleep(1)
    call_gui_callback(gui_helper_state.ungroup_selected_state)
    # return
    call_gui_callback(sm_m.selection.set, sm_m.root_state.states.values()[0])
    # time.sleep(1)
    call_gui_callback(gui_helper_state.ungroup_selected_state)

    call_gui_callback(sm_m.selection.set, sm_m.root_state.states.values()[0])
    # time.sleep(1)
    call_gui_callback(gui_helper_state.ungroup_selected_state)

    call_gui_callback(sm_m.selection.set, sm_m.root_state.states.values())
    # time.sleep(1)
    call_gui_callback(gui_helper_state.group_selected_states_and_scoped_variables)
    sm_m.root_state.states.values()[0].state.name = "Stage 1"

    call_gui_callback(sm_m.selection.set, sm_m.root_state.states.values()[0])
    call_gui_callback(gui_helper_state.change_state_type, sm_m.root_state.states.values()[0], BarrierConcurrencyState)
    # time.sleep(1)
    # return

    # raw_input("enter")
    selected_states = [sm_m.root_state.states.values()[0].states[state_id] for state_id in ['State1', 'State2']]
    print "\n" * 50
    print "select: ", [str(state_m) for state_m in selected_states]
    call_gui_callback(sm_m.selection.set, selected_states)
    # time.sleep(1)
    call_gui_callback(gui_helper_state.group_selected_states_and_scoped_variables)

    # core test
    # call_gui_callback(sm_m.root_state.states.values()[0].state.group_states, ['State1', 'State2'])
    # sm_m.root_state.states.values()[0].states.values()[0].state.name = "Stage 2"
    print "\n" * 50
    # raw_input("enter")
    print "wait1"
    # time.sleep(10)
    call_gui_callback(sm_m.history.undo)
    print "wait2 undo"
    # time.sleep(10)

    # exception test
    selected_states = [sm_m.root_state.states.values()[0].states[state_id] for state_id in
                       ['State1', 'State2', UNIQUE_DECIDER_STATE_ID]]
    print "select: ", [str(state_m) for state_m in selected_states]
    call_gui_callback(sm_m.selection.set, sm_m.root_state.states.values()[0].states.values())
    call_gui_callback(gui_helper_state.group_selected_states_and_scoped_variables)

    # exception core test
    # call_gui_callback(sm_m.root_state.states.values()[0].state.group_states, ['State1', 'State2', UNIQUE_DECIDER_STATE_ID])
    print "wait3 failure"
    # exit()
    # time.sleep(5)
    print "quitting"
    menubar_ctrl = main_window_controller.get_controller('menu_bar_controller')
    call_gui_callback(menubar_ctrl.prepare_destruction)


def test_repetitive_ungroup_state_and_group_states(caplog):
    """Check if repetitive group and ungroup works"""

    testing_utils.initialize_environment(libraries={"unit_test_state_machines":
                                                    testing_utils.get_test_sm_path("unit_test_state_machines")})

    create_models()

    main_window_view = MainWindowView()

    # load the meta data for the state machine
    rafcon.gui.singleton.state_machine_manager_model.get_selected_state_machine_model().root_state.load_meta_data()

    main_window_controller = MainWindowController(rafcon.gui.singleton.state_machine_manager_model, main_window_view)

    testing_utils.wait_for_gui()
    thread = threading.Thread(target=trigger_repetitive_group_ungroup,
                              args=[rafcon.gui.singleton.state_machine_manager_model, main_window_controller, logger])
    thread.start()

    import gtk
    gtk.main()
    logger.debug("Gtk main loop exited!")
    sm = rafcon.core.singleton.state_machine_manager.get_active_state_machine()
    if sm:
        sm.root_state.join()
        logger.debug("Joined currently executing state machine!")
        thread.join()
        logger.debug("Joined test triggering thread!")

    testing_utils.shutdown_environment(caplog=caplog, expected_warnings=0, expected_errors=1)
    pass


def test_paste_method(caplog):
    """Check multiple Scenarios of paste methods"""
    # meta data adjustments
    # model assignments
    pass

if __name__ == '__main__':
    # test_repetitive_ungroup_state_and_group_states(None)
    pytest.main([__file__, '-xs'])