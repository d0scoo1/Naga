
import urllib.request
import time
import sys
import os
from token_info import token_list as token
from tqdm import tqdm


header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.39'
    #'User-Agent':'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}


def _request_loop(save_folder, url, start_page, end_page):
    for i in tqdm(range(start_page, end_page + 1)):
        page_url = url + str(i)
        request = urllib.request.Request(page_url, headers=header)
        reponse = urllib.request.urlopen(request).read()

        fw = open(os.path.join(save_folder, str(i) +".html"), "wb")
        fw.write(reponse)
        fw.close()

        time.sleep(1)

# total 930
def _token20(save_folder):
    url = "https://etherscan.io/tokens?ps=100&p="
    _request_loop(save_folder,url, 1, 10) # token20 total 19 pages


# 10000
def _token721(save_folder):
    url = "https://etherscan.io/tokens-nft?ps=100&p="
    _request_loop(save_folder,url, 1, 100) 

# 5000
def _token1155(save_folder):
    url = "https://etherscan.io/tokens-nft1155?ps=100&p="
    _request_loop(save_folder,url, 1, 50) 

#2022年3月15日15点26分 UTC-8
if __name__ == "__main__":
    #_token20(token['20'].html_path)
    #_token721(token['721'].html_path)
    #_token1155(token['1155'].html_path)
    pass



