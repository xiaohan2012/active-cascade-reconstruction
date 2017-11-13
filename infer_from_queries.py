
# coding: utf-8

# In[10]:


import os
import pickle as pkl
from helpers import load_cascades
from inference import infection_probability
from graph_helpers import load_graph_by_name
from tqdm import tqdm
from joblib import Parallel, delayed


# In[2]:


graph_name = 'dolphin'


# In[3]:


query_dirname = 'outputs/queries/'
inf_proba_dirname = 'outputs/inf_probas'


# In[4]:


g =load_graph_by_name(graph_name)


# In[5]:


cascades = load_cascades('cascade/' + graph_name)


# In[6]:


methods = ['pagerank', 'random', 'entropy', 'prediction_error']


# In[8]:


def one_round(g, obs, c, c_path, method, query_dirname, inf_proba_dirname):
    obs_tmp = obs.tolist()
    # loop
    cid = os.path.basename(c_path).split('.')[0]
    query_log_path = os.path.join(query_dirname, graph_name, method, '{}.pkl'.format(cid))
    queries, _ = pkl.load(open(query_log_path, 'rb'))

    probas_list = []
    for q in queries:
        obs_tmp.append(q)
        probas = infection_probability(g, obs_tmp, n_samples=100)
        probas_list.append(probas)

    probas_dir = os.path.join(inf_proba_dirname, graph_name, method)
    if not os.path.exists(probas_dir):
        os.makedirs(probas_dir)
    path = os.path.join(probas_dir, '{}.pkl'.format(cid))
    pkl.dump(probas_list, open(path, 'wb'))


# In[11]:


Parallel(n_jobs=-1)(delayed(one_round)(g, obs, c, c_path, method, query_dirname, inf_proba_dirname)
                    for path, (obs, c) in tqdm(cascades)
                    for method in methods)

