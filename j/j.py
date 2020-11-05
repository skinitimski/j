from argparse import ArgumentParser

from jinja2 import Environment, PackageLoader

from munch import DefaultMunch

from os import makedirs

from os.path import isdir
from os.path import join

from shutil import rmtree

from yaml import safe_load


KEY_DEFINITION  = 'definition'
KEY_DESTINATION = 'destination'
KEY_FORCE       = 'force'

STYLE          = 'style.css'
FINAL          = 'final.html'
FINAL_CATEGORY = 'final.category.html'
FINAL_ANSWER   = 'final.answer.html'
FINAL_QUESTION = 'final.question.html'
END            = 'end.html'

JINJA_ENV = Environment(loader=PackageLoader('j'))


def main():

    args = _parse_arguments()

    j(args[KEY_DEFINITION], args[KEY_DESTINATION], args[KEY_FORCE])


def j(definition_path, destination_path, force):

    if isdir(destination_path) and force:

        rmtree(destination_path)

    makedirs(destination_path)

    _render_template(
        join(destination_path, STYLE),
        JINJA_ENV.get_template(STYLE)
    )

    definition = _read_definition(definition_path)

    template_round       = JINJA_ENV.get_template('round.html')
    template_dailydouble = JINJA_ENV.get_template('dailydouble.html')
    template_answer      = JINJA_ENV.get_template('answer.html')
    template_question    = JINJA_ENV.get_template('question.html')
    template_description = JINJA_ENV.get_template('description.html')

    rounds = definition.Rounds

    round_count = len(rounds)

    for round_index0, round_definition in enumerate(rounds):

        round_index = round_index0 + 1

        categories = round_definition.Categories

        prizes = [(p + 1) * round_index * 100 for p in range(5)]

        _render_template(
            join(destination_path, f'round{round_index}.html'),
            template_round,
            categories=categories,
            round_count=round_count,
            round_index=round_index,
            prizes=prizes
        )

        for category_index0, category_definition in enumerate(categories):

            category_index = category_index0 + 1

            if category_definition.Example:

                question_path = f'example.question.round{round_index}.category{category_index}.html'

                _render_template(
                    join(destination_path, f'example.answer.round{round_index}.category{category_index}.html'),
                    template_answer,
                    answer=category_definition.Example.Answer,
                    question_path=question_path
                )

                _render_template(
                    join(destination_path, question_path),
                    template_question,
                    round_index=round_index,
                    trivia=category_definition.Example
                )

            elif category_definition.Description:

                _render_template(
                    join(destination_path, f'description.round{round_index}.category{category_index}.html'),
                    template_description,
                    description=category_definition.Description,
                    round_index=round_index,
                    title=category_definition.Name
                )

            for prize_index, prize in enumerate(prizes):

                trivia = category_definition.Trivia[prize_index]

                if trivia.DailyDouble:

                    _render_template(
                        join(destination_path, f'dailydouble.round{round_index}.category{category_index}.prize{prize}.html'),
                        template_dailydouble,
                        category_index=category_index,
                        prize=prize,
                        round_index=round_index
                    )

                question_path = f'question.round{round_index}.category{category_index}.prize{prize}.html'

                _render_template(
                    join(destination_path, f'answer.round{round_index}.category{category_index}.prize{prize}.html'),
                    template_answer,
                    answer=trivia.Answer,
                    question_path=question_path,
                    prize=prize
                )

                _render_template(
                    join(destination_path, question_path),
                    template_question,
                    prize=prize,
                    round_index=round_index,
                    trivia=trivia
                )

    _render_template(
        join(destination_path, FINAL),
        JINJA_ENV.get_template(FINAL),
        round_count=round_count
    )

    _render_template(
        join(destination_path, FINAL_CATEGORY),
        JINJA_ENV.get_template(FINAL_CATEGORY),
        category=definition.Final.Category,
        round_count=round_count
    )

    _render_template(
        join(destination_path, FINAL_ANSWER),
        JINJA_ENV.get_template(FINAL_ANSWER),
        answer=definition.Final.Answer
    )

    _render_template(
        join(destination_path, FINAL_QUESTION),
        JINJA_ENV.get_template(FINAL_QUESTION),
        question=definition.Final.Question
    )

    _render_template(
        join(destination_path, END),
        JINJA_ENV.get_template(END)
    )


def _parse_arguments():

    parser = ArgumentParser(description='Tool to generate html-based Jeoparty')

    parser.add_argument(KEY_DEFINITION,  type=str, help='The path to the definition file')
    parser.add_argument(KEY_DESTINATION, type=str, help='The path to the destination directory')

    parser.add_argument(f'--{KEY_FORCE}', action='store_true', help='Optional flag to delete destination directory when it exists')

    args = vars(parser.parse_args())

    return args


def _read_definition(definition_path):

    with open(definition_path) as f:

        definition = DefaultMunch.fromDict(safe_load(f), None)

    return definition


def _render_template(path, template, **data):

    page = template.render(**data)

    with open(path, 'w') as f:

        f.write(page)
