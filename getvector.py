#coding=utf-8
import urllib
from bs4 import BeautifulSoup
import os
import chardet
import threading
import time
import contextlib
from Queue import Queue
import re
import tldextract
import requests
import multiprocessing
from concurrent import futures
global path1,path2 
path1=r'D:\data1\subject1_A\file'
path2=r'D:\data1\subject1_A\out'
filelist=r'D:\data1\subject1_A\file_list.txt'
def process(filename,url,number):
        htmlfile=open('%s\\%s'%(path1,filename),'r')
        content=htmlfile.read()
        result = chardet.detect(content)
        coding = result.get('encoding')
        #print coding
        htmlfile.close()
        if (coding.startswith('GB')):
             htmlpage=content.decode('gb18030')
        else:
             htmlpage=content.decode(coding)
        soup=BeautifulSoup(htmlpage,"html.parser")
        (F1,F3)=F_url(soup,url)
        F2=ICP(soup,url)
        (F4,F5,F6,F7,F8,F9)=F_average(soup,url)
        an=[]
        an.append(F1)
        an.append(F2)
        an.append(F3)
        an.append(F4)
        an.append(F5)
        an.append(F6)
        an.append(F7)
        an.append(F8)
        an.append(F9)
        outputfile=open('%s\\%s'%(path2,filename),'w')
        #if good == 'n':
           # cha=0
       # elif good== 'd':
            #cha=1
        #elif good=='p':
            #cha=2
        outputfile.write(str(number)+' ')
        for i in range(9):
            txt=str(i+1)+':'+str(an[i])+' '
            outputfile.write(txt)


        
            
        #(F3,F4)=F_url_inout(soup,url)
        #text=text.encode('utf-8')
        #outputfile=open('%s\\%s'%(path2,filename),'w')
        #outputfile.write(text)
        outputfile.close()

def F_url(soup,url):
    href=soup.find_all(href=re.compile(r'^http[s]?',re.I))
    src=soup.find_all(src=re.compile(r'^http[s]?',re.I))
    
    #link=soup.find_all(link=re.compile(r'^http[s]?',re.I))
    links=[]
    R1=0
    Ra=0
    R2=0
    url_a=tldextract.extract(url)
    url_domain=url_a.domain
    for eachlink in  href:
        temp=eachlink.attrs['href']
        #if 'http' in temp or 'https' in temp:
        #print temp
        #print href
        Ra=Ra+1
        #print Ra
        link=tldextract.extract(temp)
        link_domain=link.domain
            #print link_domain

        if link_domain <> url_domain:
            R1=R1+1
        if link_domain == url_domain:
            R2=R2+1
    for eachlink in  src:
        temp=eachlink.attrs['src']
        #if 'http' in temp or 'https' in temp:
        #print temp
        Ra=Ra+1
        link=tldextract.extract(temp)
        link_domain=link.domain


        if link_domain <> url_domain:
            R1=R1+1
        if link_domain == url_domain:
            R2=R2+1

    
    #print R1,Ra 
    if Ra==0:
        return 0,0
    elif R1>0:
        return float(R1)/Ra,float(R2)/Ra
    else:
        return -1,-1
def ICP(soup,url):
    for script in soup(["script", "style"]):
        script.extract()    # rip it out
    text=soup.get_text()
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    text=text.encode('utf-8')
    return F_icp(text,url)
def baidu_url(word): 
    # 构建百度搜索URL；因为是查收录，所以只显示了前10个搜索结果，还可以通过rn参数来调整搜索结果的数量
    '''
    get baidu search url
    '''
    return 'http://www.baidu.com/s?wd=%s' % word


def baidu_cont(url):  
    # 获取百度搜索结果页内容
    headers = {  
    'User-Agent': 'Mozilla/4.0+(compatible;+MSIE+8.0;+Windows+NT+5.1;+Trident/4.0;+GTB7.1;+.NET+CLR+2.0.50727)'
    }  # 设置UA模拟用户，还可设置多个UA提高搜索成功率
    r = requests.get(url, headers=headers)
    return r.content


def serp_links(word):  
    #获取百度搜索结果的最终URL
    '''
    get baidu serp links with the word
    '''
    #print word.decode('utf-8').encode('gb18030')
    b_url = baidu_url(word)
    soup = BeautifulSoup(baidu_cont(b_url),"html.parser")
    b_tags = soup.find_all('h3', {'class': 't'})  # 获取URL的特征值是通过class="t"
    b_links = [tag.a['href'] for tag in b_tags]
    real_links = []
    for link in b_links:  # 使用requests库获取了最终URL，而不是快照URL
        #print link
        try:
            r = requests.get(link,timeout=2)
        except Exception as e:
            real_links.append('page404')
        else:
            real_links.append(r.url)
    return real_links



def F_icp(soup,url):
    Ra=0
    R1=0
    url_a=tldextract.extract(url)
    url_domain=url_a.domain
    #print 'real', url_domain
    #text=soup.get_text()
    #print soup
    compile_rule = re.compile(r'ICP.*\d+|备案.*\d+|经营许可证.*\d+', re.I)
    compile_list = re.findall(compile_rule, soup)
    #for e in compile_list:
        #print e.decode('utf-8').encode('gb18030')
    #print '123','\n'
    if  compile_list:
        for word in compile_list:
            index_urls=serp_links(word)
            for index_u in index_urls:
                link=tldextract.extract(index_u)
            #print link.domain
                link_domain=link.domain
                Ra=Ra+1
                if link_domain == url_domain:
                    R1=R1+1
    
        if Ra==0:
            return -1
        p=float(R1)/Ra
        if p <0.7:
            return 1
        elif p>=0.7:
            return 0
        else:
            return -1
    else:
        return -1
def F_average(soup,url):
    for script in soup(["script", "style"]):
        script.extract()    # rip it out
    text=soup.get_text()
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    text=text.encode('utf-8')
    img=soup.find_all('img')
    img_num=len(img)
    patterm_css=re.compile(r'.*css',re.I)
    css=re.findall(patterm_css,text)
    css_num=len(css)
    patterm_js=re.compile(r'.*js',re.I)
    js=re.findall(patterm_js,text)
    js_num=len(js)
    form=soup.find_all('form')
    form_num=len(form)
    Input=soup.find_all('input')
    Input_num=len(Input)
    passwd_type=soup.find_all(type='password')
    passwd_num=len(passwd_type)
    return img_num,css_num,js_num,form_num,Input_num,passwd_num


    
    
    
        
   




if __name__ == '__main__':
    print 'data path',path1
    print 'output path',path2
    file_list=open(filelist,'r')
    count=0
    count2=0
    pool=multiprocessing.Pool(processes=50)
    for file_detil in file_list.readlines():

        file_data=file_detil.split(',')
        file_number=file_data[0]
        file_name=file_data[1]
        #file_good=file_data[1]
        file_url=file_data[2]
        pool.apply_async(process,(file_name,file_url,file_number))
    pool.close()
    pool.join()
    print 'down'
