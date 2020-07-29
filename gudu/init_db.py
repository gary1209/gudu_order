import os

import yaml

import models
from config import config
from server import setup_db

def main():
    p = os.path.join(os.path.dirname(__file__), '../db', 'default.yaml')
    setup_db()
    db = config.db

    with open(p) as f, config.app.test_request_context():
        for x in yaml.load(f):
            if 'model' in x:
                try:
                    model = getattr(models, x['model'])
                    tuple(map(lambda r: db.session.add(model(**r)), x['records']))
                finally:
                    db.session.commit()

if __name__ == '__main__':
    main()