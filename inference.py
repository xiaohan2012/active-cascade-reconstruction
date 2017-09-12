from minimum_steiner_tree import min_steiner_tree


def infer_infected_nodes(g, obs):
    """besides observed infections, infer other infected nodes"""
    st = min_steiner_tree(g, obs)
    remain_infs = set(map(int, st.vertices()))
    return remain_infs
