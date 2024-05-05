# © 2024 Flora Canou, based on Godtone's work
# This work is licensed under the AGPLv3 <https://www.gnu.org/licenses/agpl-3.0.html>

import mido # pip install mido
import platform, warnings # to check whether we're running Windows, in which case we want to use loopMIDI

def get_io_list ():
    mi_names = mido.get_input_names ()
    mo_names = mido.get_output_names ()
    return mi_names, mo_names

def select_launchpad_ports ():
    mi_names, mo_names = get_io_list ()
    if mi_names := [entry for entry in mi_names if "LP" in entry or "Launchpad" in entry]:
        mi_name = mi_names[0]
    else:
        raise OSError ("Launchpad input port not detected. Is Launchpad plugged in?")
    if mo_names := [entry for entry in mo_names if "LP" in entry or "Launchpad" in entry]:
        mo_name = mo_names[0]
    else:
        raise OSError ("Launchpad output port not detected. Is Launchpad plugged in?")
    print (f"Selecting Launchpad ports:\n* {mi_name}\n* {mo_name}")
    return mi_name, mo_name

def select_loopmidi_ports ():
    if platform.system () == "Windows":
        mi_names, mo_names = get_io_list ()
        if mi_names := [entry for entry in mi_names if "loopMIDI" in entry]:
            mi_name = mi_names[0]
        else:
            warnings.warn ("loopMIDI input port not detected.")
            mi_name = None
        if mo_names := [entry for entry in mo_names if "loopMIDI" in entry]:
            mo_name = mo_names[0]
        else:
            warnings.warn ("loopMIDI output port not detected.")
            mo_name = None
    else:
        mi_name, mo_name = None, None

    print (f"Selecting loopMIDI ports:\n* {mi_name}\n* {mo_name}")
    return mi_name, mo_name

mi_launchpad_name, mo_launchpad_name = select_launchpad_ports ()
mi_loopmidi_name, mo_loopmidi_name = select_loopmidi_ports ()
