import argparse


def __add_options(parser):
    parser.add_argument("--config_path", dest='config_path', default='..\\configs\\config.ini',
                        help='Different location for configuration file.')

    return parser


def __args_parser(description='Waze Travel Times Poller'):
    # get command line arguments, if any
    parser = argparse.ArgumentParser(description=description)
    __add_options(parser)
    args = parser.parse_args()
    return args
