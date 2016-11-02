import aiohttp
import asyncio
import auth_info
import settings
import json
import aiofiles
import re
from pathlib import Path

from bs4 import BeautifulSoup


class NoContestException(Exception):
    pass


class TestsNotFound(Exception):
    pass


test_filename_re = re.compile(r'^\d*$')
test_corr_filename_re = re.compile(r'^\d*\.a$')


class InformaticsDownloader:
    semaphore = asyncio.Semaphore(5000)
    opened_files_semaphore = asyncio.Semaphore(200)

    @staticmethod
    async def get_async_unbounded(session, url, raw_bytes=False, **kwargs):
        async with session.get(url, **kwargs) as resp:
            print('Getting {}'.format(url))
            if resp.status != 200:
                await asyncio.sleep(0.5)
                print('Retry {}'.format(url))
                return await InformaticsDownloader.get_async(session, url, **kwargs)
            if raw_bytes:
                return await resp.read()
            else:
                return await resp.text()

    @staticmethod
    async def get_async(session, url, **kwargs):
        async with InformaticsDownloader.semaphore:
            return await InformaticsDownloader.get_async_unbounded(session, url, **kwargs)

    @staticmethod
    def fix_latex(s):
        return s.replace('\(', '$').replace('\)', '$').replace(
            '\left(', '(').replace('\\right', ')').replace(
            '\[', "\n\n$"
        ).replace('\]', '\n\n$').replace('\left[', '[').replace(
            '\\right]', ']'
        ).replace('\left{', '{').replace('\\right}', '}')

    @staticmethod
    def parse_html(html, id):
        print('Parsing HTML for task {}'.format(id))
        soup_html = BeautifulSoup(html, 'lxml')

        statements_soup = soup_html.find('div', attrs={'class': 'problem-statement'})

        task_div = soup_html.find('div', attrs={'class': 'statements_chapter_title'})
        task_name = next(task_div.children).split('.')[1].strip()
        description = statements_soup.find('div', attrs={'class': 'legend'}).text
        description = InformaticsDownloader.fix_latex(description)

        contest_raw = task_div.find('a',
                                    attrs={'href': lambda x: False if x is None else
                                    '/cgi-bin/new-master?contest_id' in x}).text
        contest_info = contest_raw.split()
        contest_info = {
            'number': contest_info[1],
            'problem_id': contest_info[-1]
        }

        input_html = statements_soup.find('div', attrs={'class': 'input-specification'})
        if input_html is not None:
            input = input_html.text
            input = input.replace('Входные данные', '')
            input = InformaticsDownloader.fix_latex(input)
        else:
            input = ''

        output_html = statements_soup.find('div', attrs={'class': 'output-specification'})
        if output_html is not None:
            output = output_html.text
            output = output.replace('Выходные данные', '')
            output = InformaticsDownloader.fix_latex(output)
        else:
            output = ''
        note = statements_soup.find('div', attrs={'class': 'note'})
        if note is not None:
            note = note.text.replace('Примечание', '')
            note = InformaticsDownloader.fix_latex(note)

        additional_info = statements_soup.find('div', attrs={'class': 'info-specification'})
        if additional_info is not None:
            additional_info = additional_info.text
            additional_info = InformaticsDownloader.fix_latex(additional_info)

        return {
            'name': task_name,
            'description': description,
            'input_description': input,
            'output_description': output,
            'additional_info': additional_info,
            'note': note,
            'contest_info': contest_info,
            'contest_raw': contest_raw
        }

    @staticmethod
    def parse_good_solution(html):
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find('table')
        users = table.find_all('tr')[1:]

        solutions = []
        for user in users:
            vals = user.find_all('td')
            language = vals[4].text
            source_html = settings.informatics + vals[-1].find('a')['href']
            solutions.append({
                'language': language,
                'source_html': source_html
            })
        return solutions

    @staticmethod
    def parse_source_code(code_html):
        soup = BeautifulSoup(code_html, 'lxml')
        return soup.find('textarea').text

    @staticmethod
    async def get_source_code(session, code_link):
        source_code_html = await InformaticsDownloader.get_async(session,
                                                                 code_link,
                                                                 raw_bytes=True)
        source_code_html = source_code_html.decode('utf-8', 'ignore')

        code = await asyncio.get_event_loop().run_in_executor(None,
                                                              InformaticsDownloader.parse_source_code,
                                                              source_code_html)
        return code

    @staticmethod
    async def find_good_solutions(session, task_id):
        print('Finding OK solutions for {}'.format(task_id))
        params = dict(settings.informatics_ajax_count_correct_solutions)
        params['problem_id'] = task_id
        solutions_count = json.loads(await InformaticsDownloader.get_async(session,
                                                                           settings.informatics_ajax,
                                                                           params=params))
        solutions_count = min(solutions_count['result']['page_count'], settings.max_needed_correct_solutions)

        params = dict(settings.informatics_ajax_get_correct_solutions)
        params['problem_id'] = task_id
        params['count'] = solutions_count
        solutions_table = await InformaticsDownloader.get_async(session, settings.informatics_ajax,
                                                                params=params)
        solutions_table = json.loads(solutions_table)['result']['text']
        solutions = await asyncio.get_event_loop().run_in_executor(None,
                                                                   InformaticsDownloader.parse_good_solution,
                                                                   solutions_table)
        sources = [InformaticsDownloader.get_source_code(session, i['source_html']) for i in solutions]
        print('Gathering {} OK solutions for {}'.format(solutions_count, task_id))
        sources = list(await asyncio.gather(*sources))
        for i in range(len(solutions)):
            solutions[i]['source'] = sources[i]
        return solutions

    @staticmethod
    async def download_file(file_name: Path):
        try:
            async with InformaticsDownloader.opened_files_semaphore:
                print('Loading file {}'.format(file_name))
                async with aiofiles.open(str(file_name), mode='rb') as file:
                    return await file.read()
        except PermissionError as e:
            await asyncio.sleep(2)
            print('Retrying download')
            return InformaticsDownloader.download_file(file_name)

    @staticmethod
    async def get_tests(task_id, contest_info, judges_dir: Path):
        print('Loading tests for {}'.format(task_id))
        contest_dir = judges_dir / contest_info['number']
        if not contest_dir.exists():
            msg = "Couldn't find contest directory for {} {} {}. Remove the task.".format(task_id,
                                                                                          contest_info['number'],
                                                                                          contest_info['problem_id'])
            raise NoContestException(msg)
        # Check <contest>/tests/<problem>
        tests_problem = contest_dir / 'tests' / contest_info['problem_id']
        # And <contest>/problems/<problem>/tests
        problems_problem_tests = contest_dir / 'problems' / contest_info['problem_id'] / 'tests'
        if not tests_problem.exists() and not problems_problem_tests.exists():
            msg = "Couldn't find tests folder for {} {} {}. Remove the task.".format(task_id,
                                                                                     contest_info['number'],
                                                                                     contest_info['problem_id'])
            raise TestsNotFound(msg)
        if tests_problem.exists():
            result_tests = tests_problem
        else:
            result_tests = problems_problem_tests
        print('Downloading tests from {}'.format(result_tests))
        tests_files = []
        corr_files = []
        for file_test in result_tests.iterdir():
            if test_filename_re.match(file_test.name):
                tests_files.append(file_test)
            elif test_corr_filename_re.match(file_test.name):
                corr_files.append(file_test)
        tests_files.sort(key=lambda x: x.name)
        corr_files.sort(key=lambda x: x.name)
        assert len(tests_files) == len(corr_files)
        tests_files = asyncio.gather(*[InformaticsDownloader.download_file(file) for file in tests_files])
        corr_files = asyncio.gather(*[InformaticsDownloader.download_file(file) for file in corr_files])
        tests_files, corr_files = await asyncio.gather(tests_files, corr_files)
        return list(zip(tests_files, corr_files))

    @staticmethod
    async def parse_task(session, task_id, judges_dir: Path, need_tests):
        html = await InformaticsDownloader.get_async(session,
                                                     settings.informatics_task_base_link.format(task_id))
        parsed_task = await asyncio.get_event_loop().run_in_executor(None,
                                                                     InformaticsDownloader.parse_html,
                                                                     html, task_id)
        parsed_task['id'] = task_id

        if need_tests:
            parsed_tests = await InformaticsDownloader.get_tests(task_id, parsed_task['contest_info'], judges_dir)
            parsed_task['tests'] = parsed_tests

        parsed_task['solutions'] = await InformaticsDownloader.find_good_solutions(session, task_id)
        return parsed_task

    @staticmethod
    async def authorize(session):
        async with session.get(settings.informatics_base) as res:
            async with session.post(settings.informatics_auth_link, data={
                'username': auth_info.username,
                'password': auth_info.password,
                'testcookies': 1
            }) as resp:
                text = await resp.text()
                return text

    @staticmethod
    async def get_tasks_async(task_ids, judges_dir: Path, need_tests: bool):
        with aiohttp.ClientSession() as session:
            await InformaticsDownloader.authorize(session)
            futures = []
            for task_id in task_ids:
                futures.append(InformaticsDownloader.parse_task(session, task_id, judges_dir, need_tests))
            return await asyncio.gather(*futures)

    @staticmethod
    def get_tasks(task_ids, judges_dir: Path, need_tests: bool):
        res = asyncio.get_event_loop().run_until_complete(
            InformaticsDownloader.get_tasks_async(task_ids, judges_dir, need_tests))
        return res
