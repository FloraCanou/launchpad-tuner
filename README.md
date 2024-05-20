# Launchpad Tuner

This Python 3 script can be used to remap the Novation Launchpad to various isomorphic layouts. 

**NOTE: this script is in alpha stage. Existing stuff should work okay, but there are still some features to implement.**

## Requirements

- [Mido](https://mido.readthedocs.io/)
- [python-rtmidi](https://spotlightkid.github.io/python-rtmidi/)

```
pip install mido python-rtmidi
```

The device must be plugged in with latest firmware and be in programmer mode. Also requires [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html) on Windows. 

## Usage

```
from lpt_main import *
chromatic (n)
```
where `n` is the edo number. 

On running, please take note of the command prompt. A base MIDI note is suggested for each register. 

## Features
### Isomorphic Layout

The pads are mapped in a (tone - step, step) layout, so that each step along the main diagonal direction (bottom-left to top-right) ascends by a whole tone. 

The number of steps of the whole tone is automatically calculated for *n*-edo using the 2.9 subgroup interpretation. Edos whose fifth has more than 1/2 relative error are considered dual-fifth. 

The *base note* is the theoretical note to the bottom left of the pads (where *setup* is). This note takes MIDI note value 0 and is assumed to be a Cb. Hence, the following notes fill the main diagonal line, and are invariant in all edos: low Db, Eb, F, G, A, B, C#, and high D#. 

### Lighting

For plain-fifth edos, the chromatic scale is lit as follows. 

| Note    | Color                |
| ------- | -------------------- |
| Low Db  | Gray                 |
| Low D   | Red                  |
| Eb      | Orange               |
| E       | Yellow               |
| F       | Chartreuse           |
| F#      | Green                |
| G       | Spring               |
| G#      | Cyan #1 (aquamarine) |
| Ab      | Cyan #2 (capri)      |
| A       | Azure                |
| Bb      | Blue                 |
| B       | Violet               |
| C       | Magenta              |
| C#      | Rose                 |
| High D  | Red                  |
| High D# | Gray                 |

### Extending the Range

The low Db and high D# are nominally the lowest and highest notes available in this layout, respectively, and that covers the principal range for just over an octave. 

#### Register Keys

The left-hand side control keys act as register keys, each bumps the corresponding *row* by a full octave, essentially doubling the range of the instrument. 

Holding a register key while playing an affected note will bump the note to the second register, whereas releasing the register key will simply turn off the note. This is designed to facilitate playing in the second register. 

#### Tone-Shifting Keys

The top and bottom control keys act as tone-shifting keys. Each top control key raises the corresponding *column* by a whole tone, enabling the access to the range of high E to high E#. Each bottom control key lowers the corresponding *column* by the same amount, enabling the access to the range of low C to low Cb. 

Like the register keys, holding a tone-shifting key while playing an affected note will shift the note's pitch. Unlike the register keys, releasing a tone-shifting key will shift the note's pitch back to the original. 

## Edo Size Limitations

The edo size is limited by the layout as well as the MIDI standard. 

:large_blue_circle:**1–50**

Full two-and-a-half-octave range is supported.

:green_circle:**51–55**

Similar to smaller edos but notes below low C and above high E are compromised. 

:yellow_circle:**56–85**

Some notes are skipped and higher notes of the second register are increasingly unavailable. At the large end only one register's range is guaranteed. 

:orange_circle:**86–91**

Many notes are skipped and certain tone-shifted lowest and highest notes of the first register are also compromised. 

:red_circle:**92+**

An error will be raised. 
