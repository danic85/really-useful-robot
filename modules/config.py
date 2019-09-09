import configparser


class Config:
    def __init__(self):
        self.__cfg = configparser.ConfigParser()
        self.__cfg.read('../config.ini')

    def get(self, type, is_int=True, section='DEFAULT'):
        if self.__cfg and self.__cfg[section] and self.__cfg[section][type]:
            val = self.__cfg[section][type]
            if is_int:
                return int(val)
            return val
