"""Read-only XLSX parser for lightweight source checks (Python stdlib)."""
import re
from xml.etree import ElementTree as ET
from zipfile import ZipFile

NS = {'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def cell_rows(filename, sheet_name='xl/worksheets/sheet1.xml'):
    """Итерировать непустые строки первой таблицы, сохраняя буквы колонок."""
    with ZipFile(filename) as z:
        shared = []
        if 'xl/sharedStrings.xml' in z.namelist():
            with z.open('xl/sharedStrings.xml') as handle:
                for _, element in ET.iterparse(handle, events=('end',)):
                    if element.tag.endswith('}si'):
                        shared.append(''.join(t.text or '' for t in element.findall('.//x:t', NS)))
                        element.clear()
        with z.open(sheet_name) as handle:
            for _, element in ET.iterparse(handle, events=('end',)):
                if element.tag.endswith('}row'):
                    out = {}
                    for c in element.findall('x:c',NS):
                        col = re.match(r'[A-Z]+',c.attrib.get('r',''))
                        if not col:
                            continue
                        v = c.find('x:v',NS)
                        inline = c.find('x:is',NS)
                        if v is not None and v.text is not None:
                            value = v.text
                            if c.attrib.get('t')=='s':
                                value = shared[int(value)]
                        elif inline is not None:
                            value = ''.join(t.text or '' for t in inline.findall('.//x:t',NS))
                        else:
                            value = ''
                        if str(value).strip():
                            out[col.group()] = str(value).strip()
                    yield out
                    element.clear()
