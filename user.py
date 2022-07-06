import requests


class User:
    token = None

    def update(self, data):
        for el in zip(data.keys(), data.values()):
            self.__dict__[el[0]] = el[1]

    def get_token(self, path, email, password):
        self.token = requests.post(path, data={'email': email, 'password': password}).json().get('auth_token')

    def del_token(self, path, token):
        requests.post(path, headers={'Authorization': f'Token {token}'})
        self.token = None

    def data_user(self, path, token):
        data_user = requests.get(path, headers={'Authorization': f'Token {token}'})
        return data_user.json()



