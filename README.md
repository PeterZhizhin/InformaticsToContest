# InformaticsToContest

Утилита для загрузки задач с сайта [informatics.mccme.ru](informatics.mccme.ru) и экспорт их в формате Yandex.Contest.

## Требования

* Python 3.5 или выше.
* Библиотеки aiohttp, aiofiles.
* Права администратора на [informatics.mccme.ru](informatics.mccme.ru).
* Доступ на SSH сайта informatics.

## Настройка

1. Для запуска утилиты необходим доступ к тестам и корректным решениям на сайте. Для этого пользователь должен иметь
права администратора на сайте.

2. Перед запуском утилиты скопируйте файл `auth_info.py.example` в файл `auth_info.py`:
```bash
$ cp auth_info.py.example auth_info.py
```

3. В файле `auth_info.py` укажите свои логин и пароль.

4. Примонтируйте при помощи sshfs папку /home/judges куда-либо внутри файловой системы локального компьютера:
```bash
sshfs ejudge@informatics.mccme.ru:/home/judges /home/<USERNAME>/<FOLDERNAME>/
```

## Параметры запуска

```
-d --directory Название директории для сохранения файлов.
               Должна отсутствовать в папке со скриптом чтобы избежать перезаписи.
-j --judges Путь до папки примонтированной при помощи sshfs /home/judges
            сайта informatics.mccme.ru
-i --ids Список номеров задач с сайта (указанных через пробел)

Пример:
./main.py -d tasks -j /home/user/informatics/home/judges/ -i 501 520 3521
```
