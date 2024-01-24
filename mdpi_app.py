from selenium  import webdriver
import pandas as pd
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome import options
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import os, time, subprocess, random

### Function to use Express VPN for changing IP address to avoid bot detection ####
### I've commented this function call below as some users may not use Express VPN
def ChangeVPN():
    countries = ["Georgia","Serbia","Moldova",'"North Macedonia"',"Jersey","Monaco","Slovakia",'Lebanon','Argentina',
                    "Slovenia","Croatia","Albania","Cyprus","Liechtenstein","Malta","Ukraine",'Ghana','Chile','Colombia',
                    "Belarus","Bulgaria","Hungary","Luxembourg","Montenegro","Andorra",'Morocco','Honduras','Guatemala',
                    '"Czech Republic"',"Estonia","Latvia","Lithuania","Poland","Armenia","Austria",'Cuba','Panama',
                    "Portugal","Greece","Finland","Belgium","Denmark","Norway","Iceland","Ireland",'Bermuda','Mexico',
                    "Spain","Romania","Italy","Sweden","Turkey","Singapore",'Kenya','Israel','"South Africa"','Canada',
                    "Australia",'"South Korea - 2"',"Malaysia","Pakistan",'"Sri Lanka"',"Kazakhstan",'Bahamas','Brazil',
                    "Thailand","Indonesia",'"New Zealand"',"Cambodia","Vietnam","Macau",'Jamaica',
                    "Mongolia","Laos","Bangladesh","Uzbekistan","Myanmar","Nepal","Brunei","Bhutan",'Venezuela',
                    '"United Kingdom"', '"United States"',"Japan", "Germay", '"Hong Kong"', "Netherlands",'Bolivia',
                    "Switzerland","Algeria","France","Egypt"] 
    b = random.choice(countries)
    print(f"Selected Country is {b}")
        
    process = subprocess.Popen(["powershell",".\expresso.exe", "connect", "--change",
                            b],shell=True)
    result = process.communicate()[0]
    print(result)

class MdpiScrape(uc.Chrome):
    
    def __init__(self,
                keep_alive=True, keyword = ''):
        
        data_dir = keyword.replace(' ','_')
        
        if not os.path.exists(os.getcwd()+'\\' +data_dir):
             
            os.mkdir(data_dir)
        chrome_options = uc.ChromeOptions()
        prefs = {"download.default_directory" : os.getcwd()+'\\' +data_dir}
        chrome_options.add_experimental_option("prefs",prefs)
        chrome_options.add_argument("--disable-lazy-loading")
        chrome_options.add_argument("--remote-allow-origins=*")
        chrome_options.add_argument("--disable-print-preview")
        
        chrome_options.add_argument("--disable-stack-profiler")
        chrome_options.add_argument("--disable-background-networking")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("excludeSwitches=enable-automation")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-browser-side-navigation")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-popup-blocking")
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Current Working Dir: {script_dir}")
        chromeProfile = "\Includes\Data_files\data\Chrome_profile"
        ## Add your chrome executable location as browser_path ##
        browser_path = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
        print(f"Browser Executable Path is : {os.path.join(script_dir,browser_path)}")
        super(MdpiScrape, self).__init__(options=chrome_options,
                                            browser_executable_path=browser_path,
                                            suppress_welcome=True,debug=True,keep_alive=True,
                                            user_multi_procs=False)#user_data_dir= os.getcwd()+chromeProfile), version_main=121, 
        self.keep_alive = keep_alive
        
        self.maximize_window()
        
        
    def __exit__(self,exc_type , exc_val, exc_to):
        if not self.keep_alive:
            print(f" Check for processes still running ? {self.service.assert_process_still_running()}")
            print(f"Service.process.pid for chrome bot is : {self.service.process.pid}")
            self.stop_client()
            self.service._terminate_process()
            #subprocess.run(['kill',f'{self.service.process.pid}'],shell=True)
            
            self.quit()
        
    def land_first_page(self):
        #self.execute_script("window.open('');")
        #self.switch_to.window(self.window_handles[0])
        self.get('https://www.mdpi.com/user/login/') 
        
        username = self.find_element(By.ID, 'username')
        username.send_keys("pritham.pgc@gmail.com")
        password = self.find_element(By.ID, 'password')
        password.send_keys('PgC@500072')
        
        submit = self.find_element(By.XPATH, '//input[@class="button submit-btn"]')
        submit.click()
        
        
    ## Function to get total number of result pages for your serch query ##   
    def extractPages(self, st_yr, end_yr,keyword):
                  
        self.get(f'https://www.mdpi.com/search?sort=pubdate&page_count=200&year_from={st_yr}&year_to={end_yr}&q={keyword}&view=compact') 
        WebDriverWait(self, 20).until(EC.element_to_be_clickable((By.ID,'CybotCookiebotDialogBodyLevelButtonLevelOptinAllowallSelection'))).click()
        pages = self.find_element(By.XPATH, '//div[@class="columns large-6 medium-6 small-12"]')
        print(pages.text)
        total_pages = int(pages.text.split('of')[1].replace('.','').strip())
        
        print(f'total pages ==> {total_pages}')
        return total_pages
    
    ## Function to download data in tabular format from links of articles ##
    def extractEmails(self, page_no,start_yr, end_yr, keyword):
        
            try:   
                self.get(f'https://www.mdpi.com/search?sort=pubdate&page_no={str(page_no+1)}&page_count=200&year_from={start_yr}&year_to={end_yr}&q={keyword}&view=compact')
                WebDriverWait(self, 20).until(EC.element_to_be_clickable((By.XPATH, '//a[@class="export-options-show export-element export-expanded"]'))).click()
                time.sleep(5)
                print('@'*10)
                #print(show_export.text)
                #show_export.click()
                checkbox = self.find_element(By.ID, 'selectUnselectAll')
                checkbox.click()
                self.find_element(By.XPATH, '//div[@class="listing-export"]').click()
                self.find_element(By.XPATH, '//div[@class="chosen-drop"]/ul/li[contains(text(), "Tab-delimited")]').click()
                time.sleep(5)
                self.find_element(By.ID, 'articleBrowserExport_top').click()
            except Exception as e:
                print(f'Exception occurred while downloading file: ==> {str(e)}')
                ## ChangeVPN()
                ## uncomment above line if you use Express VPN
                curr_page = page_no
                    
                time.sleep(10)
                    
                self.refresh()
                pass
                    
                   
