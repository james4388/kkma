import requests
from pyquery import PyQuery as pq

from django.utils.html import strip_tags


def translate(sentence):
    ''' Using naver.com to tranlate word by word '''
    sentence = strip_tags(sentence).strip()
    words = sentence.split()
    trans = {}
    
    
    for word in words:
        r = requests.get('http://m.vndic.naver.com/search?query=%s&lh=true' % word)
        q = pq(r.text)
        tran = []
        sections = q('.section_area')
        if sections.length > 0:
            for section in sections.children('.section_h, .section_dsc').items():
                if section.hasClass('section_h'):
                    tran.append('<h4>%s</h4>' % section.text())
                elif section.hasClass('section_dsc'):
                    for sub in section.children('.section_sub').items():
                        sub.find('script, .play, .btn_play').remove()
                        sub.find('a').removeAttr('onclick')
                        tran.append('<div>%s</div>' % sub.html())
        trans[word] = tran
    return trans