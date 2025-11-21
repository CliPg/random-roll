class mapper:
    def __init__(self, **kwargs):
        self.map = kwargs
        self.queries = self.__doc__.format_map(self.map)

        import sqlite3