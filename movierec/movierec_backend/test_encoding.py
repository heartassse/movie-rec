# -*- coding: utf-8 -*-
import csv

csv_path = r"c:\Users\heartassse\Desktop\bishe\movierec\archive(3)\1\comments.csv"

encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin1', 'cp936', 'utf-16']

for enc in encodings:
    try:
        with open(csv_path, 'r', encoding=enc, errors='ignore') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            content = row['CONTENT'][:50]
            print(f"{enc:15s}: {content}")
    except Exception as e:
        print(f"{enc:15s}: ERROR - {str(e)[:40]}")
