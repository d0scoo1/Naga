def detect_lack_event_functions(self):
    """
    Before Functions: detect_owners_bwList
    如果一个 function 写了 state variable，则应当发送一个 event，提醒用户，这里寻找缺少的 event 的 function。
    我们并不考虑 event 的参数，关于 event 和实际操作不一致的问题：TokenScope: Automatically Detecting Inconsistent Behaviors of Cryptocurrency Tokens in Ethereum
    """

    lack_event_owner_functions = []
    lack_event_user_functions = []
    for f in self.state_var_written_functions:
        if not f.is_constructor_or_initializer and len(f.events) == 0:
            if f in self.owner_in_condition_functions:
                lack_event_owner_functions.append(f)
            else:
                lack_event_user_functions.append(f)
    
    self.lack_event_functions = lack_event_owner_functions + lack_event_user_functions
    self.lack_event_owner_functions = lack_event_owner_functions
    self.lack_event_user_functions = lack_event_user_functions
