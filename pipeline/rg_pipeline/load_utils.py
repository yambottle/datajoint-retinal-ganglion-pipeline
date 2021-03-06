import os
import pickle
import numpy as np

from rg_pipeline.ingest.experiment import Session, Subject, Stimulation, SpikeGroup, Spike
import rg_pipeline.compute_utils as cpt_util

def load_file_pickle(datasource:dict):
    """
    Implementation of load() specifically for pickle files

    :param datasource: a dictionary including pickle file path
    """
    # TODO - Maybe can optimize this process by https://docs.datajoint.io/python/computation/01-autopopulate.html#auto-populate
    if os.path.exists(datasource['path']):
        with open(datasource['path'], 'rb') as datafile:
            data = pickle.load(datafile)

        subject_names = Subject.fetch('subject_name')
        subjects = []
        sessions = []
        session_id = len(Session.fetch('session_id'))+1
        stimulations = []
        stimulation_idx = len(Stimulation.fetch('stimulation_id'))+1
        spike_groups = []
        spike_group_idx = len(SpikeGroup.fetch('spike_group_id'))+1
        spikes = []
        for session in data:
            # Subject
            if session['subject_name'] not in subject_names:
                # print("Insert subject: {}".format(session['subject_name']))
                # Subject.insert1([
                subjects.append([ 
                    None,
                    session['subject_name']
                ])
                subject_names = np.append(subject_names, session['subject_name'])
            
            # Session 
            # Session.insert1([ 
            sessions.append([
                None,
                session['sample_number'], 
                session['session_date'], 
                np.where(subject_names==session['subject_name'])[0][0]+1,
            ])

            for idx in range(len(session['stimulations'])):
                # Stimulations
                stimulation = session['stimulations'][idx]
                # print("Insert stimulation: {}".format(stimulation_idx))
                # Stimulation.insert1([ 
                stimulations.append([
                    None,
                    stimulation['fps'], 
                    stimulation['movie'].tobytes(),
                    "{}".format(stimulation['movie'].shape), 
                    stimulation['n_frames'], 
                    stimulation['pixel_size'], 
                    stimulation['stim_height'], 
                    stimulation['stim_width'], 
                    stimulation['stimulus_onset'], 
                    stimulation['x_block_size'], 
                    stimulation['y_block_size'],
                    session_id
                ])
                # Spikes of one stimulation 
                for spike_group in stimulation['spikes']:
                    # print("Insert spike_group: {}".format(spike_group_idx))
                    # SpikeGroup.insert1([
                    spike_groups.append([
                        None, 
                        stimulation_idx,
                    ])
                    for spike_idx in range(len(spike_group)):
                        spike_time = spike_group[spike_idx]
                        spike_movie_time = spike_time[0]-stimulation['stimulus_onset']
                        # sta = cpt_util.get_sta(stimulation, stimulation['movie'], spike_movie_time, cpt_util.STA_DELAY)
                        sta = None
                        spikes.append([
                            None,
                            spike_time[0],
                            spike_movie_time,
                            None,
                            spike_group_idx
                        ])
                        # Memory Error: if use spikes array
                        # if sta is not None:
                        #     print("Insert spike with STA")
                        #     Spike.insert1([
                        #         None,
                        #         spike_time[0],
                        #         spike_movie_time,
                        #         sta.tobytes(),
                        #         spike_group_idx
                        #     ])
                        # else:
                        #     print("Insert spike without STA")
                        #     Spike.insert1([
                        #         None,
                        #         spike_time[0],
                        #         spike_movie_time,
                        #         None,
                        #         spike_group_idx
                        #     ])
                    spike_group_idx += 1
                    # raise ValueError("debug stop")
                stimulation_idx += 1
            session_id += 1

        print("Loading Subjects...")
        Subject.insert(subjects)
        print(Subject.fetch())
        
        print("Loading Sessions...")
        Session.insert(sessions)
        print(Session.fetch())

        print("Loading Stimulations...")
        Stimulation.insert(stimulations)
        print(Stimulation.fetch('stimulation_id', 'fps', 'n_frames', 'pixel_size', 'stimulus_onset', 'session_id'))

        print("Loading SpikeGroups...")
        SpikeGroup.insert(spike_groups)
        print(SpikeGroup.fetch())

        print("Loading Spikes...")
        Spike.insert(spikes)
        print(Spike.fetch('spike_id', 'spike_time', 'spike_movie_time', 'spike_group_id'))

    else:
        raise FileNotFoundError

# TODO - since these data sources are not required in this specific task, ignore these implementation for now
# def load_file_csv(datasource:dict):
#     pass

# def load_file_parquet(datasource:dict):
#     pass

# def load_file_json(datasource:dict):
#     pass

# def load_database_mysql(datasource:dict):
#     pass

# def load_database_mssql(datasource:dict):
#     pass

# def load_database_mongodb(datasource:dict):
#     pass

# def load_request_json(datasource:dict):
#     pass