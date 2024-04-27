import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
import time
from bs4 import BeautifulSoup
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import streamlit as st


def ScrapeData(username: str, password: str, internetlevel=5):
    """Input: username, password and internetlevel from 0-5. Defaults to 5 (highspeed).
    Returns a dataframe of all the attendance on portal.zsvkm website"""
    internetlevel=(5-internetlevel)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    ptg=Service(ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install())
    st.write(ptg)
    driver = webdriver.Chrome(
        service= ptg
        ,options=options)

    url = "https://portal.svkm.ac.in/usermgmt/login"

    driver.get(url)

    driver.implicitly_wait(5*internetlevel)

    try:
        username_field = driver.find_element(By.ID,"userName")
        password_field = driver.find_element(By.ID,"userPwd")

        username_field.send_keys(username)
        password_field.send_keys(password)

        password_field.send_keys(Keys.RETURN)

        time.sleep(5*internetlevel)
        driver.get('https://portal.svkm.ac.in/DJSCE/viewDailyAttendanceByStudent')

        time.sleep(2)

        tabular_button=driver.find_element(By.ID,"libRes")
        tabular_button.click()
        time.sleep(2)
        dropdown_element = driver.find_element(By.XPATH,"/html/body/div/div[4]/div[3]/div/div[1]/div[1]/div/div[3]/div[2]/div/div/div/div[2]/div[2]/label/select")

        dropdown = Select(dropdown_element)

        dropdown.select_by_value("-1")

        time.sleep(2*internetlevel)

        fullhtml=driver.page_source

        table=driver.find_element(By.ID,"outboxTable")
        table_text=table.get_attribute('innerHTML')

    finally:
        driver.quit()
    
    table_text=table_text.replace('\t','').replace('\n','')
    fullhtml=fullhtml.replace('\t','').replace('\n','')
    soup=BeautifulSoup(fullhtml,"html.parser")
    data = str(soup.find("table"))

    dfs = pd.read_html(data)
    return dfs[0]

def ProcessData(df, startdate='2024-01-01', enddate=None):
    
    df.columns = ['ID', 'Student ID', 'Course', 'Month', 'Year', 'Date', 'Time', 'Status']
    
    df['Status']=df['Status'].apply(lambda x: 1 if x=='P' or x==1 else 0)
    df['Date']=pd.to_datetime(df['Date'],dayfirst=True)
    
    cutoff_date = pd.to_datetime(startdate)
    cutoff_end_date=pd.to_datetime(enddate)
    
    if enddate is None:
        result_2024_01_01 = df[df['Date'] > cutoff_date].groupby('Course')['Status'].agg(['mean', 'sum','count']).sort_values(by='mean', ascending=True)
        # result_2024_01_01['Total Lectures'] = result_2024_01_01['count']
        # result_2024_01_01['Attended Lectures'] = result_2024_01_01['mean'] * result_2024_01_01['count']
        df = df[df['Date'] > cutoff_date]
    else:
        print('hi')
        result_2024_01_01 = df[df['Date'] > cutoff_date ][ df['Date']< cutoff_end_date].groupby('Course')['Status'].agg(['mean','sum', 'count']).sort_values(by='mean', ascending=True)#.groupby('Course')['Status'].mean().sort_values() * 100
        result_2024_01_01['mean']=result_2024_01_01['mean']*100
        df=df[df['Date'] > cutoff_date ][ df['Date']< cutoff_end_date]
    
    return (result_2024_01_01['mean'].mean(),result_2024_01_01['sum'].sum(),result_2024_01_01['count'].sum()),result_2024_01_01, df
