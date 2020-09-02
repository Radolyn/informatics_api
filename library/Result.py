from requests import Response

from library.DataObject import DataObject


class Result(object):
    success: bool
    reason: str
    data: DataObject
    response: Response

    def __init__(self, res: Response, data: DataObject):
        json: dict

        try:
            json = res.json()
        except:
            self.success = False
            json = {'error': 'Failed to parse', 'status': 'error'}

        # -- спасибо информатиксу --
        if 'result' in json.keys():
            json['status'] = json['result']
            del json['result']

        if 'status' not in json.keys():
            if res.status_code == 200:
                json['status'] = 'success'
            else:
                json['status'] = 'error'
        # -- /спасибо информатиксу --

        self.success = json['status'] == 'success'

        self.reason = json['error'] if not self.success else 'Success'

        if data.route in json.keys():
            self.data = data
            data.data = json[data.route]
            data.parse()

        self.response = res
