#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import aiohttp
import asyncio
import argparse
import settings


async def get_task(task_id):
    task_url = settings.informatics_task_base_link.format(task_id)


def main(arguments):
    ids = arguments.ids
    assert ids is not None
    for i in ids:
        get_task(i)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Informatics MCCME to\
            Yandex.Contest')
    parser.add_argument('-i', '--ids', action='store', dest='ids',
                        type=int, nargs='+',
                        help='Ids from informatics.mccme.ru')
    args = parser.parse_args()
    main(args)
