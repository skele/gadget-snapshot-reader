#!/usr/bin/env python

import os.path
import struct
import numpy as np
import sys

class Snapshot:
    """Class in charge of the read-process of every snapshot"""

    def __init__(self, filename):
        if os.path.isfile(filename):
            self.fname = filename
            self.binfile = open(self.fname, "rb")
            self.SnapshotData = {}

            # Process header
            self.SnapshotData['header'] = self.ProcessHeader()
            self.SnapshotData['pos'] = self.ProcessParticlesPos()
            self.SnapshotData['vel'] = self.ProcessParticlesVel()
            self.SnapshotData['ids'] = self.ProcessParticlesIds()
            self.SnapshotData['mass'] = self.ProcessParticlesMass()
        else:
            print(filename, ": No such file")
            sys.exit(1)

    def __exit__(self):
        self.binfile.close()

    def getRecordLength(self, instring):
        "Takes a string of some length and interprets it as a series of bits"
        return struct.unpack('i', instring)[0]

    # Header processing
    def ProcessHeader(self):
        # because at the end another field is reserved for the length again
        self.headerlength = self.getRecordLength(self.binfile.read(4)) + 4
        header = self.binfile.read(self.headerlength)
        return self.unpackHeader(header)

    def unpackHeader(self, instring):
        fmtstring = "6i8d9i{0:d}x".format(self.headerlength-124)
        everything = struct.unpack(fmtstring, instring)
        # list of 6 items giving number of each particle
        self.Npart = np.array(everything[:6])
        self.mpart = np.array(everything[6:12])
        self.time = everything[12]
        self.Ntot = self.Npart.sum()
        return {'Npart': self.Npart,
                'Mpart': self.mpart,
                'Time': self.time,
                'Ntot': self.Ntot}

    # Positions processing
    def ProcessParticlesPos(self):
        nbytes = self.getRecordLength(self.binfile.read(4)) + 4
        body = self.binfile.read(nbytes)
        return self.unpackPositions(body)

    def unpackPositions(self, instring):
        fmtstring = "{0:d}f4x".format(self.Ntot*3)
        everything = struct.unpack(fmtstring, instring)
        self.pos = [np.zeros((i, 3)) for i in self.Npart]

        offset = 0
        for i in range(6):
            chunk = everything[offset*3:offset*3+self.Npart[i]*3]
            self.pos[i] = np.reshape(chunk, (self.Npart[i], 3))
            offset += self.Npart[i]
        return self.pos

    # Velocities processing
    def ProcessParticlesVel(self):
        nbytes = self.getRecordLength(self.binfile.read(4)) + 4
        body = self.binfile.read(nbytes)
        return self.unpackVelocities(body)

    def unpackVelocities(self, instring):
        fmtstring = "{0:d}f4x".format(self.Ntot*3)
        everything = struct.unpack(fmtstring, instring)

        self.vel = [np.zeros((i, 3)) for i in self.Npart]

        offset = 0
        for i in range(6):
            chunk = everything[offset*3:offset*3 + self.Npart[i]*3]
            self.vel[i] = np.reshape(chunk, (self.Npart[i], 3))
            offset += self.Npart[i]
        return self.vel

    # Ids processing
    def ProcessParticlesIds(self):
        nbytes = self.getRecordLength(self.binfile.read(4)) + 4
        body = self.binfile.read(nbytes)
        return self.unpackIDs(body)

    def unpackIDs(self, instring):
        fmtstring = "{0:d}i4x".format(self.Ntot)
        everything = struct.unpack(fmtstring, instring)

        self.ID = [np.zeros(i, dtype=np.int) for i in self.Npart]

        offset = 0
        for i in range(6):
            chunk = everything[offset:offset+self.Npart[i]]
            self.ID[i] = np.array(chunk, dtype=np.int)
            offset += self.Npart[i]
        return self.ID

    # Mass processing
    def ProcessParticlesMass(self):
        nbytes = self.getRecordLength(self.binfile.read(4)) + 4
        body = self.binfile.read(nbytes)
        return self.unpackMasses(body)

    def unpackMasses(self, instring):
        self.m = [np.zeros(i) for i in self.Npart]
        missing_masses = 0

        for i in range(6):
            total = self.Npart[i]
            mass = self.mpart[i]

            if total > 0:
                if mass == 0:
                    missing_masses += total
                elif mass > 0:
                    self.m[i].fill(mass)

        fmtstring = "{0:d}f4x".format(missing_masses)
        everything = struct.unpack(fmtstring, instring)


        offset = 0
        for i in range(6):
            if self.Npart[i] > 0 and self.mpart[i] == 0:
                chunk = everything[offset:offset+self.Npart[i]]
                self.m[i] = np.array(chunk)
                offset += self.Npart[i]

        return self.m

    # Utils

    def computeCOM(self, parts=range(6)):
        '''
        Computes center of mass for all the particle types
        given in the list parts,
        default all
        '''
        com = np.zeros(3)
        totM = 0.0
        for i in parts:
            for j in range(self.Npart[i]):
                com += self.pos[i][j, :]*self.m[i][j]
                totM += self.m[i][j]
        com = com/totM
        self.com = com

    def to_ascii(self):
        def get_tuple(key):
            return tuple(i for i in self.SnapshotData[key])

        ids = np.concatenate(get_tuple('ids'), axis = 0)
        mass = np.concatenate(get_tuple('mass'), axis = 0)
        pos = np.concatenate(get_tuple('pos'), axis = 0)
        vel = np.concatenate(get_tuple('vel'), axis = 0)

        fmtstring = ['%8d', '%1.5e',
                     '% 1.5e', '% 1.5e', '% 1.5e',
                     '% 1.5e', '% 1.5e', '% 1.5e']

        np.savetxt(fname+'.asc',
                   np.hstack([zip(ids, mass), pos, vel]),
                   fmt=fmtstring)

    def get_data_by_type(self, ptype):
        return [self.SnapshotData['ids'][ptype],
               self.SnapshotData['mass'][ptype],
               self.SnapshotData['pos'][ptype],
               self.SnapshotData['vel'][ptype]]

    def print_data_by_type(self, ptype):
        for i in range(self.Npart[ptype]):
            pid = self.SnapshotData['ids'][ptype][i]
            mass = self.SnapshotData['mass'][ptype][i]
            posx, posy, posz = self.SnapshotData['pos'][ptype][i]
            velx, vely, velz = self.SnapshotData['vel'][ptype][i]

            print('%8d %1.5e % 1.5e % 1.5e % 1.5e % 1.5e % 1.5e % 1.5e' % (pid, mass, posx, posy, posz, velx, vely, velz))

## Print utils
#
#def print_header(snap):
#    for key, val in snap.SnapshotData['header'].iteritems():
#        print(key, val)
#
#
#def print_pos(snap):
#    ptype = 0
#    for p in snap.SnapshotData['pos']:
#        print("Type", ptype, p)
#        ptype += 1
#
#
#def print_vel(snap):
#    vtype = 0
#    for v in snap.SnapshotData['vel']:
#        print("Type", vtype, v)
#        vtype += 1
#
#
#def print_ids(snap):
#    itype = 0
#    for i in snap.SnapshotData['ids']:
#        print("Type", itype, i)
#        itype += 1
#
#
#def print_mass(snap):
#    mtype = 0
#    for m in snap.SnapshotData['mass']:
#        print("Type", mtype, m)
#        mtype += 1

