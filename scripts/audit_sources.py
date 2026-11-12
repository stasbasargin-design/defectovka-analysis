#!/usr/bin/env python3
"""Неразрушающий аудит выгрузок Excel. Предупреждения не роняют CI."""
from pathlib import Path
import sys
import json
from collections import Counter
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from defectovka.xlsx_reader import cell_rows


def inspect_linked():
    counter=Counter(); examples=[]
    for row_idx,row in enumerate(cell_rows(ROOT/'data/raw/Связаные работы.xlsx'),start=1):
        if row_idx==1: continue
        counter['rows']+=1
        if not row.get('B'): counter['no_base_catalog_code']+=1
        if not row.get('D'): counter['no_related_item_name']+=1
        if not row.get('E'): counter['no_related_catalog_code']+=1
        if not row.get('G'): counter['no_brand']+=1
        if not row.get('H'): counter['no_variant']+=1
        amount=row.get('I')
        if amount:
            try:
                if float(amount)<=0: raise ValueError()
            except ValueError:
                counter['bad_quantity']+=1
                if len(examples)<30: examples.append({'excel_row':row_idx,'problem':'bad_quantity'})
    return {'counts':dict(counter),'examples':examples}


def inspect_stock():
    counter=Counter(); examples=[]
    for row_idx,row in enumerate(cell_rows(ROOT/'data/raw/остатки по складу (1).xlsx'),start=1):
        if row_idx==1: continue
        counter['rows']+=1
        if not row.get('B'): counter['no_article']+=1
        if not row.get('C'): counter['no_name']+=1
        for col,label in [('D','price'),('E','quantity')]:
            if not row.get(col): continue
            try: float(row[col].replace(',','.'))
            except ValueError:
                counter['non_numeric_'+label]+=1
                if len(examples)<30: examples.append({'excel_row':row_idx,'problem':'non_numeric_'+label})
    return {'counts':dict(counter),'examples':examples}


def main():
    result={'generated_at':datetime.now(timezone.utc).isoformat(),
            'linked_works':inspect_linked(),'stock':inspect_stock(),
            'note':'Аудит не определяет фактическую точность подбора и не изменяет файлы.'}
    output=ROOT/'reports'/'source-audit.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
