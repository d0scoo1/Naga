
from naga.printers.abstract_printer import AbstractPrinter

class NagaSummary(AbstractPrinter):

    def output(self):
        txt = ""
        if self.naga.contracts_erc20:
            txt += "ERC20:\n"
            for c in self.naga.contracts_erc20:
                txt += "{}\n".format(c.name)
        if self.naga.contracts_erc721:
            txt += "ERC721:\n"
            for c in self.naga.contracts_erc721:
                txt += "{}\n".format(c.name)
        if self.naga.contracts_erc1155:
            txt += "ERC1155:\n"
            for c in self.naga.contracts_erc1155:
                txt += "{}\n".format(c.name)
        return txt