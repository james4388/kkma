import xlrd
import os

from django.db.models import F

from .models import Example, Phrase


def extract_phrases(content, rlist, skip=2):
    rlist = rlist[:-skip] 
    start_index = None if len(rlist) % 2 == 0 else 0    # First item is not pairs
    phrases = []
    phrase = ''
    for pos in rlist:
        if start_index is not None:
            phrase = content[start_index:pos[0]]
            start_index = None
            phrases.append(phrase)
        else:
            start_index = pos[0]
    return phrases


def import_xls(file_path, morpheme, used_in, **kwargs):
    if not os.path.isfile(file_path):
        return False, 'File not found'
    
    # Open workbook
    wb = xlrd.open_workbook(file_path, formatting_info=True)
    
    try:
        sheet = wb.sheet_by_name(used_in)
    except xlrd.XLRDError:
        return False, 'Sheet %s does not exist' % used_in
        
    nrows = sheet.nrows
    ncols = sheet.ncols
    
    content_col = kwargs.get('content_col', 1)
    if content_col > ncols - 1:
        return False, 'content_col %d (from 0) larger than number of columns %d' % (content_col, ncols)
    
    category_col = kwargs.get('category_col', 3)
    has_category_col = ncols > category_col
    prefix_col = kwargs.get('prefix_col', 4)
    has_prefix_col = ncols > prefix_col
    suffix_col = kwargs.get('suffix_col', 5)
    has_suffix_col = ncols > suffix_col
    
    start_from = kwargs.get('start_from', 1)
    if start_from > nrows - 1:
        return False, 'start_from %d (from 0) larger than number of rows %d' % (start_from, nrows)
    
    examples = []
    for row in xrange(start_from, nrows):
        data = {
            'morpheme': morpheme,
            'used_in': used_in
        }
        content = sheet.cell(row, content_col).value
        content = content.upper() if content else ''
        data['content'] = content
        if has_category_col:
            category = sheet.cell(row, category_col).value
            data['category'] = category if category.strip() else None
        if has_prefix_col:
            data['prefix'] = sheet.cell(row, prefix_col).value
        if has_suffix_col:
            data['suffix'] = sheet.cell(row, suffix_col).value
        phrases = extract_phrases(
            content,
            sheet.rich_text_runlist_map.get((row, content_col), []),
            kwargs.get('exclude_rich', 2)
        )
        
        if not kwargs.get('dry_run', False):
            example, created = Example.objects.update_or_create(
                content=data['content'], morpheme=data['morpheme'], used_in=data['used_in'],
                defaults=data
            )
            for phrase in phrases:
                phrase_obj, _ = Phrase.objects.get_or_create(phrase=phrase)
                if created:
                    Phrase.objects.filter(id=phrase_obj.id).update(count=F('count') + 1)
                example.phrases.add(phrase_obj)
            
        data['phrases'] = phrases
        examples.append(data)

        
    return True, examples