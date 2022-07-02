#https://beautifulsoup.readthedocs.io/zh_CN/v4.4.0/#id8

from bs4 import BeautifulSoup
import os
import json
from tqdm import tqdm
from token_info import token_list as token

def __token_721_1155_tr(tr):
    tds = tr.find_all('td')
    t = {}
    '''
    index = tds[0].get_text()
    address = tds[1].find("a")['href'][7:]
    transfers_24 = tds[2].get_text().replace(',','')
    transfers_3d_7d = tds[3].get_text().replace(',','')
    return  index +","+ address +"," +transfers_24 + "," + transfers_3d_7d
    '''
    t['index'] = tds[0].get_text()
    t['address'] = tds[1].find("a")['href'][7:].lower()
    t['transfers_24'] = tds[2].get_text().replace(',', '')
    t['transfers_3d_7d'] = tds[3].get_text().replace(',', '')
    return json.dumps(t)


def _token_721_1155(r_path,w_path):
    ds = []
    for i in tqdm(range(1, len(os.listdir(r_path)) + 1)):
        html = os.path.join(r_path, str(i) + '.html')
        soup = BeautifulSoup(open(html), 'lxml')
        tbody = soup.find('tbody')
        trs = tbody.find_all('tr')
        for tr in trs:
            r = __token_721_1155_tr(tr)
            ds.append(r)

    with open(w_path,'w') as f:
        for line in ds:
            f.write(line +"\n")
    f.close()
    print("count",len(ds))


def _token20(r_path,w_path):

    ds = []
    for i in tqdm(range(1,len(os.listdir(r_path))+1)):
        i = str(i)
        html = os.path.join(r_path,str(i)+'.html')
        soup = BeautifulSoup(open(html), 'lxml')
        tbody = soup.find('tbody')
        trs = tbody.find_all('tr')
        for tr in trs:
            r = __token20_tr(tr)
            ds.append(r)

    with open(w_path,'w') as f:
        for line in ds:
            f.write(line +"\n")
    f.close()
    print("count",len(ds))

def __token20_tr(tr):
    tds = tr.find_all('td')
    ''' csv
    index = tds[0].get_text()
    address = tds[1].find("a")['href'][7:]
    name = tds[1].find("a").next_element

    price = tds[2].next_element
    price_btc = tds[2].div.next_element[:-4]
    price_eth = tds[2].div.span.next_element[:-4]

    change = tds[3].get_text().strip()
    volume = tds[4].get_text().strip().replace(',','')
    circulatingMarketCap = tds[5].get_text().strip().replace(',','')
    onChainMarketCap = tds[6].get_text().strip().replace(',','')
    holders = tds[7].next_element.replace(',','')
    return index+","+address+","+name+","\
           +price+","+price_btc+","+price_eth+","\
           +change +"," + volume + "," \
           + circulatingMarketCap + "," + onChainMarketCap + "," + holders
    '''
    t = {}
    t['index'] = tds[0].get_text()
    t['address'] = tds[1].find("a")['href'][7:].lower()
    t['name'] = tds[1].find("a").next_element

    t['price'] = tds[2].next_element
    t['price_btc'] = tds[2].div.next_element[:-4]
    t['price_eth'] = tds[2].div.span.next_element[:-4]

    t['change'] = tds[3].get_text().strip()
    t['volume'] = tds[4].get_text().strip().replace(',','')
    t['circulatingMarketCap'] = tds[5].get_text().strip().replace(',','')
    t['onChainMarketCap'] = tds[6].get_text().strip().replace(',','')
    t['holders'] = tds[7].next_element.replace(',','')

    return json.dumps(t)

if __name__ == "__main__":
    _token20(token['20'].html_path,token['20'].html_json)
    _token_721_1155(token['721'].html_path,token['721'].html_json)
    _token_721_1155(token['1155'].html_path,token['1155'].html_json)
    #pass