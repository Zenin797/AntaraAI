from langchain_community.utilities import StackExchangeAPIWrapper

stackexchange = StackExchangeAPIWrapper()

respose = stackexchange.run("zsh: command not found: python")
print(respose)