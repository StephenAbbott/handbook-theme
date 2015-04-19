import polib
import os
import shutil
import codecs

def info(lang):
    fp = 'translation/%s/LC_MESSAGES/all.po' % lang

    po = polib.pofile(fp)
    print po.percent_translated()
    entries = po.translated_entries()
    print entries[0].msgid
    print entries[0].msgstr


def translate_file(infile, po_entries_sorted):
    '''
    Algorithm:

    Sort translation msgids from longest to shortest so that we match larger
    segments before shorter segments.

    for each msgid:
        do simple find and replace on source using msgid and msgstr

    Adjustment:

    Problem: pofile and source file may break lines at different lengths
    meaning a simple find and replace will not work

    we can use structure of pofile source which is that sphinx breaks msgid
    paragraph so we always know that a msgid in pofile will never be more than
    a paragraph.  We can therefore split source file by paragraph and do
    matching that way
    '''
    instr = infile.read()

    paras = instr.split('\n\n')
    outparas = []
    nomatch = []
    for para in paras:
        out = match_paragraph(para, po_entries_sorted)
        if out == para:
            nomatch.append(para)
        outparas.append(out)
    outstr = '\n\n'.join(outparas)
    if len(nomatch) > 0:
        print('Failed to match %s paragraphs' % len(nomatch))
    return outstr

def match_paragraph(para, po_entries_sorted):
    for entry in po_entries_sorted:
        out = para.replace(entry.msgid, entry.msgstr)
        if out != para:
            return out
        # no match so eliminate line breaks and try replace again
        else:
            tmp = para.replace('\n', ' ').replace('  ', ' ')
            msgid = entry.msgid.replace('\n', ' ').replace('  ', ' ')
            out = tmp.replace(msgid, entry.msgstr)
            if out != tmp: # we had a match
                return out
            else: # reset out to para
                out = para
    return out
    
def get_po_entries(lang):
    path = 'translation/%s/LC_MESSAGES/all.po' % lang
    po = polib.pofile(path)
    entries = po.translated_entries()
    def comparator(x,y):
        return cmp(len(x.msgid), len(y.msgid))
    newentries = sorted(entries, comparator, reverse=True)
    return newentries

def get_all_files_to_translate(basepath):
    allthefiles = []
    for dirname, subdirs, files in os.walk(basepath):
        if '/_' in dirname:
            continue
        print dirname
        files = [ os.path.join(dirname, f)[len(basepath):].lstrip('/') for f in files if f.endswith('.rst') ]
        allthefiles.extend(files)
    return allthefiles

def translate_all(lang, source, dest):
    poentries = get_po_entries(lang)
    files = get_all_files_to_translate(source)
    for path in files:
        fullpath = os.path.join(source, path)
        fo = codecs.open(fullpath, encoding='utf8')
        out = translate_file(fo, poentries)
        destpath = os.path.join(dest, os.path.splitext(path)[0] + '.md')
        parentdir = os.path.dirname(destpath)
        if not os.path.exists(parentdir):
            os.makedirs(parentdir)
        with codecs.open(destpath, 'w', encoding='utf8') as fout:
            fout.write(out)

import pypandoc
def convert_to_markdown(instr, outstr):
    pass


class TestItAll(object):
    def test_get_po_entries(self):
        entries = get_po_entries('de')
        assert len(entries) > 300
        assert len(entries[0].msgid) > len(entries[1].msgid)

    def test_match_paragraph(self):
        para = \
'''**This handbook discusses the legal, social and technical aspects of 
open data.** It can be used by anyone but is especially 
designed for those seeking to **open up** data. It discusses the 
**why, what and how** of open data -- why to go open, what open is, 
and the how to 'open' data.'''
        entries = get_po_entries('de')
        out = match_paragraph(para, entries)
        assert out.startswith('** Dieses Handbuch'), out

    def test_translate_file(self):
        fpath = 'source/index.rst'
        entries = get_po_entries('de')
        out = translate_file(open(fpath), entries)
        assert out
        assert len(out) > 10, out[:100]
        assert not '**This handbook' in out, out[:500]

    def test_get_all_files_to_translate(self):
        out = get_all_files_to_translate('source')
        assert 'index.rst' in out, out
        assert 'introduction/index.rst' in out
    
    def test_translate_all(self):
        testdir = '/tmp/handbook-translate'
        if os.path.exists(testdir):
            shutil.rmtree(testdir)
        os.makedirs(testdir)
        translate_all('de', 'source', testdir)
        indexpath = os.path.join(testdir, 'index.md')
        assert os.path.exists(indexpath), indexpath
        content = open(indexpath).read()
        assert 'Das Open Data Handbuch' in content, content


if __name__ == '__main__':
    translated_langs = [
        'de',
        'el',
        'es',
        'fr',
        'he',
        'id',
        'is',
        'it',
        'ja',
        'ko',
        'lt_LT',
        'lv',
        'nl_BE',
        'pt_BR',
        'ro',
        'ru',
        'zh_CN',
        'zh_TW'
        ]
    pass

