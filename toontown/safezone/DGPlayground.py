from direct.task import Task
from toontown.safezone import Playground
import random

class DGPlayground(Playground.Playground):
    def enter(self, requestStatus):
        Playground.Playground.enter(self, requestStatus)
        taskMgr.doMethodLater(1, self.__birds, 'DG-birds')

    def exit(self):
        Playground.Playground.exit(self)
        taskMgr.remove('DG-birds')

    def __birds(self, task):
        base.playSfx(random.choice(self.loader.birdSound))
        time = random.random() * 20.0 + 1
        taskMgr.doMethodLater(time, self.__birds, 'DG-birds')
        return Task.done
