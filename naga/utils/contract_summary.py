
from naga.core.state_variable_naga import DType, VarLabel, StateVarN, DMethod

def state_variables(self):
    summary = {
        'svars': [],
        'svars_detection': {},
        'svars_label': {},
        'multistage_owners': [],
        'state_variables_label_rw': {},
        #'state_variables_rw': {},
    }

    for svar in self.svarn_pool.values(): 
        summary['svars'].append(svar.toJson())

    for dt in DType: 
        summary['svars_detection'][dt.value] = [svar.name for svar in self.get_svars_by_dtype(dt)]
    for label in VarLabel: 
        summary['svars_label'][label.value] = [svar.name for svar in self.get_svars_by_label(label)]

    summary['multistage_owners'] = [svar.name for svar in self.multistage_owners]

    return summary

def modifiers(self):
    summary = {'all_modifiers':[]}
    for m in self.contract.modifiers:
        modifier = {
            'name': m.name,
            'state_variables_read':[svar.name for svar in m.all_state_variables_read()],
            'state_variables_written': [svar.name for svar in m.all_state_variables_written()],
            'solidity_variables_read':[svar.name for svar in m.all_solidity_variables_read()],
        }
        summary['all_modifiers'].append(modifier)

    return summary

def functions(self):
    summary = {'functions':[]}
    for f in self.functions:
        f_summary = {
            'name': f.function.full_name,
            'owner_in_condition': f in self.owner_in_condition_functions,
            #'parameters':f.function.parameters,
            'state_variables_read':[svar.name for svar in f.function.all_state_variables_read()],
            'state_variables_written': [svar.name for svar in f.function.all_state_variables_written()],
            'solidity_variables_read':[svar.name for svar in f.function.all_solidity_variables_read()],
            'conditions': [r._print() for r in f.conditions],
            
        }
        summary['functions'].append(f_summary)

    return summary

def calls(self):

    all_functions = [f for f in self.contract.functions + self.contract.modifiers]
    internal_calls = 0
    external_calls = 0
    for f in all_functions:
        internal_calls += len(f.internal_calls)
        external_calls += len(f.high_level_calls)
    return {
        'internal_calls': internal_calls,
        'external_calls': external_calls,
    }

def collect_summary(self):
    for d in self.detectors:
        self.summary.update(d.summary())

    self.summary.update(calls(self))
    self.summary.update(state_variables(self))
    self.summary.update(modifiers(self))
    self.summary.update(functions(self))