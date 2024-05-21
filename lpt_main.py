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
    In this layout, each step along the main diagonal direction (bottom-left to top-right) ascends by a whole tone. 
    Assume the base note is Cb, our range is low Db to high D#. 
    We're lighting these notes and all the duplicates thereof, specifically 
    Db, Eb, F, G, A, B, C#, and D#. 
    For plain-fifth edos we're also lighting 
    D, E, F#, G#, Ab, Bb, C and D. 

    Color codes: 
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

    # overflow protection
    if 8*t >= 0x80: # raise for edos >= 92
        raise ValueError ("Edo is too large to be mapped.")
    elif 9*t >= 0x80: # warn for edos between 86 and 91
        warnings.warn ("Many notes will be skipped. Register keys will be disabled for most notes. Tone-shifting keys will be disabled for some notes. ")
        compromise_offset = -chroma if chroma else -t//2
    elif 8*t + n >= 0x80: # warn for edos between 56 and 85
        warnings.warn ("Some notes will be skipped and register keys will be disabled for some notes. ")
        compromise_offset = 0
    elif 9*t + n >= 0x80: # warn for edos between 51 and 55
        warnings.warn ("Tone-shifting keys will be disabled for some notes. ")
        compromise_offset = -chroma if chroma else -t//2
    else:
        compromise_offset = 0

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
            # light low D, E, F#, and G# above G
            if ((row - col) % t % chroma == 0 and (row - col) % t // chroma == 1
                    # and col + (row - col)//t <= 4): 
                    and col <= 4): # only light the G# above G
                color_offset = (col + (row - col)//t - 2) % 6
                color_map[k] = (rb[color_offset] + 4 - 4) % 0x38 + 4
            # light high D, C, Bb, and Ab below A
            elif ((col - row) % t % chroma == 0 and (col - row) % t // chroma == 1
                    # and col + (row - col)//t >= 4): 
                    and col >= 5): # only light the Ab below A
                color_offset = (col + (row - col)//t - 1) % 6
                color_map[k] = (rb[color_offset] - 4 - 4) % 0x38 + 4
    
    # we're mapping the low Cb to 0 if it's not compromised
    # otherwise we're mapping the low C to 0
    if chroma:
        note_series = [t + chroma + compromise_offset, 5*t + compromise_offset]
        print (
            f"Suggested reference midi note: \n"
            f"Contratreble in F: D6 = {note_series[1]}\n"
            f"Piccolo      in C: D5 = {note_series[0]}\n"
            f"Treble       in F: D5 = {note_series[1]}\n"
            f"Soprano      in C: D4 = {note_series[0]}\n"
            f"Alto         in F: D4 = {note_series[1]}\n"
            f"Tenor        in C: D3 = {note_series[0]}\n"
            f"Baritone     in F: D3 = {note_series[1]}\n"
            f"Bass         in C: D2 = {note_series[0]}\n"
            f"Great Bass   in F: D2 = {note_series[1]}\n"
            f"Contrabass   in C: D1 = {note_series[0]}"
        )
    mapping (n, x = t - 1, y = 1, color_map = color_map, base_note = compromise_offset)

def mapping (n, x, y, color_map = [0x00]*100, base_note = 60):
    """
    (x, y) isomorphic layout mapping function
    with register keys for each row that move the notes by n steps. 
    color_map: a 100-entry (0 to 99) list of colors from Launchpad's color palette. 
    base_note: theoretical note to the bottom left of the pads (where *setup* is).
    """
    global mi_launchpad_name, mo_launchpad_name, mo_loopmidi_name
    t = tone (n)

    def transform (midi_note):
        """
        Defines the mapping from midi note given by Launchpad 
        to midi note in isomorphic layout.
        """
        row, col = get_coordinates (midi_note)
        base_and_offset = base_note + col*x + row*y
        reg = n if control_r0_state[row] else 0
        alt = (t if control_c9_state[col] else 0) - (t if control_c0_state[col] else 0)
        if (result := base_and_offset + reg  + alt) // 0x80 == 0:
            return result
        else:
            return base_and_offset

    with mido.open_output (mo_launchpad_name) as color:
        print ("Coloring..")
        for k in range (1, 109):
            msg = mido.Message ('note_on', channel = 0, note = k, velocity = color_map[k % 100])
            color.send (msg)

    # transform the launchpad's midi input (mi) into custom midi output (mo)
    with mido.open_input (mi_launchpad_name) as mi, mido.open_output (mo_loopmidi_name) as mo:
        key_state = {key: 0 for key in range (100)} # for keeping track of keys being held
        note_state = {note: 0 for note in range (0x80)} # for keeping track of notes being played
        control_r0_state, control_r9_state, control_c0_state, control_c9_state \
            = ({key: 0 for key in range (10)} for _ in range (4)) # for keeping track of control keys being held
        for msg in mi: # process midi messages from launchpad
            msg_to_send = msg.copy ()
            if msg.type == "control_change":
                control_row, control_col = get_coordinates (msg.control)

                if control_col == 0: # left control keys
                    # move all midi notes of the row to the new register
                    # on activating the register key
                    for col in range (1, 9):
                        # get the key and the old note it's mapped to
                        key = control_row*10 + col
                        control_r0_state[control_row] = not bool (msg.value)
                        note_old = transform (key)

                        # if we find a key that's held
                        if key_state[key]: 
                            # turn off the old note
                            mo.send (mido.Message ("note_on", note = note_old, velocity = 0))

                            # if we're activating the register key
                            if msg.value:
                                # get the new note
                                control_r0_state[control_row] = True
                                note_new = transform (key)

                                # turn off the new note if it's on, and then
                                # turn it on with the old note's original velocity
                                if note_state[note_new]: 
                                    mo.send (mido.Message ("note_on", note = note_new, velocity = 0))
                                mo.send (mido.Message ("note_on", note = note_new, velocity = note_state[note_old]))

                                # record the new note
                                note_state[note_new] = note_state[note_old]
                            
                            # clear the old note
                            note_state[note_old] = 0
                    
                    # set the control state
                    control_r0_state[control_row] = bool (msg.value)
                    # print (control_row, control_r0_state[control_row], sep = ", ")

                elif control_col == 9: #right control keys
                    pass

                if control_row == 0: # bottom control keys
                    # tone-shift all midi notes of the column
                    for row in range (1, 9):
                        # get the key and the old note it's mapped to
                        key = row*10 + control_col
                        control_c0_state[control_col] = not bool (msg.value)
                        note_old = transform (key)

                        # if we find a key that's held
                        if key_state[key]: 
                            # turn off the old note
                            mo.send (mido.Message ("note_on", note = note_old, velocity = 0))

                            # get the new note
                            control_c0_state[control_col] = bool (msg.value)
                            note_new = transform (key)

                            # turn off the new note if it's on, and then
                            # turn it on with the old note's original velocity
                            if note_state[note_new]: 
                                mo.send (mido.Message ("note_on", note = note_new, velocity = 0))
                            mo.send (mido.Message ("note_on", note = note_new, velocity = note_state[note_old]))

                            # record the new note and clear the old note
                            note_state[note_new] = note_state[note_old]
                            note_state[note_old] = 0
                    
                    # set the control state
                    control_c0_state[control_col] = bool (msg.value)
                    # print (control_col, control_c0_state[control_col], sep = ", ")

                elif control_row == 9: # top control keys
                    # tone-shift all midi notes of the column
                    for row in range (1, 9):
                        # get the key and the old note it's mapped to
                        key = row*10 + control_col
                        control_c9_state[control_col] = not bool (msg.value)
                        note_old = transform (key)

                        # if we find a key that's held
                        if key_state[key]: 
                            # turn off the old note
                            mo.send (mido.Message ("note_on", note = note_old, velocity = 0))

                            # get the new note
                            control_c9_state[control_col] = bool (msg.value)
                            note_new = transform (key)

                            # turn off the new note if it's on, and then
                            # turn it on with the old note's original velocity
                            if note_state[note_new]: 
                                mo.send (mido.Message ("note_on", note = note_new, velocity = 0))
                            mo.send (mido.Message ("note_on", note = note_new, velocity = note_state[note_old]))

                            # record the new note and clear the old note
                            note_state[note_new] = note_state[note_old]
                            note_state[note_old] = 0
                    
                    # set the control state
                    control_c9_state[control_col] = bool (msg.value)
                    # print (control_col, control_c9_state[control_col], sep = ", ")

            if msg.type == "note_on":
                key = msg.note
                note = transform (key)

                # turn off the note if it's on, and then
                # turn it on with the new velocity
                if msg.velocity and note_state[note]: 
                    mo.send (mido.Message ("note_on", note = note, velocity = 0))
                msg_to_send = mido.Message ("note_on", note = note, velocity = msg.velocity)

                # record the states
                key_state[key] = msg.velocity
                note_state[note] = msg.velocity

            mo.send (msg_to_send)

            if not msg.type == "clock" and not msg.type == "aftertouch":
                print (msg_to_send)
