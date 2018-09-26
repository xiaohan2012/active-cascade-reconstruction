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
