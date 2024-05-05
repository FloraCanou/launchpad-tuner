# © 2024 Flora Canou, based on Godtone's work
# This work is licensed under the AGPLv3 <https://www.gnu.org/licenses/agpl-3.0.html>

from lpt_io import *

def mapping_basic (vel = 96):
    """
    Basic isomorphic layout mapping function.
    vel: buttons not pressure-sensitive get this velocity.
    """
    global mi_launchpad_name, mo_loopmidi_name
    
    # transform the launchpad's midi input (mi) into custom midi output (mo)
    with mido.open_input (mi_launchpad_name) as mi, mido.open_output (mo_loopmidi_name) as mo:
        for msg in mi: # process midi messages from launchpad
            msg_to_send = msg.copy ()
            if msg.type == "control_change":
                msg_to_send = mido.Message ("note_on", note = msg.control, velocity = vel if msg.value else 0)
            if not msg.type == "clock":
                print (msg_to_send)
            mo.send (msg_to_send)

def mapping_xy (x, y, base_note = 60, vel = 96):
    """
    (x, y) isomorphic layout mapping function.
    base_note: pad at bottom left.
    vel: buttons not pressure-sensitive get this velocity.
    """
    global mi_launchpad_name, mo_loopmidi_name

    def get_coordinates (k):
        k %= 100
        return k//10, k%10

    def transform (midi_note):
        """
        Defines the mapping from midi note given by launchpad 
        to midi note in isomorphic layout.
        """
        row, col = get_coordinates (midi_note)
        return (col - 1)*x + (row - 1)*y + base_note
    
    # transform the launchpad's midi input (mi) into custom midi output (mo)
    with mido.open_input (mi_launchpad_name) as mi, mido.open_output (mo_loopmidi_name) as mo:
        for msg in mi: # process midi messages from launchpad
            msg_to_send = msg.copy ()
            if msg.type == "note_on":
                msg_to_send = mido.Message ("note_on", note = transform (msg.note), velocity = msg.velocity)
            if msg.type == "control_change":
                msg_to_send = mido.Message ("note_on", note = transform (msg.control), velocity = vel if msg.value else 0)
            if not msg.type == "clock":
                print (msg_to_send)
            mo.send (msg_to_send)

def color_basic ():
    '''Basic lighting function. '''
    global mo_launchpad_name
    with mido.open_output (mo_launchpad_name) as color:
        print ("Coloring..")
        for k in range (1, 109):
            msg = mido.Message ('note_on', channel = 0, note = k, velocity = k)
            color.send (msg)

def unlight ():
    '''Basic unlighting function.'''
    global mo_launchpad_name
    with mido.open_output (mo_launchpad_name) as color:
        print ("Unlighting..")
        for k in range (1, 109):
            msg = mido.Message ('note_off', channel = 0, note = k)
            color.send (msg)
