import json

class ContractsAnalyzer():
    def __init__(self, csv_output):
        self.csv_output = csv_output
        self.contractJsons = []
    
    def put(self,contractJson):
        self.contractJsons.append(contractJson)

    
    def summary(self):
        pass