##########################################################################

if __name__ == '__main__':
    keyword_input = input('Enter any Keyword: ')
    with MdpiScrape(keyword=keyword_input) as bot:
        bot.land_first_page()
        pages_number = bot.extractPages(st_yr='2017',end_yr='2023',keyword=keyword_input)
        for i in range(pages_number):
            
            bot.extractEmails(page_no=i,start_yr='2017',end_yr='2023',keyword=keyword_input)
        time.sleep(10)
        os.system(r'.\\kill.bat ' + str(bot.browser_pid))
                    
        ########################################
        ######## Parse downloaded files ########
        ########################################
    files_in_cwd = os.listdir(os.getcwd()+ '\\'+ keyword_input.replace(' ','_'))
    txt_files = [keyword_input.replace(' ','_')+'\\'+file for file in files_in_cwd if '.txt' in file]
    print('&&&&&&&&&&&&&')
    print(txt_files)
    input_files = keyword_input.replace(" ","_")+"\\" + '*.txt'
    out_file = keyword_input.replace(" ","_")+"\\" + keyword_input.replace(" ","_")+"_results.txt"
    copy_process = subprocess.Popen(['powershell', 'Get-Content', input_files, '| Set-Content', out_file], shell=True)
    result = copy_process.communicate()[0]
    print(result)
    df = pd.read_csv(out_file, sep = '\t',skip_blank_lines=True, skipinitialspace=True)
    df.rename(columns = {'AUTHOR':'names', 'EMAIL ':'emails'}, inplace = True)
    print(df)
    df2 = df[['names', 'emails']].copy(deep=True)
    
    del df
    df2['names'].mask(df2['names'].str.contains(';') == True, other = df2['names'].str.split(';'), inplace = True)
    df2['emails'].mask(df2['emails'].str.contains(';') == True, other = df2['emails'].str.split(';'), inplace = True)

    #df2=df2.set_index(['names', 'emails']).apply(pd.Series.explode).reset_index()
    df2['len_names'] = df2['names'].str.len()
    df2['len_mails'] = df2['emails'].str.len()
    df3 = df2[df2['len_names'] == df2['len_mails']].copy(deep=True)
    df3 = df3.explode(['names','emails'])
    df3.reset_index(drop = True)
    df3['names']=df3['names'].str.strip()
    df3['emails']=df3['emails'].str.strip()
    df3[['Last_Name','First_Name']] = df3['names'].str.split(',',n=1, expand = True)

    df3['First_Name'] = df3['First_Name'].str.strip()
    df3['Last_Name'] = df3['Last_Name'].str.strip()
    df3['Names'] = df3['First_Name'] + " " + df3['Last_Name']
    
    #for file in txt_files:
    df4 = df3.loc[:,['emails', 'Names']].copy(deep=True)
    df5 = df4[df4['emails'] != ''].copy(deep=True)
    df6 = df5.drop_duplicates('emails')
    df6.to_csv(out_file.replace('.txt', '')+'.csv', encoding = 'utf-8', index = False)
    del df3, df2, df4, df5 , df6 
    
    print('Results are successfully Saved....')
       
     
        