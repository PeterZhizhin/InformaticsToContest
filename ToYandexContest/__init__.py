from shutil import make_archive
import json
from pathlib import Path

from ToYandexContest.YandexContest_json import contest_json
from ToYandexContest.language_transitions import language_transition


class YandexContestProblem:
    def __init__(self, problem):
        self.problem = problem

    def save_tests(self, task_dir: Path):
        problem = self.problem

        tests_dir = task_dir / 'tests'
        tests_dir.mkdir(parents=True)
        tests_files = []
        for num, test in enumerate(problem['tests'], start=1):
            test_name = '{0:0>2}'.format(num)
            corr_name = '{0:0>2}.a'.format(num)

            test_path = tests_dir / test_name
            corr_path = tests_dir / corr_name
            with test_path.open('wb') as test_file:
                test_file.write(test[0])
            with corr_path.open('wb') as corr_file:
                corr_file.write(test[1])
            tests_files.append(('tests/{}'.format(test_name),
                                'tests/{}'.format(corr_name)))
        problem.pop('tests')

        return tests_files

    def save_solutions(self, task_dir: Path):
        problem = self.problem
        solution_string = ''
        solutions = []
        for num, solution in enumerate(problem['solutions'], start=1):
            extension = ''
            solution_language = solution['language']
            if solution_language in language_transition:
                extension = language_transition[solution_language][1]
            solution_name = 'solution{0:0>2}'.format(num) + extension
            if solution['language'] in language_transition:
                solutions.append((solution_name, language_transition[solution_language][0]))
            else:
                solutions.append((solution_name, None))

            solution_path = task_dir / solution_name
            with solution_path.open('w') as solution_file:
                print(solution['source'], file=solution_file)
                solution.pop('source')
                solution_string += solution_name + ': {0:0>2} {1}'.format(num, solution['language'])

        return solutions, solution_string

    @staticmethod
    def get_json_for_contest(problem, solutions):
        yandex_contest_json = dict(contest_json)

        name = problem['name']
        description = problem['description']
        input_desr = problem['input_description']
        output_descr = problem['output_description']

        note = ''
        if problem['note'] is not None:
            note += '\n\n' + problem['note'] + '\n\n'
        if problem['additional_info'] is not None:
            note += '\n\n' + problem['additional_info'] + '\n\n'
        note = note.strip()

        yandex_contest_json['names']['ru'] = name
        yandex_contest_json['statements'][0]['texStatement']['legend'] = description
        yandex_contest_json['statements'][0]['texStatement']['inputFormat'] = input_desr
        yandex_contest_json['statements'][0]['texStatement']['outputFormat'] = output_descr
        yandex_contest_json['statements'][0]['texStatement']['notes'] = note

        task_solutions = []
        for solution in solutions:
            task_solutions.append({
                'compilerId': 'gcc0x' if solution[1] is None else solution[1],
                'sourcePath': solution[0],
                'verdict': 'ok',
            })
        yandex_contest_json['solutions'] = task_solutions

        return yandex_contest_json

    def save_task(self, task_dir: Path):
        print('Saving task {}'.format(task_dir.name))

        task_dir.mkdir(parents=True)
        if 'tests' in self.problem:
            tests_files = self.save_tests(task_dir)
        solutions, solution_string = self.save_solutions(task_dir)

        problem = self.problem
        with (task_dir / 'info.json').open('w') as info_file:
            json.dump(problem, info_file, sort_keys=True, indent=4, ensure_ascii=False)
        with (task_dir / 'description.txt').open('w') as info_file:
            separator = '\n------------------------------\n'
            print(problem['name'], problem['description'],
                  problem['input_description'], problem['output_description'],
                  problem['note'], problem['additional_info'],
                  solution_string,
                  file=info_file, sep=separator)

        good_json = YandexContestProblem.get_json_for_contest(problem, solutions)
        with (task_dir / 'problem.json').open('w') as problem_file:
            json.dump(good_json, problem_file, sort_keys=True, indent=4, ensure_ascii=False)

