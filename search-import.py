# -*- coding: utf-8 -*-
# encoding=utf8

import os
import requests
import json
import codecs
from pyquery import PyQuery as pq
import hashlib
import requests.utils, pickle

FILE_DETAIL = 'http://kkma.snu.ac.kr/statistic?submenu=filedetail&fileId={0}'
VIEW_CONTEXT = 'http://kkma.snu.ac.kr/search?submenu=VIEW_CONTEXT&fileId={0}&partId={1}&sentId={2}'
IMPORT_URL = 'http://localhost:8000/add-example/'
IMPORT_BATCH_URL = 'http://localhost:8000/add-batch-example/'

BATCH_LIMIT = 500

BASE = os.path.dirname(os.path.abspath(__file__))

record_count = 0
post_queue = []



def encode_filename(name):
    return hashlib.md5(name.encode('utf-8')).hexdigest()


def process_detail(table):
  trs = table.children('tr')
  content = ''
  if trs.length > 0:
    for tr in trs.items():
      child = tr.children()
      if child.length > 1:
        col1 = child.eq(0).html()
        col2 = child.eq(1).html()
        content += u'<p><b>{0}</b><span class="data">{1}</span></p>'.format(col1, col2)
  return content


def has_next_page(currentPage, j):
  pagings = j('div.paging')
  if pagings.length > 1:
    bottom_pg = pagings.eq(pagings.length - 1)
    page_links = bottom_pg.children('a')
    if page_links.length > 0:
      last = page_links.eq(page_links.length - 1)
      if last.text() == u'\u25b6':
        return True
      try:
        if int(last.text()) > currentPage:
          return True  
      except:
        pass
  return False


def process_links(href):
  idstr = href.replace("javascript:viewSentDetail('", '').replace("')", '')
  ids = idstr.split(':')
  file_detail = FILE_DETAIL.format(ids[0])
  view_context = VIEW_CONTEXT.format(*ids)
  return u'<a target="_blank" href="{0}"><출처: 포구, 형태 의미 분석 전자파일></a> <a target="_blank" href="{1}">[주변 문장 보기]</a>'.format(file_detail, view_context)


def extract_id(href):
  idstr = href.replace("javascript:viewSentDetail('", '').replace("')", '')
  ids = idstr.split(':')
  if len(ids) < 3:
    ids.append(0)
    ids.append(0)
    ids.append(0)
  return ids


def init_session(keyword, wsType='W'):
  print 'Initialize Session'
  s = requests.Session()
  
  if os.path.isfile('session.pickle'):
    print 'Found previous session. Restoring'
    with open('session.pickle') as f:
        cookies = requests.utils.cookiejar_from_dict(pickle.load(f))
        s.cookies = cookies

  s.get('http://kkma.snu.ac.kr/search')

  r = s.post('http://kkma.snu.ac.kr/search', data={"submenu":"MORP",
    "page":"1",
    "viewPage":"1",
    "viewMorp":None,
    "viewMorps":None,
    "viewPos":None,
    "viewSem":None,
    "tabMenu":"SENT",
    "pageSize":"500",
    "morp": keyword,
    "match":"EXACT",
    "pos":None,
    "wsType": wsType,
    "textClassLv2":None,
    "textClassLv3":None,
    "textClassLv4":None,
    "viewPageSize":"20"
  })
  
  return s


