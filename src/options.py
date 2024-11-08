import argparse


def __add_options(parser):
    parser.add_argument("--config_path", dest='config_path', default=None,
                        help='Different location for configuration file.')

    parser.add_argument("--testing_file", dest='testing_file', default=None,
                        help='Override the feed setting and use a local json file for testing.')

    return parser


def __args_parser(description='Waze Travel Times Poller'):
    # get command line arguments, if any
    parser = argparse.ArgumentParser(description=description)
    __add_options(parser)
    args = parser.parse_args()
    return args
