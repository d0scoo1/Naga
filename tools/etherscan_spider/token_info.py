import os

class Token:
    '''
    PATH of the token related files
    '''
    def __init__(self,root_path,name):
        self.root_path = root_path
        self.name = name
        self.path = os.path.join(root_path,name)
        self.html_path = os.path.join(self.path,'htmls')
        self.raw_path = os.path.join(self.path,'raws')
        self.contracts_path = os.path.join(self.path,'contracts')

        self.html_json = os.path.join(self.path,'htmls.json')
        self.contracts_json = os.path.join(self.path,'contracts.json')

        self.logs = os.path.join(self.path,'logs.txt')
        self.no_contracts = os.path.join(self.path,'no_contracts.txt')

    def create_folders(self):
        paths = [self.html_path, self.raw_path, self.contracts_path]
        for path in paths:
            if not os.path.exists(path):
                os.makedirs(path)

root_path =  '/mnt/c/users/vk/naga/20220701' #'./tokens'
token_list = {
    '20' : Token(root_path,'token20'),
    '721' : Token(root_path,'token721'),
    '1155' : Token(root_path,'token1155'),
}

if __name__== '__main__':

    for token in token_list:
        token_list[token].create_folders()
