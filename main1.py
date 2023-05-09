from selenium import webdriver
from selenium.webdriver.chrome.options import Options,ChromiumOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pprint
import pandas as pd
from lxml import *
import requests

# funtion to initiate driver with given url and return driver object
def initiateDriver(url):
    option = Options()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=option)
    driver.get(url)
    return driver

# function to parse HTML page
def HTMLparser(driver):
    pageSource = driver.page_source
    soup = BeautifulSoup(pageSource,'lxml')
    return soup

# function to scrape 2023 website
def scrapeContent1(soup,driver):
    tables = soup.find_all('table')

    row_lst = []
    #iterate throught tables in HTML
    for table in tables:
        # iterate through rows of table
        for row in table.find_all('tr'):
            # iterate through cells of each row and extract info
            for cell in row.find_all('td'):
                contents = cell.contents
                strong_tag = cell.find('strong')
                span_tags = cell.find_all('span')
                span_tag = cell.find('span')
                text = ''
                emailCounter = 0
                data_lst = []
                if len(contents) >1:
                    telephoneNo = None
                    for content in contents:
                        if content.name == 'br':
                            text += '\n'
                        elif content.name == 'script':
                            continue
                        elif contents.index(content)==0:
                            name = content.string
                        elif "M:" in content.string:
                            if "|" in content.string:
                                mobileNo = content.string.replace("M:","").replace(" ","").split("|")
                            else:
                                mobileNo = content.string.replace("M:","").replace(" ","")
                        elif content.name == 'span':
                            emailCounter +=1
                            if emailCounter==1:
                                email = content.string
                            else:
                                email+=", " + content.string
                        elif "T:" in content.string:

                            if "|" in content.string:
                                telephoneNo = content.string.replace("T:", "").split("|")
                            elif ";" in content.string:
                                telephoneNo = content.string.replace("T:", "").split(";")
                            else:
                                telephoneNo = content.string.replace("T:", "").strip()
                        else:
                            text += content.string.strip()
                            text=text.replace("E:","")
                            text = text.replace('\n',' ')
                            text = text.replace('|', ' ')
                            text = text.strip()
                    #appending data in list
                    data_lst.append(name)
                    data_lst.append(mobileNo)
                    data_lst.append(email)
                    data_lst.append(telephoneNo)
                    data_lst.append(text.strip())
                    #appending list in outer list
                    row_lst.append(data_lst)


                    # # print(f'Name: {name}\nMobile No: {mobileNo}\nEmail: {email}\nTelephone No:{telephoneNo}\nJob: {text}')
                    # fileContent += f'Name: {name}\nMobile No: {mobileNo}\nEmail: {email}\nTelephone No: {telephoneNo}\nJob: {text}'


    #making list elements strings separated ','
    for row in row_lst:
        if isinstance(row[1], list):
            row[1] = ", ".join(row[1])
    #making dataframe from list created above
    data = pd.DataFrame(row_lst,columns=['Name',"Mobile No.",'Email','Telephone No.','Job'])
    #filling empty cells with 'Null'
    data.fillna(value='Null',inplace = True)
    #Creating csv files
    data.to_csv('Philippines-base-chapters-2023.csv',index=False)

#function to scrape 2018 website
def scrapeContent2(soup,driver):
    table = soup.find("table")
    rows = table.find_all("tr")
    row_lst = []
    # iterate through rows in HTML table
    for row in rows:

        try:
            row['class']
            Class = True
        except :
            Class = False

        if Class == False:
            td = row.find_all('td')[0]

            contents = td.find("p").contents

            telephoneNo = None
            facebook=None
            job = ''
            emailCounter = 0
            data_lst = []
            # iterate through cells of each row and extract info
            for content in contents:

                if content.string is None:
                    continue
                if content.name == 'br':
                    print("\n")
                elif content.name == 'script':
                    continue
                elif contents.index(content) == 0:
                    name = content.string.replace('\xa0',' ')
                elif content.name == 'span':
                    emailCounter += 1
                    if emailCounter == 1:
                        email = content.string.replace("Email:","").strip()
                    else:
                        email += ", " + content.string.replace("Email:","").strip()
                elif "Tel. No,:"in content.string or "Tel. No.:" in content.string or "(085)" in content.string:

                    if "|" in content.string:
                        telephoneNo = content.string.replace("Tel. No,:", "").replace("Tel. No.:", "").strip().split("|")
                    elif ";" in content.string:
                        telephoneNo = content.string.replace("Tel. No,:", "").replace("Tel. No.:", "").strip().split(";")
                    else:
                        telephoneNo = content.string.replace("Tel. No,:", "").replace("Tel. No.:", "").strip()
                elif "Facebook:" in content.string or " (@pnapalawan)"  in content.string or content.name:
                    facebook = content.string.replace("Facebook:","").strip()
                else:
                    job += content.string.strip()
                    job = job.replace("Email:","").replace("Facebook:","")
            # appending data in list
            data_lst.append(name)
            data_lst.append(email)
            data_lst.append(telephoneNo)
            data_lst.append(job)
            data_lst.append(facebook)
            row_lst.append(data_lst)
            # print(f'Name: {name}\nEmail: {email}\nTelephone No:{telephoneNo}\nJob: {job}\nFacebook: {facebook}\n\n')
    # making list elements strings separated ','
    for row in row_lst:
        if isinstance(row[1], list):
            row[1] = ", ".join(row[1])
    # making dataframe from list created above
    data = pd.DataFrame(row_lst,columns=['Name',"Email",'Telephone No.','Job','Facebook'])
    # filling empty cells with 'Null'
    data.fillna(value='Null',inplace = True)
    # Creating csv files
    data.to_csv('Philippines-base-chapters-2018.csv',index=False)



    driver.close()
if __name__ == "__main__":
    driver = initiateDriver('https://pna-ph.org/chapters/philippine-chapters/975-philippine-based-chapters-2023')
    soup = HTMLparser(driver)
    scrapeContent1(soup,driver)
    driver1 = initiateDriver("https://pna-ph.org/chapters/philippine-chapters/102-philippine-based-chapters-2018")
    soup_1 = HTMLparser(driver1)
    scrapeContent2(soup_1,driver1)
