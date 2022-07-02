
import subprocess

openzeppelin_dir = '/mnt/c/Users/vk/naga/openzeppelin-contracts'

def get_solc_versions():
    """
    get a list of all the supported versions of solidity, sorted from earliest to latest
    :return: ascending list of versions, for example ["0.4.0", "0.4.1", ...]
    """
    result = subprocess.run(["solc-select", "versions"], stdout=subprocess.PIPE, check=True)
    solc_versions = result.stdout.decode("utf-8").split("\n")

    # there's an extra newline so just remove all empty strings
    solc_versions = [version.split(" ")[0] for version in solc_versions if version != ""]
    
    solc_versions = sorted(solc_versions, key=lambda x: list(map(int, x.split("."))))
    return solc_versions

def set_solc(solc_ver):
    '''
    set the global solc version
    '''
    subprocess.run(["solc-select", "use", solc_ver], stdout=subprocess.PIPE, check=True)

def get_solc_remaps(version='0.8.0',openzeppelin_dir = openzeppelin_dir):
    '''
    get the remaps for a given solc version
    '''

    v = int(version.split('.')[1])

    if v == 5:
        return "@openzeppelin/=" + openzeppelin_dir + "/openzeppelin-contracts-solc-0.5/"
    if v == 6:
        return "@openzeppelin/=" + openzeppelin_dir + "/openzeppelin-contracts-solc-0.6/"
    if v == 7:
        return "@openzeppelin/=" + openzeppelin_dir + "/openzeppelin-contracts-solc-0.7/"  
    if v == 8:
        return "@openzeppelin/=" + openzeppelin_dir + "/openzeppelin-contracts-solc-0.8/"

    return "@openzeppelin/=" + openzeppelin_dir + "/openzeppelin-contracts-solc-0.8/"


if __name__ == "__main__":
    #set_solc("0.5.5")
    #get_solc_versions()
    print(get_solc_versions())