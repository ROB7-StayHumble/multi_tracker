import numpy as np

# Drift dynamics (constant velocity model)
phi = np.matrix([[1, 1, 0, 0],
                 [0, 1, 0, 0],
                 [0, 0, 1, 1],
                 [0, 0, 0, 1]])

# Observation dynamics (observe position and velocity)
H   = np.matrix([[1, 0, 0, 0],
                 [0, 0, 1, 0]])

# Initial covariance
P0  = 10*np.eye(4)

# Dynamics covariance
Q   = 0.2*np.matrix(np.eye(4))

# Observation covariance
R   = 5*np.matrix(np.eye(2))

#
# ### Define kalman filter properties ########
# phi = np.matrix([                    [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
#                                      [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
#                                      [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
#                                      [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
#                                      [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
#                                      [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
#                                      [0, 0, 0, 0, 0, 0, 1, 1, 0, 0],
#                                      [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
#                                      [0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
#                                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]])
#
# H   = np.matrix([                    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                                      [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
#                                      [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
#                                      [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
#                                      [0, 0, 0, 0, 0, 0, 0, 0, 1, 0]])
# P0  = 10*np.eye(10)
# Q   = .2*np.matrix(np.eye(10))
# R   = 50*np.matrix(np.eye(5))

gamma  = None
gammaW = None

max_covariance = 200
max_velocity = 500

association_matrix = np.matrix([[1,1]], dtype=float).T
association_matrix /= np.linalg.norm(association_matrix)
