from argparse import ArgumentParser

from jinja2 import Environment, PackageLoader

from munch import DefaultMunch

from os import mkdir

from os.path import join

from yaml import safe_load


KEY_DEFINITION  = 'definition'
KEY_DESTINATION = 'destination'

STYLE          = 'style.css'
FINAL          = 'final.html'
FINAL_CATEGORY = 'final.category.html'
FINAL_ANSWER   = 'final.answer.html'
FINAL_QUESTION = 'final.question.html'
END            = 'end.html'

JINJA_ENV = Environment(loader=PackageLoader('j'))


def main():

    args = _parse_arguments()

    j(args[KEY_DEFINITION], args[KEY_DESTINATION])


def j(definition_path, destination_path):

    # this will fail if the directory already exists
    # TODO: maybe honor a --force flag?
    mkdir(destination_path)

    _render_template(
        join(destination_path, STYLE),
        JINJA_ENV.get_template(STYLE)
    )

    definition = _read_definition(definition_path)

    template_round       = JINJA_ENV.get_template('round.html')
    template_dailydouble = JINJA_ENV.get_template('dailydouble.html')
    template_answer      = JINJA_ENV.get_template('answer.html')
    template_question    = JINJA_ENV.get_template('question.html')

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

                _render_template(
                    join(destination_path, f'answer.round{round_index}.category{category_index}.prize{prize}.html'),
                    template_answer,
                    answer=trivia.Answer,
                    category_index=category_index,
                    prize=prize,
                    round_index=round_index
                )

                _render_template(
                    join(destination_path, f'question.round{round_index}.category{category_index}.prize{prize}.html'),
                    template_question,
                    question=trivia.Question,
                    round_index=round_index
                )

    _render_template(
        join(destination_path, FINAL),
        JINJA_ENV.get_template(FINAL),
        round_count=round_count
    )

    _render_template(
        join(destination_path, FINAL_CATEGORY),
        JINJA_ENV.get_template(FINAL_CATEGORY),
        category=definition.Final.Category
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

    parser = ArgumentParser(description='Tool to generate html-based Jeopardy')

    parser.add_argument(KEY_DEFINITION,  type=str, help='The path to the definition file')
    parser.add_argument(KEY_DESTINATION, type=str, help='The path to the destination directory')

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
