
class Library():

    def __init__(self, type):
        self.type = type

    def get_title_list(self, domain, search_keyword, provider, type):
        print('get_title_list')

    @staticmethod
    def get_library(type):
        if type == 'BC':
            from bookcube import Bookcube
            return Bookcube(type)
        elif type == 'KB':
            from kyobo import Kyobo
            return Kyobo(type)
        elif type == 'KN':
            from kyobo_new import KyoboNew
            return KyoboNew(type)
        elif type == 'YS':
            from yes24 import Yes24
            return Yes24(type)
        elif type == 'SL':
            from seoul import Seoul
            return Seoul(type)

        return