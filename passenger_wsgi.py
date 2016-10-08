import sys, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.join(BASE_DIR))  #You must add your project here or 500

#Switch to new python
#You may try to replace $HOME with your actual path
PYTHON_PATH = os.path.join(BASE_DIR, 'env', 'bin', 'python')
if sys.executable != PYTHON_PATH:
    os.execl(PYTHON_PATH, "python2.7.12", *sys.argv)

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