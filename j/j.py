from argparse import ArgumentParser


def main():

    args = _parse_arguments()

    print(args)


def _parse_arguments():

    parser = ArgumentParser(description='Tool to generate html-based Jeopardy')

    parser.add_argument('definition_file', type=str, help='The path to the definition file')

    args = vars(parser.parse_args())

    return args

