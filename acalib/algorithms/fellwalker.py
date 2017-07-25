import numpy as np
import acalib
import pycupid
from astropy.nddata import *
from .algorithm import Algorithm
from .. import core


# storing unusable pixels for now (-1)
def _struct_builder(data, caa):
    dims = caa.shape
    clumps = dict()

    #2D data cube
    if len(dims)==2:
        for i in range(dims[0]):
            for j in range(dims[1]):
                if caa[i,j] in clumps:
                    clumps[caa[i,j]].append((i,j))
                else:
                    clumps[caa[i,j]] = [(i,j)]
    #3D data cube
    elif len(dims)==3:
        for i in range(dims[0]):
            for j in range(dims[1]):
                for k in range(dims[2]):
                    if caa[i,j,k] in clumps:
                        clumps[caa[i,j,k]].append((i,j,k))
                    else:
                        clumps[caa[i,j,k]] = [(i,j,k)]
    peaks = {}
    for i,pl in clumps.items():
        peaks[i] = None
        max_value = -float("inf")
        # for pixel position in pixel list
        for pp in pl:
            if data[pp] > max_value:
                max_value = data[pp]
                peaks[i] = pp

    return clumps,peaks

@support_nddata
def _fellwalker(data, config, wcs=None, mask=None, unit=None, rms=0.0):
    cube = data
    if len(data.shape) == 4:
        if data.shape[0] == 1:
            cube = data[0,:,:,:]
            if data.shape[1] == 1:
                cube = data[0,:,:]
    elif len(data.shape) == 3:
        if data.shape[0] == 1:
            cube = data[0,:,:]

    ret = pycupid.fellwalker(cube, rms,config=config)

    if ret is not None:
        ret[ret == ret.min()] = 0
        if wcs:
            return NDDataRef(ret, uncertainty=None, mask=None, wcs=wcs, meta=None, unit=unit)
        else:
            return ret
    else:
        return None


class FellWalker(Algorithm):

    def default_params(self):
        if 'FWHMBEAM' not in self.config:
            self.config['FWHMBEAM'] = 2.0
        if 'VELORES' not in self.config:
            self.config['VELORES'] =  2.0

    def run(self, data):
<<<<<<< HEAD
        if isinstance(data,NDData):
=======
        if type(data) is NDData or type(data) is NDDataRef:
>>>>>>> official/devel
            if len(data.data.shape) > 4:
                raise Exception("Algorithm only support 2D and 3D Matrices")
        else:
            if len(data.shape) > 4:
                raise Exception("Algorithm only support 2D and 3D Matrices")
        # if rms not in config, estimate it

        if 'RMS' not in self.config:
            if type(data) == NDData or type(data)== NDDataRef:
                rms = acalib.rms(data.data)
            else:
                rms = acalib.rms(data)
        else:
            rms = self.config['RMS']

        # computing the CAA through CUPID's fellwalker clumping algorithm
        caa = _fellwalker(data, self.config, rms=rms)

        # computing asocciated structures
        if caa is not None:
            clumps,peaks = _struct_builder(caa.data)

            return caa,clumps,peaks
        else:
            return None,None,None