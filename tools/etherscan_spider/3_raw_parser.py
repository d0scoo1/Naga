from token_info import token_list as token
import json
import os
from tqdm import tqdm
import re
import subprocess

def __format_version(ver):
    pattern = re.compile(r'v0\.\d\.\d+')
    m = pattern.match(ver)
    if m is None:
        return ver
    f_ver = m.group(0)[1:]
    return f_ver

from solc_utils import get_solc_versions
solc_list = get_solc_versions()
solc_set = set(solc_list)
def _get_version(ver):
    f_ver = __format_version(ver)

    if f_ver in solc_set:
        return f_ver
    else:
        return 'noSolc'

def _raw_paser(_token,address):
    with open(os.path.join(_token.raw_path,address), 'r') as fr:
        raw = json.loads(fr.read())
    fr.close()

    address = address.lower()
    raw_result = raw['result'][0]
    raw_result['address'] = address
    del raw_result['ABI']
    del raw_result['ConstructorArguments']
    #del r['LicenseType']
    del raw_result['SwarmSource']
    raw_result['version'] = _get_version(raw_result['CompilerVersion'])
    
    sourceCode = raw_result['SourceCode']
    del raw_result['SourceCode']

    if sourceCode == "":  ### if no source code, skip ###
        with open( _token.no_contracts, 'a') as fa:
            fa.write(address + '\n')
        fa.close()
        return None

    sol_files = {}
    if sourceCode[0] == '{':  # multiple files
        if sourceCode[1] == '{':
            sourceCode = json.loads(sourceCode[1:-1])['sources']
        else:
            sourceCode = json.loads(sourceCode)
        
        sol_files = _solname_conflict(sourceCode)
        for key in sol_files:
            sol_files[key] = _redirect_import(sol_files[key].split('\n'))
  
    else:
        sol_files[raw_result['ContractName']+".sol"] = sourceCode
    
    ### write sol files ###
    _write_sol_files(os.path.join(_token.contracts_path,raw_result['version'],raw_result['address']),sol_files)

    return raw_result


################ utils functions ################
def _solname_conflict(sourceCode): 
    soln_keys = {}
    sol_files = {}
    for key in sourceCode:
        soln = _get_solname_sol(key)
        if soln in soln_keys:
            key1 = soln_keys[soln]
            if len(sourceCode[key]['content']) < len(sourceCode[key1]['content']): # leave the file that has the max length
                continue
        soln_keys[soln] = key
        sol_files[soln] = sourceCode[key]['content']
        
    return sol_files


def __get_solname(path):
    solname = ''
    if '/' not in path:
        solname = path
    else:
        solname = path.split('/')[-1]

    return solname.split('.sol')[0]

def _get_solname_sol(path):
    return __get_solname(path) + '.sol'

def _redirect_import(lines):
    # format lines
    for i in range(0,len(lines)):
        lines[i] = lines[i].replace('\r', '')

    for i in range(0,len(lines)):
        bare_line = lines[i].lstrip()  #
        if bare_line.find('import ') == 0:
            lines[i] = __override_import_line(bare_line)
            continue

    # recombine lines
    code = ''
    for line in lines:
        code = code + line + "\n"
    return code

def __override_import_line(import_line):

    line = import_line.replace('://', '')

    if '//' in line:
        line = import_line.split("//")[0]
    if '/*' in line:
        if '*/' in line:
            line = import_line.split("/*")[0]
        else:
            print(import_line)

    line = line.replace("\'",'\"')
    if "\"" not in line:
        return line

    ref = line.split('\"')[1]

    if '/' not in line:
        new_ref = './' + ref
    else:
        items = ref.split('/')
        new_ref = './' + items[len(items) - 1]

    return line.replace(ref,new_ref)

########### End utils functions ################

def _write_sol_files(sol_path,sol_files):
    if not os.path.exists(sol_path):
        os.makedirs(sol_path)
    for sol_name in sol_files:
        with open(os.path.join(sol_path, sol_name), 'w') as fw2:
            fw2.write(sol_files[sol_name])
        fw2.close()

def raw_parser(_token):
    ### clean folders ###
    if os.path.exists(_token.contracts_path):
        subprocess.run(["rm", "-rf", _token.contracts_path], stdout=subprocess.PIPE, check=True)
        os.makedirs(_token.contracts_path)
    
    if os.path.exists(_token.contracts_json):
        subprocess.run(["rm", "-rf", _token.contracts_json], stdout=subprocess.PIPE, check=True)

    if os.path.exists(_token.no_contracts):
        subprocess.run(["rm", "-rf", _token.no_contracts], stdout=subprocess.PIPE, check=True)

    for raw_address in tqdm(os.listdir(_token.raw_path)):
        raw_result = _raw_paser(_token, raw_address)
        
        ### write contracts_json ###
        if raw_result != None:
            with open(os.path.join(_token.contracts_path, _token.contracts_json), 'a') as fw1:
                fw1.write(json.dumps(raw_result) + '\n')
            fw1.close()

if __name__ == "__main__":
    raw_parser(token['20'])
    raw_parser(token['721'])
    raw_parser(token['1155'])

    #_raw_paser(token['721'],'0xb543f9043b387ce5b3d1f0d916e42d8ea2eba2e0')

    pass