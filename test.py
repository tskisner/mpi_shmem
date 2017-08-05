##
##  Copyright (c) 2017, all rights reserved.  Use of this source code 
##  is governed by a BSD license that can be found in the top-level
##  LICENSE file.
##

from mpi4py import MPI

import numpy as np
import numpy.testing as nt

from shmem import MPIShared


comm = MPI.COMM_WORLD
rank = comm.rank
procs = comm.size

# Dimensions of our shared memory array
datadims = (2, 2, 10)

# Data type of our shared memory array
datatype = np.float64

# For testing the "set()" method, every process is going to
# create a full-sized data buffer and fill it with its process rank.
local = np.ones(datadims, dtype=datatype)
local *= rank

# A context manager is the pythonic way to make sure that the
# object has no dangling reference counts after leaving the context,
# and will ensure that the shared memory is freed properly.

with MPIShared(local.shape, local.dtype, comm) as shm:

    for p in range(procs):
        # Every process takes turns writing to the buffer.
        if p == rank:
            # My turn!  Write my process rank to the whole buffer.
            shm.set(local, (0, 0, 0), rank)
        # Everybody wait...
        comm.barrier()

        # Every process is now going to read a copy from the shared memory 
        # and make sure that they see the data written by the current process.
        check = np.zeros_like(local)
        check[:,:,:] = shm[:,:,:]

        # This should be bitwise identical, even for floats
        nt.assert_equal(check, p)
