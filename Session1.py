# -*- coding: utf-8 -*-
"""
Created on Sun May 30 19:50:15 2021

@author: filip.markovic
"""

import pandas as pd
Zmluvy = pd.read_csv(r'C:\Users\filip.markovic\OneDrive - Hlavne mesto SR Bratislava\Python - Spyder scripts\Zmluvy_zoznam.csv', sep = ';')
Kody = Zmluvy['Kod_zmluvy'].tolist()
print(Kody)