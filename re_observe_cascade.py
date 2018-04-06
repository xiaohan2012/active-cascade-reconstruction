import pickle as pkl
import os
from cascade_generator import observe_cascade
from helpers import cascade_source
from glob import glob

graph = 'nethept'
from_obs = 0.2
from_dir = 'cascade-weighted/{}-mic-s0.02-o{}/'.format(graph, from_obs)

target_obs_list = [0.1, 0.3, 0.4, 0.5]

for target_obs in target_obs_list:
    print('target_obs', target_obs)
    to_dir = 'cascade-weighted/{}-mic-s0.02-o{}/'.format(graph, target_obs)

    if not os.path.exists(to_dir):
        os.makedirs(to_dir)

    for input_path in glob(from_dir + '*'):
        # print('input_path', input_path)
        id_ = os.path.basename(input_path)
        _, c = pkl.load(open(input_path, 'rb'))[:2]
        s = cascade_source(c)
        
        obs = observe_cascade(c, s, target_obs, 'uniform')
        
        output_path = to_dir + id_
        # print('output_path', output_path)
        pkl.dump((obs, c, None), open(output_path, 'wb'))
    
