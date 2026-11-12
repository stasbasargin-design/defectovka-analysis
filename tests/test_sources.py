"""Проверки неизменности и доступности базовых выгрузок."""
import hashlib
import json
import sys
from pathlib import Path
from unittest import TestCase
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from defectovka.xlsx_reader import cell_rows


class TestSources(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT/'data'/'manifest.json').read_text(encoding='utf-8'))['files']

    def test_six_source_files_and_hashes(self):
        self.assertEqual(len(self.manifest),6)
        for item in self.manifest:
            with self.subTest(file=item['name']):
                file = ROOT/item['path']
                self.assertTrue(file.is_file())
                self.assertEqual(hashlib.sha256(file.read_bytes()).hexdigest(), item['sha256'])
                with ZipFile(file) as archive:
                    self.assertIsNone(archive.testzip())
                    self.assertIn('xl/workbook.xml',archive.namelist())

    def test_linked_work_column_headers(self):
        first = next(cell_rows(ROOT/'data'/'raw'/'Связаные работы.xlsx'))
        for col, text in {'B':'№ по каталогу','C':'Авторабота/Причина обращения',
                'D':'Связанная авторабота/номенклатура','E':'№ по каталогу (для поиска)',
                'F':'Модель','G':'Марка','H':'Вариант комплектации','I':'Количество'}.items():
            self.assertEqual(first.get(col),text)

    def test_stock_headers(self):
        first = next(cell_rows(ROOT/'data'/'raw'/'остатки по складу (1).xlsx'))
        self.assertEqual([first.get(x) for x in 'ABCDE'],
                         ['Производитель','Артикул','Номенклатура','Цена','Количество'])

    def test_vehicle_headers(self):
        first = next(cell_rows(ROOT/'data'/'raw'/'автомобили.xlsx'))
        self.assertEqual([first.get(x) for x in 'ABCD'],
                         ['VIN','Марка','Модель автомобиля','Вариант комплектации'])

    def test_price_reports_and_cp_template_present(self):
        for file in ('Прайс на автоработы NPR.xlsx','Прайс-лист на автоработы.xlsx'):
            text = ' '.join(v for r in list_first_rows(ROOT/'data'/'raw'/file,10) for v in r.values())
            self.assertIn('Прайс-лист авторабот',text)
        text = ' '.join(v for r in list_first_rows(ROOT/'data'/'raw'/'КП образец.xlsx',12) for v in r.values())
        self.assertIn('Коммерческое предложение',text)


def list_first_rows(file,n):
    from itertools import islice
    return list(islice(cell_rows(file),n))
