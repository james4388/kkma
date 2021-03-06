import sys, os

VIRTUAL_ENV_PYTHON = 'venv-python'  # Python > 2.7.6 dreamhost not return sys.executable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def is_venv_python():
    if len(sys.argv) > 0:
        last_item = sys.argv[len(sys.argv)-1]
        if last_item == VIRTUAL_ENV_PYTHON:
            return True
    return False

sys.path.append(os.path.join(BASE_DIR, 'kkmadb'))  #You must add your project here or 500

#Switch to new python
#You may try to replace $HOME with your actual path
PYTHON_PATH = os.path.join(BASE_DIR, 'env', 'bin', 'python')
if not is_venv_python():
    os.execl(PYTHON_PATH, "python2.7.12", *sys.argv + [VIRTUAL_ENV_PYTHON])

sys.path.insert(0, os.path.join(BASE_DIR, 'env', 'bin'))
sys.path.insert(0, os.path.join(
    BASE_DIR, 'env', 'lib', 'python2.7', 'site-packages', 'django'
))
sys.path.insert(0, os.path.join(
    BASE_DIR, 'env', 'lib', 'python2.7', 'site-packages'
))

os.environ['DJANGO_SETTINGS_MODULE'] = "kkmadb.settings"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()