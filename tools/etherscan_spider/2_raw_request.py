import urllib.request
import json
import time
import os
from  multiprocessing import Process,Queue
from tqdm import tqdm
from token_info import token_list as token

base_url = "https://api.etherscan.io/api?module=contract&action=getsourcecode"
apikey = "&apikey=99111UXSQPVIU93JMZIHC3ZNFN4JQGDJ77" # input your api key, you can get it from https://etherscan.io/myapikey


def producer(q,path):

    local_addrs = set()
    for addr in os.listdir(os.path.join(path,'raws')):
        local_addrs.add(addr)
    print('local',len(local_addrs))

    contracts = []
    with open(os.path.join(path,'htmls.json'), 'r') as fr:
        line = fr.readline()
        while line != '':
            c = json.loads(line)
            if c['address'] not in local_addrs:
                contracts.append(c)
            line = fr.readline()
    fr.close()

    for c in tqdm(contracts):
        q.put(c)
        time.sleep(0.2)


def consumer(q,path):

    while 1:
        c = q.get()
        if c:
            _request_one(c['address'],os.path.join(path,'raws'))
        else:
            time.sleep(0.1)
            break

def _request_one(addr,save_path):
    url = base_url + apikey + "&address=" + addr
    request = urllib.request.Request(url)
    reponse = urllib.request.urlopen(request, timeout=10).read()  # 10s timeout
    r = json.loads(reponse.decode('utf-8'))

    if r['status'] == '1' and r['message'] == 'OK':
        with open(os.path.join(save_path, addr), 'w') as fw:
            fw.write(json.dumps(r))
        fw.close()

        # Proxy == 1
        r = r['result'][0]
        if r['Proxy'] == '1' and r['Implementation'] != '':
           _request_one(r['Implementation'],save_path)

    elif r['status'] == '0' and r['message'] == 'NOTOK':
        if r['result'] == "Max rate limit reached":
            print('Max rate limit reached')
            _request_one(addr,save_path)
        else:
            print(addr,json.dumps(r))

if __name__ == "__main__":
    
    #path = token['20'].path
    path = token['721'].path
    #path = token['1155'].path

    q = Queue(5)

    p1 = Process(target=producer,args=(q,path))

    c1 = Process(target=consumer,args=(q, path))
    c2 = Process(target=consumer, args=(q, path))
    c3 = Process(target=consumer, args=(q, path))
    c4 = Process(target=consumer, args=(q, path))
    c5 = Process(target=consumer, args=(q, path))

    tasks = [p1,c1,c2,c3,c4,c5]
    [t.start() for t in tasks]

    p1.join()
    q.put(None)
    q.put(None)
    q.put(None)
    q.put(None)
    q.put(None)
    print('finish')

    #crytic-compile '0x009c43b42aefac590c719e971020575974122811' --export-dir 'tokens' --etherscan-apikey 99111UXSQPVIU93JMZIHC3ZNFN4JQGDJ77 --etherscan-only-source-code