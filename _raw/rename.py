# -*- coding: utf-8 -*-
# encoding=utf8
import os
import hashlib
kw = '에서'
filename = hashlib.md5(kw.encode('utf-8')).hexdigest()
print filename
'''[os.rename(
    f, f.replace('result-에서-W', 'result-{0}-W'.format(filename))
 ) for f in os.listdir('.') if not f.startswith('.')]'''