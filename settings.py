from frozendict import frozendict

informatics = 'http://informatics.mccme.ru/'
informatics_base = 'http://informatics.mccme.ru/login/index.php'
informatics_task_base_link = "http://informatics.mccme.ru/mod/statements/view3.php?chapterid={}"
informatics_auth_link = 'http://informatics.mccme.ru/login/index.php'

informatics_ajax = 'http://informatics.mccme.ru/moodle/ajax/ajax.php'
informatics_ajax_count_correct_solutions = frozendict(
    dict(
        objectName='submits',
        group_id=0,
        user_id=0,
        status_id=0,
        lang_id=-1,
        count=1,
        statement_id=0,
        action='getPageCount',
    )
)
informatics_ajax_get_correct_solutions = frozendict(
    dict(
        group_id=0,
        user_id=0,
        lang_id=-1,
        status_id=0,
        statement_id=0,
        objectName='submits',
        count=100,
        page=1,
        action='getHTMLTable',
    ))

max_needed_correct_solutions = 5