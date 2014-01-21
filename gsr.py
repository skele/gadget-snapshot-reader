#!/usr/bin/python
import struct
import numpy as np

class Snapshot:
    def getRecordLength(self, instring):
        "Takes a string of some length and interprets it as a series of bits"
        return struct.unpack('i',instring)[0]

    def unpackHeader(self, instring):
        fmtstring = "6i8d9i{0:d}x".format(self.headerlength-124)
        everything = struct.unpack(fmtstring,instring)
        #list of 6 items giving number of each particle
        self.Npart = np.array(everything[:6])
        #mass array
        self.mpart = np.array(everything[6:12])
        self.time = everything[12]
        self.Ntot = sum(self.Npart)

    def unpackPositions(self, instring):
        fmtstring = "{0:d}f4x".format(self.Ntot*3)
        everything = struct.unpack(fmtstring,instring)
        self.pos = [np.zeros((i,3)) for i in self.Npart]

        offset = 0
        for i in range(6):
            for j in range(self.Npart[i]):
                for k in range(3):
                    self.pos[i][j,k] = everything[offset*3 + j*3 + k]
            offset += self.Npart[i]

    def unpackVelocities(self, instring):
        fmtstring = "{0:d}f4x".format(self.Ntot*3)
        everything = struct.unpack(fmtstring,instring)

        self.vel = [np.zeros((i,3)) for i in self.Npart]

        offset = 0
        for i in range(6):
            for j in range(self.Npart[i]):
                for k in range(3):
                    self.vel[i][j,k] = everything[offset*3 + j*3 + k]
            offset += self.Npart[i]

    def unpackIDs(self, instring):
        fmtstring = "{0:d}i4x".format(self.Ntot)
        everything = struct.unpack(fmtstring,instring)

        self.ID = [np.zeros(i,dtype=np.int) for i in self.Npart]

        offset = 0
        for i in range(6):
            for j in range(self.Npart[i]):
                self.ID[i][j] = everything[offset + j]
            offset += self.Npart[i]

    def unpackMasses(self, instring):
        fmtstring = "{0:d}f4x".format(self.Ntot)
        everything = struct.unpack(fmtstring,instring)

        self.m = [np.zeros(i) for i in self.Npart]

        offset = 0
        for i in range(6):
            for j in range(self.Npart[i]):
                self.m[i][j] = everything[offset + j]
            offset += self.Npart[i]

    def ProcessHeader(self):
        self.headerlength = self.getRecordLength(self.binfile.read(4)) + 4 #because at the end another field is reserved for the length again
        header = self.binfile.read(self.headerlength)
        self.unpackHeader(header)

    def ProcessBody(self):
        nbytes = self.getRecordLength(self.binfile.read(4)) + 4
        #now positions
        body = self.binfile.read(nbytes)
        self.unpackPositions(body)

        nbytes = self.getRecordLength(self.binfile.read(4)) + 4
        body = self.binfile.read(nbytes)
        self.unpackVelocities(body)

        nbytes = self.getRecordLength(self.binfile.read(4)) + 4
        body = self.binfile.read(nbytes)
        self.unpackIDs(body)

        nbytes = self.getRecordLength(self.binfile.read(4)) + 4
        body = self.binfile.read(nbytes)
        self.unpackMasses(body)

    def computeCOM(self,parts=range(6)):
        '''
        Computes center of mass for all the particle types given in the list parts, default all
        '''
        com = np.zeros(3)
        totM = 0.0
        for i in parts:
            for j in range(self.Npart[i]):
                com += self.pos[i][j,:]*self.m[i][j]
                totM += self.m[i][j]
        com = com/totM
        self.com = com

    def __init__(self, filename):
        self.binfile = open(filename,"rb")
        #Process header
        self.ProcessHeader()
        #Process Body
        self.ProcessBody()

    def __exit__(self):
        self.binfile.close()

if __name__ == '__main__':
    print "initializing some snapshot..."
    newsnap = Snapshot("snapshot_001")
    print "Computing center of mass"
    newsnap.computeCOM()
    print newsnap.com

