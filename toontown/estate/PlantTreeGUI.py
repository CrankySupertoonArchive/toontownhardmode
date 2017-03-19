from direct.directnotify import DirectNotifyGlobal
from direct.showbase.ShowBase import *
from toontown.toonbase import TTLocalizer
import string
from direct.fsm import StateData

class PlantTreeGUI(StateData.StateData):
    notify = DirectNotifyGlobal.directNotify.newCategory('PlantTreeGUI')

    def __init__(self, doneEvent):
        self.doneEvent = doneEvent
        self.oldActivateMode = base.localAvatar.inventory.activateMode
        base.localAvatar.inventory.setActivateMode('plantTree')
        base.localAvatar.inventory.show()
        self.accept('inventory-selection', self.__handleInventory)
        self.accept('inventory-pass', self.__handleCancel)
        return

    def destroy(self):
        self.ignore('inventory-selection')
        self.ignore('inventory-pass')
        base.localAvatar.inventory.setActivateMode(self.oldActivateMode)
        base.localAvatar.inventory.hide()
        return

    def __handleInventory(self, track, level):
        if base.localAvatar.inventory.numItem(track, level) > 0:
            messenger.send(self.doneEvent, [True, track, level])
        else:
            self.notify.error("An item we don't have: track %s level %s was selected." % (track, level))

    def __handleCancel(self):
        messenger.send(self.doneEvent, [False, None, None])
        return
