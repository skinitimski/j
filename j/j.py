from argparse import ArgumentParser

from jinja2 import Environment, PackageLoader

from munch import munchify

from os import mkdir

from os.path import join

from yaml import safe_load


KEY_DEFINITION  = 'definition'
KEY_DESTINATION = 'destination'

STYLE = 'style.css'

JINJA_ENV = Environment(loader=PackageLoader('j'))

def main():

    args = _parse_arguments()

    j(args[KEY_DEFINITION], args[KEY_DESTINATION])



def j(definition_path, destination_path):

    mkdir(destination_path)

    _copy_style(destination_path)

    definition = _read_definition(definition_path)

    template_round    = JINJA_ENV.get_template('round.html')
    template_answer   = JINJA_ENV.get_template('answer.html')
    template_question = JINJA_ENV.get_template('question.html')

    for round_index, round_definition in enumerate(definition.Rounds):

        with open(join(destination_path, f'round{round_index}.html'), 'w') as f:

            f.write(template_round.render())

        for category_index, category_definition in enumerate(round_definition.Categories):

            for prize in ['100', '200', '300', '400', '500']:

                with open(join(destination_path, f'{category_index}.{prize}.answer.html'), 'w') as f:

                    f.write(template_answer.render())

                with open(join(destination_path, f'{category_index}.{prize}.question.html'), 'w') as f:

                    f.write(template_question.render())


def _parse_arguments():

    parser = ArgumentParser(description='Tool to generate html-based Jeopardy')

    parser.add_argument(KEY_DEFINITION,  type=str, help='The path to the definition file')
    parser.add_argument(KEY_DESTINATION, type=str, help='The path to the destination directory')

    args = vars(parser.parse_args())

    return args


def _copy_style(destination_path):

    with open(join(destination_path, STYLE), 'w') as f:

        f.write(JINJA_ENV.get_template(STYLE).render())


def _read_definition(definition_path):

    with open(definition_path) as f:

        definition = munchify(safe_load(f))

    return definition
