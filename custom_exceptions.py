
class ChampionException(Exception):
    def __init__(self, message='No se reconoce el campeón.'):
        self.message = message
        super().__init__(self.message)


class RandomCatException(Exception):
    def __init__(self, message='No se ecnontró un michi :('):
        self.message = message
        super().__init__(self.message)


class NotPlayedException(Exception):
    def __init__(self, message='Creo que no lo he jugado.'):
        self.message = message
        super().__init__(self.message)
