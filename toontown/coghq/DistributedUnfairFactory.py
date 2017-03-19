from direct.directnotify import DirectNotifyGlobal
import DistributedFactory

class DistributedUnfairFactory(DistributedFactory.DistributedFactory):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedUnfairFactory')

    def __init__(self, cr):
        DistributedFactory.DistributedFactory.__init__(self, cr)

    def getFloorOuchLevel(self):
        return 8
