from flask_sqlalchemy import SQLAlchemy

class Config():
    _host = '0.0.0.0'
    _port = 1234
    _debug = True
    _db = None
    _app = None


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


config = Config()
