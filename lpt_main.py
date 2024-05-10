# © 2024 Flora Canou, based on Godtone's work
# This work is licensed under the AGPLv3 <https://www.gnu.org/licenses/agpl-3.0.html>

from lpt_io import *

# factory colors: 
# 0x00 -- 0x03 grayscale
# 0x04 -- 0x3B 14 chromas * 4 levels
# 0x3C -- 0x7F other colors

def tone (n):
    """
    Approximate number of steps of the whole tone in n-edo. 
    Precision should be enough for n < 20,000.
    """
    return int (round (n*0.169925))

def get_coordinates (k):
    """Gets the coordinates (row, col) for key code k on the Launchpad."""
    k %= 100
    return k//10, k%10

def chromatic (n):
    """
    (tone - step, step) isomorphic layout lighting and mapping function. 
    In this layout, each note along the main diagonal line ascends by a whole tone. 
    We're lighting these notes and all the duplicates thereof. 
    Assume the base note is Db, we're lighting Db, Eb, F, G, A, B, C#, and D#. 
    For plain-fifth edos we're also lighting D, E, F#, G#, Ab, Bb, C and D. 

    low Db  = gray
    low D   = red
    Eb      = orange
    E       = yellow
    F       = chartreuse
    F#      = green
    G       = spring
    G#      = cyan #1 (aquamarine)
    Ab      = cyan #2 (capri)
    A       = azure
    Bb      = blue
    B       = violet
    C       = magenta
    C#      = rose
    high D  = red
    high D# = gray
    """
    global mi_launchpad_name, mo_launchpad_name, mo_loopmidi_name
    
    # rb for rainbow
    # basic palette along the main diagonal line
    rb = [0x09, 0x11, 0x19, 0x29, 0x31, 0x39] 
    
    # approximate number of steps of the whole tone
    # and chroma for plain-fifth edos
    t = tone (n)
    chroma = (7*t - n)//2 if (n + t) % 2 == 0 else None

    color_map = [0x00]*100
    for k in range (0, 100):
        row, col = get_coordinates (k)
        if row == 0 or row == 9 or col == 0 or col == 9:
            continue # skip control keys
        
        # light low Db (bottom left) and high D# (upper right)
        if row == 1 and col == 1 or row == 8 and col == 8:
            color_map[k] = 0x02
        # light Eb, F, G, A, B, and C#
        elif (row - col) % t == 0:
            color_offset = (col + (row - col)//t - 2) % 6
            color_map[k] = rb[color_offset]
        elif chroma:
            # light D, E, F#, G#
            if ((row - col) % t % chroma == 0 and (row - col) % t // chroma == 1
                    and col + (row - col)//t <= 4): # don't light A#
                color_offset = (col + (row - col)//t - 2) % 6
                color_map[k] = (rb[color_offset] + 4 - 4) % 0x38 + 4
            # light Ab, Bb, C and D
            elif ((col - row) % t % chroma == 0 and (col - row) % t // chroma == 1
                    and col + (row - col)//t >= 4): # don't light Gb
                color_offset = (col + (row - col)//t - 1) % 6
                color_map[k] = (rb[color_offset] - 4 - 4) % 0x38 + 4
        
    mapping (n, x = t - 1, y = 1, color_map = color_map, base_note = n)

def mapping (n, x, y, color_map = [0x00]*100, base_note = 60):
    """
    (x, y) isomorphic layout mapping function
    with register keys for each row that move the notes by n steps. 
    color_map: a 100-entry (0 to 99) list of colors from Launchpad's color palette. 
    base_note: pad at bottom left.
    """
    global mi_launchpad_name, mo_launchpad_name, mo_loopmidi_name

    def transform (midi_note):
        """
        Defines the mapping from midi note given by Launchpad 
        to midi note in isomorphic layout.
        """
        row, col = get_coordinates (midi_note)
        return (col - 1)*x + (row - 1)*y + base_note + (control_reg if row == control_row else 0)

    with mido.open_output (mo_launchpad_name) as color:
        print ("Coloring..")
        for k in range (1, 109):
            msg = mido.Message ('note_on', channel = 0, note = k, velocity = color_map[k % 100])
            color.send (msg)

    # transform the launchpad's midi input (mi) into custom midi output (mo)
    with mido.open_input (mi_launchpad_name) as mi, mido.open_output (mo_loopmidi_name) as mo:
        control_row, control_reg = 0, 0
        note_state = dict () # for keeping track of equivalent notes being held
        for note in range (0, 128):
            note_state[note] = 0
        for msg in mi: # process midi messages from launchpad
            msg_to_send = msg.copy ()
            if msg.type == "control_change":
                control_row = msg.control//10

                # turn off all midi notes of the row before changing register
                for k in range (1, 9):
                    note = transform (control_row*10 + k)
                    if note_state[note]:
                        mo.send (mido.Message ("note_on", note = note, velocity = 0))
                        note_state[note] -= 1
                
                control_reg = n if msg.value else 0
            if msg.type == "note_on":
                note = transform (msg.note)
                # turn off equivalent midi note before repressing
                if msg.velocity:
                    if note_state[note]: #if the note is already held
                        mo.send (mido.Message ("note_on", note = note, velocity = 0)) 
                    note_state[note] += 1
                elif note_state[note]: #if we're releasing a note
                    note_state[note] -= 1
                # print (note_state[note])

                msg_to_send = mido.Message ("note_on", note = note, velocity = msg.velocity)

            if not msg.type == "clock" and not msg.type == "aftertouch":
                print (msg_to_send)

            mo.send (msg_to_send)
