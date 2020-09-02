class DataObject(object):
    """Класс, содержащий типизированный ответ

    Args:
        data (dict): исходный ответ
        route (str): путь до ветки с данными
    """
    data: dict
    route: str = 'data'

    def parse(self):
        pass
