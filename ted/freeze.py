import os
from common import list_countries, get_output_dir
from web import app

client = app.test_client()

def freeze_request(req_path):
    print "Freezing %s..." % req_path
    path = os.path.join(get_output_dir(), req_path.lstrip('/'))
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    fh = open(path, 'w')
    res = client.get(req_path)
    fh.write(res.data)
    fh.close()


def freeze_all():
    freeze_request('/index.html')
    for country in list_countries():
        freeze_request('/country/%s.html' % country)


if __name__ == '__main__':
    freeze_all()




