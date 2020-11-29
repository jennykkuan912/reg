from bs4 import BeautifulSoup
import requests, sys, re
import pandas as pd
import time
import grouplist
class downloader(object):
 
    def __init__(self):
        self.server = 'https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/'
        self.target = 'https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/'
        self.urls = []
        self.nums = 0
        self.df = pd.DataFrame()
        self.groupname = grouplist.getgrouplist()


    def get_download_url(self):
        req = requests.get(self.target)
        html = req.text
        div_bf = BeautifulSoup(html,'lxml')
        
        div = div_bf.find_all('table', id= "ctl00_ctl00_ctl00_ctl00_Content_Content_Content_Content_GridView1")
        
        a_bf = BeautifulSoup(str(div[0]),'lxml')
        a = a_bf.find_all('a')
        
        for each in a:
            url = self.server+each.get('href')
            if(url not in self.urls):
                self.urls.append(url)
        self.nums = len(self.urls)
    
    def get_reg(self,txt):
        
        flag = 1
        regex = ""
        head = ""
        des_num = 1
        group_head = ""
        group_whole = ""
        for ele in txt:
            if ele == '':
                continue
            ele = ele.replace('(','\(')
            ele = ele.replace(')','\)')
            match_description = re.findall("([\S\s]*\.$)",ele)
            match_group_head = re.findall("([\S\s]*?):$",ele)
            match_group_name = re.findall("([\S\s]*?):",ele)

            if match_group_head:
                match = match_group_head
                group_head = ""
                for eles in re.split("\s",match[0]):
                    eles = eles.replace('-','')
                    eles = eles.replace('\(','')
                    eles = eles.replace('\)','')
                    group_head += eles[:3] 
                group_whole = match[0]
                regex += match[0]+":(?:\s+|\S)"
            elif match_group_name:
                match = match_group_name
                #match = re.findall("([\S\s]*?):",ele)
                group_name = ""
                for eles in re.split("\s",match[0]):
                    eles = eles.replace('-','')
                    eles = eles.replace('\(','')
                    eles = eles.replace('\)','')
                    group_name += eles[:3]
                if group_head=="":
                    #self.groupname[group_name]=match[0]
                    pattern_name = self.groupname[group_name]
                    regex += match[0]+":(?:\s+|\S)"+"(?P<"+pattern_name+">.*)\s+"
                    
                else:
                    pattern_name = self.groupname[group_head+group_name]
                    regex += match[0]+":(?:\s+|\S)"+"(?P<"+pattern_name+">.*)\s+"

                
            else:
                match = ele
                match = match.replace('(','\(')
                match = match.replace(')','\)')
                #regex += "(?P<Description"+str(des_num)+">"+match+")\s"
                pattern_name = self.groupname["Description"+str(des_num)]
                regex += "(?P<"+pattern_name+">.*)\s+"
                #regex += match
                des_num += 1
        #print(regex)
        return regex[:-3]
    def get_contents(self, target):
        req = requests.get(target)
        html = req.text
        bf = BeautifulSoup(html,'lxml')
        block = bf.find_all('div', class_ = "block")
        block = BeautifulSoup(str(block[0]),'lxml')
        eventHeader= block.find_all('h2')
        eventExample = block.find_all('p',class_="EventExample")
        eventID = re.findall("\d+",eventHeader[0].text)[0]
        #data = {"HEAD":eventHeader[0].text,"EX":example,"REG":reg, "DICT":regex_dict}
        reg = ""
        example = ""
        tmp = ""
        tmp2 = []
        #data = {"HEAD":eventHeader[0].text,"EX":example,"REG":reg, "DICT":regex_dict}
        for content in eventExample:
            texts = content.text.replace(':\xa0\xa0',': ')
            texts = texts.replace(':\xa0',': ')
            texts = texts.replace('\xa0','')

            tmp =  re.sub("\n\r\n|\r\n \t|\r\n |\n |\t\t|\r\n|\n|\t",' ',texts)
            texts = re.sub("\t",'',texts)
            texts = re.split("\n\r\n|\r\n |\n |\r\n|\n",texts)
            if(len(tmp2) !=0 and texts[0]==tmp2[0]) or texts[:12] == "Example from" or texts[:9] == "Server 20":
                break
            tmp2 = tmp2+texts
            example += (tmp+' ')
        print(eventID)
        data = {"ID":eventID,"EX":example,"LIST":tmp2}
        self.df = self.df.append(data,ignore_index=True)
    
    def get_csv(self):
        # 準備傳入 
        df = pd.read_csv('content_m1.csv',encoding='cp1252')
        ID = df['ID']
        EX = df['EX']
        LIST = df['LIST']
        regs =[]
        regex_dicts = []
        df1 = pd.DataFrame()
        for i in range(ID.size):
            id_a = ID[i]
            ex_a = EX[i]
            list_a = LIST[i].strip('\'][\'').replace('\'', '').split(', ') 
            reg = self.get_reg(list_a)
            regs.append(reg)
            regex_dict = []
            try:
                regex_dict = [m.groupdict() for m in re.finditer(reg,ex_a)]
                #print(regex_dict)
                regex_dicts.append(str(regex_dict))
            except Exception as e:
                #print(f'An Error occurred: {e}')
                regex_dicts.append(str(e))
                pass
            print(len(regex_dict))
            data = {"ID":id_a,"EX":ex_a,"LIST":list_a, "REG":reg, "DICT":{} if len(regex_dict)==0 else regex_dict[0]}
            print(id_a)
            df1 = df1.append(data,ignore_index=True)
        print(type(dict("")))
        #df1["DICT"] = df1["DICT"].apply(lambda x : dict(((x))) )
        #df3 = df1["DICT"].apply(pd.Series )
        #result = pd.concat([df1, df3], axis=1).drop('DICT', axis=1)

 
        filename = time.strftime("%Y%m%d%H%M%S", time.localtime()) 
        df1.to_csv (r'output/result'+filename+'.csv', index = False, header=True)
        #print(self.groupname,sep = "\n")
        print('Done!')

        
    
    def writer(self, path, text):
        write_flag = True
        with open(path, 'a', encoding='utf-8') as f:
            f.writelines(text)
            f.write('\n\n')
    def save_content(self):
        print('Start!')
        self.get_download_url()
        print("NUM:", dl.nums)
        for i in range(dl.nums):
            print(dl.urls[i])
            self.get_contents(dl.urls[i])
            sys.stdout.flush()
        self.df.to_csv (r'content.csv', index = False, header=True)
        print('Done!')
 
if __name__ == "__main__":
    dl = downloader()
    #dl.save_content()
    dl.get_csv()

    