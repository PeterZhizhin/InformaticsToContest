#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import argparse
from InformaticsDownloader import InformaticsDownloader
from pathlib import Path
from shutil import make_archive

from ToYandexContest import YandexContestProblem


def check_output_directory(directory):
    if directory is None:
        print("No directory for saving tasks")
    directory = Path.cwd() / directory
    if directory.exists():
        print('Output directory exists: {}'.format(directory))
        sys.exit()
    return directory


def check_judges_directory(directory):
    if directory is None:
        print("No judges directory for tests")
        sys.exit()
    judges_dir = Path(directory)
    if not judges_dir.exists():
        print("Path for judges doesn't exists: {}".format(judges_dir))
        sys.exit()
    return judges_dir


def main(arguments):
    ids = arguments.ids
    if ids is None:
        print('No ids')
        sys.exit()

    directory = check_output_directory(arguments.directory)
    judges_dir = check_judges_directory(arguments.sshfs)
    need_tests = arguments.need_tests
    tasks = InformaticsDownloader.get_tasks(ids, judges_dir, need_tests)
    yandex_tasks = [YandexContestProblem(task) for task in tasks]
    for num, yandex_task in enumerate(yandex_tasks):
        task_dir = directory / chr(num + ord('A'))
        yandex_task.save_task(task_dir)
        make_archive(str(task_dir), 'zip', str(task_dir))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Informatics MCCME to\
            Yandex.Contest')
    parser.add_argument('-d', '--directory', action='store', dest='directory',
                        type=str, help='Directory for saving tasks')
    parser.add_argument('-j', '--judges', action='store', dest='sshfs',
                        type=str, help='Directory of informatics.mccme.ru /home/judges for downloading tests')
    parser.add_argument('-i', '--ids', action='store', dest='ids',
                        type=int, nargs='+',
                        help='Ids from informatics.mccme.ru')
    parser.add_argument('-r', '--remove_tests', help='Do not download tests',
                        dest='need_tests', action='store_const',
                        const=False, default=True)
    args = parser.parse_args()
    main(args)
