# © 2024 Flora Canou, based on Godtone's work
# This work is licensed under the AGPLv3 <https://www.gnu.org/licenses/agpl-3.0.html>

import math
from lpt_io import *

# 0x00 -- 0x03 grayscale
# 0x04 -- 0x3B 14 chromas * 4 levels
# 0x3C -- 0x7F other colors

rb7 = [0x05, 0x0d, 0x15, 0x1d, 0x25, 0x2d, 0x35] # rb for rainbow
color_map = [0x00]*109

def mapping (x, y, n, base_note = 60):
    """
    (x, y) isomorphic layout mapping function
    with register keys for each row that move the notes by n steps. 
    base_note: pad at bottom left.
    """
    global mi_launchpad_name, mo_launchpad_name, mo_loopmidi_name
    
    def get_coordinates (k):
        """Gets the coordinates (row, col) for key code k on the Launchpad."""
        k %= 100
        return k//10, k%10

    def transform (midi_note):
        """
        Defines the mapping from midi note given by launchpad 
        to midi note in isomorphic layout.
        """
        row, col = get_coordinates (midi_note)
        return (col - 1)*x + (row - 1)*y + base_note + (control_reg if row == control_row else 0)

    with mido.open_output (mo_launchpad_name) as color:
        print ("Coloring..")
        for k in range (1, 109):
            msg = mido.Message ('note_on', channel = 0, note = k, velocity = color_map[k])
            color.send (msg)

    # transform the launchpad's midi input (mi) into custom midi output (mo)
    with mido.open_input (mi_launchpad_name) as mi, mido.open_output (mo_loopmidi_name) as mo:
        control_row = 0
        control_reg = 0
        for msg in mi: # process midi messages from launchpad
            msg_to_send = msg.copy ()
            if msg.type == "control_change":
                control_row = msg.control//10
                control_reg = n if msg.value else 0
            if msg.type == "note_on":
                msg_to_send = mido.Message ("note_on", note = transform (msg.note), velocity = msg.velocity)

            # if not msg.type == "clock":
            #     print (msg_to_send)

            mo.send (msg_to_send)
