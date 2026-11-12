import sys
from pathlib import Path
from unittest import TestCase

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from defectovka.rules import maintenance_interval, exclude_agreed, sum_parts_within_defect


class TestMaintenance(TestCase):
    def test_10k_window(self):
        self.assertEqual(maintenance_interval(9000,10000),10000)
        self.assertEqual(maintenance_interval(11000,10000),10000)
        self.assertEqual(maintenance_interval(10000,10000),10000)
        self.assertIsNone(maintenance_interval(8999,10000))
        self.assertIsNone(maintenance_interval(11001,10000))

    def test_15k_step(self):
        self.assertEqual(maintenance_interval(14950,15000),15000)
        self.assertEqual(maintenance_interval(29000,15000),30000)
        self.assertIsNone(maintenance_interval(13000,15000))

    def test_invalid_or_ambiguous(self):
        with self.assertRaises(ValueError):
            maintenance_interval(10000,0)
        self.assertIsNone(maintenance_interval(7500,5000,tolerance=3000))


class TestSelection(TestCase):
    def test_agreed_work_not_added_twice(self):
        work = [{'code':'A-1'},{'code':'B-2'}]
        self.assertEqual(exclude_agreed(work,['A-1']),[{'code':'B-2'}])

    def test_same_part_merges_only_inside_defect(self):
        rows=[{'defect_id':'d1','code':'P-1','quantity':2},
              {'defect_id':'d1','code':'P-1','quantity':3},
              {'defect_id':'d2','code':'P-1','quantity':4}]
        self.assertEqual(sum_parts_within_defect(rows),[
            {'defect_id':'d1','code':'P-1','quantity':5.0},
            {'defect_id':'d2','code':'P-1','quantity':4.0}])

    def test_zero_quantity_rejected(self):
        with self.assertRaises(ValueError):
            sum_parts_within_defect([{'defect_id':'d1','code':'P-1','quantity':0}])
