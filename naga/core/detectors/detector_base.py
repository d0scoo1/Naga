
def init_detect(self):
    self.exp_svars_dict = dict() # svar:StateVariable -> (label:str, rw:str)
    for svar in self.all_state_vars:
        self.exp_svars_dict[svar] = {'label': None,'rw': None,}

def _set_state_vars_label(self,label,svars):
    for svar in svars:
        self.exp_svars_dict[svar]['label'] = label

def _get_no_label_svars(self, svars):
    no_label_svars = [svar for svar in self.exp_svars_dict if self.exp_svars_dict[svar]['label'] == None]
    return [svar for svar in svars if svar in no_label_svars]

def _get_label_svars(self, label):
    return [svar for svar in self.exp_svars_dict if self.exp_svars_dict[svar]['label'] == label]
