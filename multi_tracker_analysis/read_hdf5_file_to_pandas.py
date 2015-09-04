import numpy as np
import h5py
import copy
import pandas
import os

def get_filenames(path, contains):
    cmd = 'ls ' + path
    ls = os.popen(cmd).read()
    all_filelist = ls.split('\n')
    try:
        all_filelist.remove('')
    except:
        pass
    filelist = []
    for i, filename in enumerate(all_filelist):
        if contains in filename:
            filelist.append( os.path.join(path, filename) )
    return filelist

class Trajectory(object):
    def __init__(self, pd, objid):
        self.pd = pd[pd['objid']==objid]
        
        for column in self.pd.columns:
            self.__setattr__(column, self.pd[column])
        
class Dataset(object):
    def __init__(self, pd):
        self.pd = pd
        self.keys = []
        self.__processed_trajecs__ = {}
    
    def trajec(self, key):
        return Trajectory(self.pd, key)
    
    def framestamp_to_timestamp(self, frame):
        t = self.pd.ix[frame]['time_epoch']
        try:
            return t.iloc[0]
        except:
            return t
            
    def timestamp_to_framestamp(self, t):
        try:
            pd_subset = self.pd[self.pd['time_epoch_secs']==np.floor(t)]
            return np.argmin(pd_subset['time_epoch'] - t)
        except:
            return np.argmin(self.pd['time_epoch'] - t)
        
def load_data_as_pandas_dataframe_from_hdf5_file(filename, attributes=None):
    data = h5py.File(filename, 'r')['data']
    if attributes is None:
        attributes = {   'objid'                : 'objid',
                         'time_epoch_secs'      : 'header.stamp.secs',
                         'time_epoch_nsecs'     : 'header.stamp.nsecs',
                         'position_x'           : 'position.x',
                         'position_y'           : 'position.y',
                         'velocity_x'           : 'velocity.x',
                         'velocity_y'           : 'velocity.y',
                         'angle'                : 'angle',
                         'frames'               : 'header.frame_id'}
    index = data['header.frame_id'].flat
    d = {}
    for attribute, name in attributes.items():
        d.setdefault(attribute, data[name].flat)
    pd = pandas.DataFrame(d, index=index)
    pd = pd.drop(pd.index==[0]) # delete 0 frames (frames with no data)
    pd = calc_additional_columns(pd)
    # pd_subset = pd[pd.objid==key]
    return pd
    
def calc_additional_columns(pd):
    pd['time_epoch'] = pd['time_epoch_secs'] + pd['time_epoch_nsecs']*1e-9
    pd['speed'] = np.linalg.norm( [pd['velocity_x'], pd['velocity_y']] )
    return pd
    
def framestamp_to_timestamp(pd, frame):
    return pd.ix[frame]['time_epoch'].iloc[0]
        
def timestamp_to_framestamp(pd, t):
    pd_subset = pd[pd['time_epoch_secs']==np.floor(t)]
    return np.argmin(pd_subset['time_epoch'] - t)

def pixels_to_units(pd, pixels_per_unit, center=[0,0]):
    attributes = ['speed',
                  'position_x',
                  'position_y',
                  'velocity_x',
                  'velocity_y',
                  ]
    for attribute in attributes:
        pd[attribute] = pd[attribute] / pixels_per_unit
    
    return pd

def load_multiple_datasets_into_single_pandas_data_frame(filenames, sync_frames=None):
    '''
    filenames   - list of hdf5 files to load, full path name
    sync_frames - list of frames, one for each filename, these sync_frames will all be set to zero
                  defaults to using first frame for each dataset as sync

    '''

    pds = [load_data_as_pandas_dataframe_from_hdf5_file(filename) for filename in filenames]
    if sync_frames is None:
        sync_frames = [np.min(pd.frames) for pd in pds]
        
    for i, pd in enumerate(pds):
        pd.index -= sync_frames[i]
        pd.frames -= sync_frames[i]
    
    combined_pd = pandas.concat(pds)
    
    return combined_pd











