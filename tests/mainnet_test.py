from naga_test import NagaTest

class MainnetTest(NagaTest):
    def __init__(self, tag, contractsJson_path, contract_dir, output_dir, is_clean_env=False, erc_force=None) -> None:
        super().__init__(tag, contractsJson_path, contract_dir, output_dir, is_clean_env, erc_force)