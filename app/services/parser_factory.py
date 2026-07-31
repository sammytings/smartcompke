from .parsers.generic import GenericParser
from .parsers.jumia import JumiaParser
#from .parsers.gadgetsoko import GadgetSokoParser
#from .parsers.kilimall import KilimallParser


class ParserFactory:

    @staticmethod
    def get_parser(url):

        url = url.lower()

        if "jumia" in url:
            return JumiaParser(url)

        #if "gadgetsoko" in url:
         #   return GadgetSokoParser(url)

 #       if "kilimall" in url:
  #          return KilimallParser(url)

        return GenericParser(url)