def search(session, keyword, viewPos='JKB', wsType='W', page=1):
  global record_count
  global post_queue
  
  cache_file = os.path.join(BASE, '_raw', "result-{0}-{1}-{2}.html".format(
    encode_filename(keyword), wsType, page
  ))
  
  print 'Seaching from page %d' % page
  
  if not os.path.isfile(cache_file):
    try:
        r = s.post('http://kkma.snu.ac.kr/search', data={
          "submenu":"MORP",
          "page":"1",
          "viewPage": page,
          "viewMorp": keyword,
          "viewMorps":None,
          "viewPos":"JKB",
          "viewSem":None,
          "tabMenu":"SENT",
          "pageSize":"500",
          "morp": keyword,
          "match":"EXACT",
          "pos":None,
          "wsType":wsType,
          "textClassLv2":None,
          "textClassLv3":None,
          "textClassLv4":None,
          "viewPageSize":"500"
        })
    except Exception as ex:
        print ex
        print "Retry"
        try:
            r = s.post('http://kkma.snu.ac.kr/search', data={
              "submenu":"MORP",
              "page":"1",
              "viewPage": page,
              "viewMorp": keyword,
              "viewMorps":None,
              "viewPos":"JKB",
              "viewSem":None,
              "tabMenu":"SENT",
              "pageSize":"500",
              "morp": keyword,
              "match":"EXACT",
              "pos":None,
              "wsType":wsType,
              "textClassLv2":None,
              "textClassLv3":None,
              "textClassLv4":None,
              "viewPageSize":"500"
            })
        except:
            print "Still fail, dump session to file to retry later"
            with open('session.pickle', 'w') as f:
                pickle.dump(requests.utils.dict_from_cookiejar(session.cookies), f)

    with codecs.open(cache_file, "w+", "utf-8-sig") as rout:
      rout.write(r.text)
      
    j = pq(r.text)
  
  else: # Read from cache
    print 'Use cache'
    cache_data = None
    with codecs.open(cache_file, "r", "utf-8-sig") as rin:
      cache_data = rin.read()
      
    j = pq(cache_data)

  containers = j('div[style="padding:0px; border:1px dashed #888888;margin-top:10px;width:100%;"]')

  if containers.length > 0:
    for container in containers.items():
      record_count += 1
      
      data = {
        "count": record_count,
        "example": "",
        "detail": "",
        "extra": [0,0,0]
      }
      
      children = container.children()
      if children.length > 1:
        main_div = children.eq(0)
        extend_div = children.eq(1)
      
        main_child = main_div.children()
        if main_child.length > 0:
          a = main_child.eq(0)
          a.children('span').attr('style', None)    #Remove style from span
          data['extra'] = extract_id(a.attr('href'))
          data['example'] = a.html()
          
        extend_child = extend_div.children()
        if extend_child.length > 0:
          detail = extend_child.eq(0)
          data['detail'] = process_detail(detail)
          
      # Submit data
      '''
      p = requests.post(IMPORT_URL, data={
        'word_type': viewPos,
        'ws_type': wsType,
        'morpheme': keyword,
        'index': record_count,
        'content': data['example'],
        'detail': data['detail'],
        'field_id': data['extra'][0],
        'part_id': data['extra'][1],
        'sent_id': data['extra'][2]
      })'''
      
      post_queue.append({
        'word_type': viewPos,
        'ws_type': wsType,
        'morpheme': keyword,
        'index': record_count,
        'content': data['example'],
        'detail': data['detail'],
        'field_id': data['extra'][0],
        'part_id': data['extra'][1],
        'sent_id': data['extra'][2]
      })
      
      if len(post_queue) >= BATCH_LIMIT:
        p = requests.post(IMPORT_BATCH_URL, data={'data': json.dumps(post_queue)})
        post_queue = []
    
  if len(post_queue) > 0:
    p = requests.post(IMPORT_BATCH_URL, data={'data': json.dumps(post_queue)})
    post_queue = []
 
  has_next = has_next_page(page, j)
  print 'Has next page', has_next
  return has_next


if __name__ == '__main__':
  if not os.path.exists('_raw'):
    os.makedirs('_raw')

  kw = u"서"
  wsType = 'S'
  page = 1
  s = init_session(kw, wsType=wsType)
    
  has_next = True

  while has_next:
    has_next = search(s, kw, page=page, wsType=wsType)
    page += 1
    print '%d record processed' % record_count
    
  print 'Finished! Total %d record' % record_count