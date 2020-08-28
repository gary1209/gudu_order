from flask_sqlalchemy import SQLAlchemy
import yaml

class Config():
    _host = '0.0.0.0'
    _port = 1234
    _debug = True
    _db = None
    _app = None
    _order_pos_working = False
    _checkout_pos_working = False

    @property
    def db(self):
        '''
        :return: The pony orm db instance without db provider binding
        '''
        if self._db:
            return self._db

        self._db = SQLAlchemy()
        return self._db

    @property
    def app(self):
        '''
        The Flask app instance
        '''
        return self._app

    @app.setter
    def app(self, val):
        '''
        Init the database for the app while setting
        '''
        self._app = val
        self.db.init_app(self.app)

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def debug(self):
        return self._debug


    def read_config(self):
        with open('status.yaml') as f:
            for x in yaml.load(f):
                if 'order_pos_working' in x:
                    self._order_pos_working = x['order_pos_working']

    @property
    def order_pos_working(self):
        return self._order_pos_working

    @order_pos_working.setter
    def order_pos_working(self, val):
        self._order_pos_working = val

    @property
    def checkout_pos_working(self):
        return self._checkout_pos_working

    @checkout_pos_working.setter
    def checkout_pos_working(self, val):
        self._checkout_pos_working = val

config = Config()
config.read_config()
