from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import requests as r
import keyboard
import time
import pandas as pd

#vsetky zmluvy
Zmluvy = pd.read_csv(r"C:\Users\filip.markovic\OneDrive - Hlavne mesto SR Bratislava\Python - Spyder scripts\Zmluvy_zoznam.csv", encoding='latin1', sep = ';')
Kody = Zmluvy['Kod_zmluvy'].tolist()
options = Options()
options.binary_location = r"C:\Users\filip.markovic\AppData\Local\Mozilla Firefox\firefox.exe"

#funkcie na ziskanie url a nasledne stiahnutie pdf
def scrape_CRZ(kodZmluvy):
    driver = webdriver.Firefox(executable_path="C:\\Users\\filip.markovic\\OneDrive - Hlavne mesto SR Bratislava\\Python - Spyder scripts\\geckodriver.exe", firefox_options=options)
    driver.get("https://www.crz.gov.sk")
    #driver.maximize_window()

    time.sleep(1)
    searchWindow = driver.find_element_by_xpath("//*[@id='frm_filter_3_nazov']")
    searchWindow.send_keys(kodZmluvy)

    priceWindow = driver.find_element_by_xpath("//*[@id='frm_filter_3_art_suma_spolu_od']")
    priceWindow.send_keys("1")

    time.sleep(1)
    searchButton = driver.find_element_by_xpath("//*[@id='frm_filter_3_odoslat']")
    searchButton.click()

    time.sleep(1)
    try:
        target = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/table/tbody/tr[2]/td[2]/a")
    except Exception:
        pass
    finally:
        target.click()
    
    currentUrl = str(driver.current_url)
    print(currentUrl.split("/")[-2])
    IDnumber = int(currentUrl.split("/")[-2]) + 1
    driver.close()
    return(IDnumber)  
    
   
def downloadPDF(IDnumber):
    driver = webdriver.Firefox(executable_path="C:\\Users\\filip.markovic\\OneDrive - Hlavne mesto SR Bratislava\\Python - Spyder scripts\\geckodriver.exe",firefox_options=options)
    try:
        pdfUrl = "https://www.crz.gov.sk/data/att/{}_dokument.pdf".format(IDnumber)
        driver.get(pdfUrl)
        download = driver.find_element_by_xpath('//*[@id="download"]')
    except Exception:
        pdfUrl = "https://www.crz.gov.sk/data/att/{}_dokument.pdf".format(int(IDnumber)+1)
        driver.get(pdfUrl)
        download = driver.find_element_by_xpath('//*[@id="download"]')
        print("Zmluva c. {} je vynimocna (+2)".format(IDnumber-1) )
    except Exception:
        print("Zmluva c. {} je vynimocna (neviem preco)".format(IDnumber-1) )
    finally:
        download.click()
        time.sleep(3)
        keyboard.press_and_release("enter")
        driver.close()

#funckie v akcii
for cislo in Kody:
    url = scrape_CRZ(cislo)
    downloadPDF(url)
    print("PDF - {} bolo stiahnute...".format(cislo))
    
    
downloadPDF(scrape_CRZ('0135-PRB-2018'))
print(Kody_2018)


#testik pred vytvorenim pdf parsovacej funkcie
import pdfplumber as pdfp
with pdfp.open(r"C:\Users\filip.markovic\OneDrive - Hlavne mesto SR Bratislava\MDV\3509077_dokument.pdf") as pdf:
        page = pdf.pages[1]
        text = page.extract_text()
print(text)

for row in text.split('\n'):
    if row.startswith("Dotácia"):
        if str(row.split()[-4]) + str(row.split()[-3]) == "bežnéhoštandardu":
            print("bezny")       


#funkcia ktora:
    # 1) iteruje cez pdf vo foldri (directory)
    # 2) z 1. a 2. strany pdf extrahuje text z riadka, ktory zacina alebo obsahuje speficicke slovoe/slovne spojenie
    # 3) extrahovany text prida do vybraneho listu (standard, obec, cena, typ, kolaudacia) 
import pdfplumber as pdfp
from PyPDF2 import PdfFileReader
import os

directory = "C:\\Users\\filip.markovic\\OneDrive - Hlavne mesto SR Bratislava\\MDV_TEST"
obec = []                   
standard = [] 
typ = [] 
cena = []  
kolaudacia = []              
def getData(directory):
    for filename in os.scandir(directory):
        fp = filename.path        
        pdf = pdfp.open(fp)
        page = pdf.pages[0]
        text = page.extract_text()
        page2 = pdf.pages[1]
        text2 = page2.extract_text()
        for row in text.split('\n'):
            rs = row.split()
            b = "bežného"
            n = "nižšieho"
            if row.startswith("Dotácia"):
                if rs[-5] == b or rs[-4] == b or rs[-3] == b or rs[-2] == b or rs[-1] == b:
                    standard.append("bezny") 
                elif rs[-5] == n or rs[-4] == n or rs[-3] == n or rs[-2] == n or rs[-1] == n:
                    standard.append("nizsi")
                else:
                    standard.append("something went wrong")
        for row in text.split('\n'):  
            if row.startswith("Obec"):
                 obec.append(row.split("Obec ")[-1])
            elif row.startswith("Mesto"):
                 obec.append(row.split("Mesto ")[-1])
        for row in text2.split('\n'):
            stringZ1 ="zhotoviteľ:"
            stringZ2 ="zhotoviteľ/"
            stringP ="predávajúci:"
            if row.find(stringZ1) != -1 or row.find(stringZ2) != -1:
                 typ.append("vystavba")
            elif row.find(stringP) != -1:
                 typ.append("kupa")
        for row in text2.split('\n'): 
            string ="termín kolaudácie stavby:"
            if row.find(string) != -1:
                 kolaudacia.append(str(row.split()[-1]))
        for row in text2.split('\n'):  
            if row.startswith("vrátane dane z pridanej hodnoty:"):
                 cena.append(row.split("vrátane dane z pridanej hodnoty:  ")[-1])
 
#test fukncie
getData(directory)
print(standard)                                
print(obec)   
print(typ)  
print(kolaudacia) 
print(cena) 

#dataframe z listov s udajmi 
PDFextrakt = pd.DataFrame(list(zip(obec,standard,typ,kolaudacia,cena)),
                              columns = ['obec','standard','typ','kolaudacia','cena'])
#export do csv
print(PDFextrakt)
PDFextrakt.to_csv("C:\\Users\\filip.markovic\\OneDrive - Hlavne mesto SR Bratislava\\MDV\\extrakt.csv", encoding='utf-8-sig')

                   
