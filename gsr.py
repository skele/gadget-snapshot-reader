#!/usr/bin/python
##import numpy as np
import struct

class Snapshot:
    def getRecordLength(self, instring):
        "Takes a string of some length and interprets it as a series of bits"
        return struct.unpack('i',instring)[0]

    def unpackHeader(self, instring):
        fmtstring = "6i8f10i{0:d}x".format(self.headerlength-96)
        everything = struct.unpack(fmtstring,instring)
        #list of 6 items giving number of each particle
        self.Npart = everything[1:6]
        #mass array
        self.mpart = everything[7:12]

    def ProcessHeader(self):
        self.headerlength = self.getRecordLength(self.binfile.read(4))
        header = self.binfile.read(self.headerlength)
        self.unpackHeader(header)

    def ProcessBody(self):
        nbytes = self.getRecordLength(self.binfile.read(4))
        print nbytes
        body = self.binfile.read(nbytes)

    def __init__(self, filename):
        self.binfile = open(filename,"rb")
        #Process header
        self.ProcessHeader()
        self.ProcessBody()

if __name__ == '__main__':
    print "initializing some snapshot..."
    newsnap = Snapshot("snapshot_001")
    print "done"

