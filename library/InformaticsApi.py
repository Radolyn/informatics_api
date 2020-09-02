import re
from typing import Any

import requests
from bs4 import BeautifulSoup
from requests import Response

from library.DataObject import DataObject
from library.Models import RunsList, SourceRun, TestsList
from library.Problem import Problem
from library.Result import Result
from library.UnauthorizedException import UnauthorizedException
from library.User import User


def str_cleaner(string: str) -> str:
    """
    Заменяет все двойные переходы и пробелы на одинарные
    :param string: Строка
    :return: Чистая строка
    """
    return re.sub(r'([\r\t])|(\s){2,}?|(\n){2,}?', '', string)[:-1]


class InformaticsApi(object):
    """Предоставляет методы для работы с костыльным back-end'ом информатикса

    Args:
        url (str): ссылка на сайт
        backend (str): путь относительно сайта до back-end'а
        session (Session): сессия
        routes (dict): пути до front-end'овских страниц
        backend_routes (dict): пути до back-end'овских страниц
        user (User): текущий пользователь
    """

    def __init__(self) -> None:
        """Инициализирует класс
        """
        self.url = 'https://informatics.msk.ru/'
        self.backend = 'py/'
        self.session = requests.Session()
        self.routes = {
            'login': 'login/index.php',
            'problem': 'mod/statements/view.php?chapterid=%i',
        }
        self.backend_routes = {
            'submit': 'problem/%i/submit',
            'run': 'problem/run/%i/source',
            'filter':
                'problem/%i/filter-runs?user_id=%i&from_timestamp=%i&to_timestamp=%i&group_id=%i&lang_id=%i&status_id=%i&statement_id=%i&count=%i&with_comment=%s&page=%i',
            'source': 'problem/run/%i/source',
            'protocol': 'protocol/get/%i'
        }
        self.user: User = None

    def get_route(self, route: str, backend: bool = True) -> str:
        """Получение полного пути до страницы

        Args:
            route (str): название
            backend (bool, optional): Back-end или front-end. По умолчанию True.

        Returns:
            str: Путь до страницы
        """
        if backend:
            return self.url + self.backend + self.backend_routes[route]

        return self.url + self.routes[route]

    def send_request(self,
                     route: str,
                     route_data: Any,
                     method: str = 'get',
                     data: dict = None,
                     files: dict = None) -> Response:
        """Отправляет запрос на back-end

        Args:
            route (str): имя пути
            route_data (Any): данные для форматирования пути
            method (str, optional): Метод. По умолчанию 'get'.
            data (dict, optional): Данные для запроса. По умолчанию None.
            files (dict, optional): Файлы для запроса. По умолчанию None.

        Raises:
            UnauthorizedException: Если пользователь не авторизован

        Returns:
            Response: Ответ
        """
        if not self.user:
            raise UnauthorizedException()
        res = self.session.request(method,
                                   self.get_route(route) % route_data,
                                   data=data,
                                   files=files,
                                   timeout=5,
                                   json=True)
        return res

    def authorize(self, username: str, password: str) -> bool:
        """Авторизовывает пользователя

        Args:
            username (str): Логин
            password (str): Пароль

        Returns:
            bool: Успешная ли авторизация
        """
        # спасибо информатиксу за доп. костыли
        form = self.session.get(self.get_route('login', False))
        login_token = BeautifulSoup(form.text, 'html.parser').select(
            '#login > input[type=hidden]:nth-child(3)')[0].attrs['value']

        res = self.session.post(self.get_route('login', False),
                                data={
                                    'anchor': '',
                                    'logintoken': login_token,
                                    'username': username,
                                    'password': password,
                                    'rememberusername': 1
                                })

        if 'Вы зашли под именем' not in res.text:
            return False

        self.user = User(
            int(
                BeautifulSoup(res.text, 'html.parser').select(
                    '#page-footer > div > div.logininfo > a:nth-child(1)')
                [0].attrs['href'].replace(self.url + 'user/profile.php?id=',
                                          '')))

        return True

    def get_user(self) -> User:
        # todo;
        return None

    # --  --

    def get_problem(self, id: int) -> Problem:
        """Парсит всю информацию о задании

        Args:
            id (int): ID задачи

        Returns:
            Problem: Задача
        """
        data = self.session.get(self.get_route('problem', False) % id)

        if data.status_code != 200:
            return Problem(-1)

        problem = Problem(id)

        # todo: проверка на пустоту

        tree = BeautifulSoup(data.text, 'html.parser')

        # -- имя --
        problem.title = tree.title.text

        # -- описание --
        desc = tree.find('div', {'class': 'legend'})

        if desc:
            problem.description = str_cleaner(desc.text.strip())

        # -- входные данные --
        input_data = tree.find('div', {'class': 'input-specification'})

        if input_data:
            problem.output_data = str_cleaner(input_data.text.strip().replace(
                'Входные данные', ''))

        # -- выходные данные --
        output_data = tree.find('div', {'class': 'output-specification'})

        if output_data:
            problem.output_data = str_cleaner(output_data.text.strip().replace(
                'Выходные данные', ''))

        # todo: парсить пример(ы)

        return problem

    # -- / --

    # --  --

    def submit_problem(self, id: int, file: str, lang_id: int) -> Result:
        """Отправляет заадчу на тестирование

        Args:
            id (int): ID
            file (str): Файл
            lang_id (int): ID языка

        Returns:
            Result: Результат операции (DataObject)
        """
        f = open(file, 'rb')

        req = self.send_request('submit', id, 'post', {'lang_id': lang_id},
                                {'file': f})

        f.close()

        return Result(req, DataObject())

    def get_self_runs(self,
                      id: int,
                      from_timestamp: Any = -1,
                      to_timestamp: Any = -1,
                      group_id: int = 0,
                      lang_id: int = -1,
                      status_id: int = -1,
                      statement_id: int = 0,
                      count: int = 20,
                      with_comment: str = '',
                      page: int = 1) -> Result:
        """Получает посылки текущего пользователя

        Args:
            id (int): ID задачи
            from_timestamp (Any, optional): С какого времени. Defaults to -1.
            to_timestamp (Any, optional): По какое время. Defaults to -1.
            group_id (int, optional): ID группы. Defaults to 0.
            lang_id (int, optional): ID языка. Defaults to -1.
            status_id (int, optional): ID статуса. Defaults to -1.
            statement_id (int, optional): ID ???. Defaults to 0.
            count (int, optional): Количество. Defaults to 20.
            with_comment (str, optional): С комментарием. Defaults to ''.
            page (int, optional): Страница. Defaults to 1.

        Returns:
            Result: Результат операции (RunsList)
        """
        return self.get_runs(id, self.user.id, from_timestamp, to_timestamp,
                             group_id, lang_id, status_id, statement_id, count,
                             with_comment, page)

    def get_runs(self,
                 id: int,
                 user_id: int,
                 from_timestamp: int = -1,
                 to_timestamp: int = -1,
                 group_id: int = 0,
                 lang_id: int = -1,
                 status_id: int = -1,
                 statement_id: int = 0,
                 count: int = 20,
                 with_comment: str = '',
                 page: int = 1) -> Result:
        """Получает посылки пользователя по ID

        Args:
            id (int): ID задачи
            user_id (int): ID пользователя
            from_timestamp (Any, optional): С какого времени. Defaults to -1.
            to_timestamp (Any, optional): По какое время. Defaults to -1.
            group_id (int, optional): ID группы. Defaults to 0.
            lang_id (int, optional): ID языка. Defaults to -1.
            status_id (int, optional): ID статуса. Defaults to -1.
            statement_id (int, optional): ID ???. Defaults to 0.
            count (int, optional): Количество. Defaults to 20.
            with_comment (str, optional): С комментарием. Defaults to ''.
            page (int, optional): Страница. Defaults to 1.

        Returns:
            Result: Результат операции (RunsList)
        """
        req = self.send_request(
            'filter',
            (id, user_id, from_timestamp, to_timestamp, group_id, lang_id,
             status_id, statement_id, count, with_comment, page))
        return Result(req, RunsList())

    def get_run(self, id: int) -> Result:
        """Получает исходный код посылки

        Args:
            id (int): ID посылки

        Returns:
            Result: Результат операции (SourceRun)
        """
        req = self.send_request('source', id)
        return Result(req, SourceRun())

    def get_protocol(self, id: int) -> Result:
        """Получает протоколы проверки посылки

        Args:
            id (int): ID посылки

        Returns:
            Result: Результат операции (TestsList)
        """
        req = self.send_request('protocol', id)
        return Result(req, TestsList())

    # -- / --
