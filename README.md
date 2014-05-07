gadget-snapshot-reader (GSR)
============================

Python module to read binary snapshots from Gadget.

Usage
------

For a simple transformation from the gadget-binary file
to ascii, you can do the following:

```python
from gsr import *

snap = Snapshot(filename)
snap.to_ascii()
```

Every ascii file is generated using the following order:

| id | mass | posx | posy | posz | velx | vely | velz |

If you want to print certain information from the snapshot
by type:

```python
particle_type = 5  # From GADGET, only 0, 1, 2, 3, 4, 5
snap.print_data_by_type(particle_type)
```

To use the data from the snapshot, it's possible to get
a list with all the information of a particle type:

```python
particle_type = 5
data = snap.get_data_by_type(particle_type)
```

which will return a list with the following structure
in the order *ids, masses, positions, velocities*:

```python
[[id0, id1, ...],[mass0, mass1, ...], [[pos0x, pos0y, pos0z], [pos1x, pos1y, pos2z]], [[vel0x, vel0y, vel0z], [vel1x, vel1y, vel1z], ...]]
```
