from core import SIMULATION_METHODS


def add_input_args(parser):
    parser.add_argument('-g', '--graph',
                        required=True,
                        help='graph name')
    parser.add_argument('--dataset',
                        required=True,
                        help='dataset id, e.g. lattice-100-msi-s0.25-o0.25-omuniform')
    parser.add_argument('-f', '--graph_suffix',
                        required=True,
                        help='suffix of graph name')
    parser.add_argument('-c', '--cascade_path',
                        help='path of generated cascade')

    
def add_query_method_args(parser):
    parser.add_argument('-q', '--query_method',
                        required=True,
                        choices={'random',
                                 'pagerank',
                                 'entropy',
                                 'cond-entropy',
                                 'mutual-info',
                                 'oracle-e',
                                 'oracle-l'},
                        help='query strategy')
    # following applies to sampler approach
    parser.add_argument('-n', '--n_queries', default=10, type=int,
                        help='number of queries')
    parser.add_argument('-m', '--query_sampling_method', default='loop_erased', type=str,
                        choices=('loop_erased', 'cut') + SIMULATION_METHODS,
                        help='the steiner tree sampling method')
    parser.add_argument('-r', '--root_sampler', type=str,
                        default='pagerank',
                        choices={'pagerank', 'random', 'true_root'},
                        help='the steiner tree sampling method')
    parser.add_argument('-s', '--query_n_samples', default=100, type=int,
                        help='number of samples')

    # specific to cond-entropy sampler
    parser.add_argument('-p', '--min_proba', default=0.0, type=float,
                        help='(minimum) threshold used for pruning candidate nodes')
    parser.add_argument('-e', '--num_estimation_nodes', default=None, type=int,
                        help='number of nodes used for error estimation')

    # specific to pagerank root sampler
    parser.add_argument('--root_pagerank_noise', default=0.0, type=float,
                        help='the epsilon value for pagerank root sampling, the higher the more noisy')

    
def add_cascade_parameter_args(parser):
    # cascade parameters
    parser.add_argument(
        '--infection_proba',
        default=0.5,
        type=float,
        help='infection probability of the cascade generation model'
    )
    parser.add_argument(
        '--cascade_size',
        default=0.1,
        type=float,
        help='cascade size, e.g, fraction of nodes that are infected'
    )
    parser.add_argument(
        '--cascade_model',
        default='si',
        choices=('si', 'ic'),
        type=str,
        help='cascade model'
    )
    return parser


def add_inference_args(parser):
    # inference related
    parser.add_argument('--inference_sampling_method',
                        default='simulation',
                        choices=('loop_erased', 'cut') + SIMULATION_METHODS,
                        help='')    
    parser.add_argument('--inference_n_samples', type=int,
                        default=100,
                        help='number of samples')
    parser.add_argument('--infer_every',
                        default=1,
                        type=int,
                        help='evaluate every ?')
    


def add_eval_args(parser):
    parser.add_argument(
        '--metric_name',
        choices=('ap', 'auc', 'p@k', 'entropy', 'map', 'mrr', 'n',
                 'ratio_discovered_inf', 'l1', 'l2', 'cross_entropy'),
        help='evalulation method'
    )
    parser.add_argument(
        '--eval_with_mask',
        action="store_true",
        help='whether evaluate with masks or not. If True, queries and obs are excluded'
    )


def add_debug_args(parser):
    parser.add_argument(
        '-b', '--debug',
        action='store_true', help='whether debug or not'
    )
    parser.add_argument(
        '-v', '--verbose', type=int, default=0,
        help='vebose level to be used'
    )
