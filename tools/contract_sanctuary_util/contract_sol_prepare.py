import os
import json
import time
import solc_utils as get_solc_versions
import subprocess
import numpy as np
from shutil import copy

'''
先加载contracts.json，
然后根据根据json信息获得contract path
'''
# 加载json文件
def load_contracts_json(file_path):
    contracts_index = []
    with open(file_path) as f:
        line = f.readline()
        while line != "":
            c = json.loads(line)
            contracts_index.append(c)
            line = f.readline()
    return contracts_index

# 将json按版本号分类
def compiler_contracts_json(contracts_index):
    contracts_version = {}
    for c in contracts_index:
        if c['compiler'] not in contracts_version:
            contracts_version[c['compiler']] = [c]
        else:
            contracts_version[c['compiler']].append(c)

    return contracts_version,sorted(contracts_version.keys(), key=lambda x: list(map(int, x.split("."))))


'''
all_contract = True, all contracts
all_contract = False, contracts can be compiled
'''
def contracts_summary(contracts_index, all_contract=False):

    balances = []
    txcounts = []
    dates = []

    num = 0
    for c in contracts_index:
        if c['solc'] == True or all_contract == True:
            balances.append(c['balance'])
            txcounts.append(c['txcount'])
            dates.append(c['date'])
            num = num + 1

    print("constracts num:", num,"\n"
        "balance sum:", np.sum(balances),"Ether\n"
        "txcount sum:", np.sum(txcounts),"\n"
        "start date:", time.strftime("%Y-%m-%d", time.localtime(np.min(dates))),"\n"
        "end date:", time.strftime("%Y-%m-%d", time.localtime(np.max(dates))),"\n"
    )

# 获得合约地址
def get_contract_path(root_path, cjson):
    return os.path.join(root_path, cjson['compiler'], cjson['address'][2:42] + '_' + cjson['name'] + '.sol')


# 对加载的json源文件文件进行格式化处理
def _format_contracts_json(contracts_index):
    solc_versions = get_solc_versions()  # 可编译的版本

    for c in contracts_index:
        if " " in c['balance']:
            balance = c['balance'].split(" ")[0].replace(",", "")
            c['balance'] = float(balance)
        else:
            c['balance'] = 0.0

        if "v" in c['compiler']:
            c['compiler'] = c['compiler'].split("v")[1]

        if c['compiler'] in solc_versions:  # 能否被本地solc编译
            c['solc'] = True
        else:
            c['solc'] = False

        c['date'] = time.mktime(time.strptime(c['date'], "%m/%d/%Y"))

    return contracts_index


def copy_sol(mainnet_path, contracts_path):
    '''
    copy contracts file from ethereum/contracts/mainnet

    constracts num: 115622
    balance sum: 2520197.1947112908 Ether
    txcount sum: 68746855
    start date: 2017-06-19
    end date: 2022-02-22
    '''

    if os.path.exists(contracts_path):
        subprocess.run(["rm", "-rf", contracts_path], stdout=subprocess.PIPE, check=True)

    contracts_line = set()  # remove duplicates
    with open(os.path.join(mainnet_path, "contracts.json")) as f:
        line = f.readline()
        while line != "":
            contracts_line.add(line)
            line = f.readline()

    contracts_index = []
    for c in contracts_line:
        contracts_index.append(json.loads(c))

    contracts_index = _format_contracts_json(contracts_index)

    #divide contracts by compiler (solc version)
    for c in contracts_index:
        if c['solc'] == False:
            continue
        # mainnet/00/address_name.sol
        source_file = os.path.join(mainnet_path, c['address'][2:4], c['address'][2:42] + "_" + c['name'] + ".sol")
        # print(source_file)
        if os.path.isfile(source_file):
            target_dir = os.path.join(contracts_path, c['compiler'])  # mainnet/version/address_name.sol
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            target_file = os.path.join(target_dir, c['address'][2:42] + "_" + c['name'] + ".sol")
            # print(target_file)
            copy(source_file, target_file)
        else:
            c['solc'] = False

    f = open(os.path.join(contracts_path,'contracts.json'), 'w+')
    for c in contracts_index:
        if c['solc'] == True:
            f.write(json.dumps(c) + "\n")
    f.close()

    contracts_summary(contracts_index)


if __name__ == "__main__":
    mainnet_path = "/data/disk_16t_2/kailun/smart_contract_centralization/smart-contract-sanctuary-ethereum/contracts/mainnet/"
    contracts_path = "/data/disk_16t_2/kailun/smart contracts/ethereum_mainnet/"

    copy_sol(mainnet_path, contracts_path)