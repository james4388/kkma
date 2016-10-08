import sys, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _get_log():
    return file(os.path.join(BASE_DIR, 'tmp', 'log.txt'), 'a')
log = _get_log()
print >>log, "Running %s" % (sys.executable)

sys.path.append(os.path.join(BASE_DIR, 'kkmadb'))  #You must add your project here or 500

#Switch to new python
#You may try to replace $HOME with your actual path
PYTHON_PATH = os.path.join(BASE_DIR, 'env', 'bin', 'python')
if sys.executable != PYTHON_PATH:
    print >>log, "Detected wrong interpreter location, swapping to %s" % (PYTHON_PATH)
    log.flush()
    log.close()
    os.execl(PYTHON_PATH, "python2.7.12", *sys.argv)
    
log.flush()
log.close()

from paste.deploy import loadapp

sys.path.insert(0, os.path.join(BASE_DIR, 'env', 'bin'))
sys.path.insert(0, os.path.join(
    BASE_DIR, 'env', 'lib', 'python2.7', 'site-packages', 'django'
))
sys.path.insert(0, os.path.join(
    BASE_DIR, 'env', 'lib', 'python2.7', 'site-packages'
))

os.environ['DJANGO_SETTINGS_MODULE'] = "kkmadb.settings"

from django.core.wsgi import get_wsgi_application
# application = get_wsgi_application()

def application(environ, start_response):
    log = _get_log()
    print >>log, "Application called:"
    print >>log, "environ: %s" % str(environ)
    results = []
    try:
        app = get_wsgi_application()
        print >>log, "App loaded, attempting to run"
        log.flush()
        results = app(environ, start_response)
        print >>log, "App executed successfully"
    except Exception, inst:
        print >>log, "Error: %s" % str(type(inst))
        print >>log, inst.args
        log.flush()
    finally:
        log.close()
    return results