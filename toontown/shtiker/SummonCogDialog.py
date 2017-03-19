from direct.gui.DirectGui import *
from panda3d.core import *
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import StateData
from toontown.toonbase import TTLocalizer
from toontown.toontowngui import TTDialog
from toontown.toonbase import ToontownGlobals
from toontown.suit import SuitDNA
from toontown.suit import Suit
from toontown.battle import SuitBattleGlobals
from toontown.toon import NPCToons

class SummonCogDialog(DirectFrame, StateData.StateData):
    notify = DirectNotifyGlobal.directNotify.newCategory('SummonCogDialog')
    notify.setInfo(True)

    def __init__(self, suitIndex):
        DirectFrame.__init__(self, parent=aspect2dp, pos=(0, 0, 0.3), relief=None, image=DGG.getDefaultDialogGeom(), image_scale=(1.6, 1, 1.07), image_pos=(0, 0, 0.09), image_color=ToontownGlobals.GlobalDialogColor, text=TTLocalizer.SummonDlgTitle, text_scale=0.12, text_pos=(0, 0.5), borderWidth=(0.01, 0.01), sortOrder=NO_FADE_SORT_INDEX)
        StateData.StateData.__init__(self, 'summon-cog-done')
        self.initialiseoptions(SummonCogDialog)
        self.suitIndex = suitIndex
        base.summonDialog = self
        self.popup = None
        self.suitName = SuitDNA.suitHeadTypes[self.suitIndex]
        self.suitFullName = SuitBattleGlobals.SuitAttributes[self.suitName]['name']
        return

    def unload(self):
        if self.isLoaded == 0:
            return None
        self.isLoaded = 0
        self.exit()
        DirectFrame.destroy(self)
        return None

    def load(self):
        if self.isLoaded == 1:
            return None
        self.isLoaded = 1
        gui = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
        guiButton = loader.loadModel('phase_3/models/gui/quit_button')
        self.head = Suit.attachSuitHead(self, self.suitName)
        z = self.head.getZ()
        self.head.setPos(-0.4, -0.1, z + 0.14)
        self.suitLabel = DirectLabel(parent=self, relief=None, text=self.suitFullName, text_font=ToontownGlobals.getSuitFont(), pos=(-0.4, 0, -0.085), scale=0.07)
        closeButtonImage = (gui.find('**/CloseBtn_UP'), gui.find('**/CloseBtn_DN'), gui.find('**/CloseBtn_Rllvr'))
        buttonImage = (guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR'))
        disabledColor = Vec4(0.5, 0.5, 0.5, 1)
        base.cr.lmao = self
        self.summonBuildingButton = DirectButton(parent=self, relief=None, text=TTLocalizer.SummonDlgButton1, image=buttonImage, image_scale=(1.7, 1, 1), image3_color=disabledColor, text_scale=0.06, text_pos=(0, -0.01), pos=(0.3, 0, 0.37), command=self.issueSummons, extraArgs=['building'])
        self.summonInvasionButton = DirectButton(parent=self, relief=None, text=TTLocalizer.SummonDlgButton2, image=buttonImage, image_scale=(1.7, 1, 1), image3_color=disabledColor, text_scale=0.06, text_pos=(0, -0.01), pos=(0.3, 0, 0.245), command=self.issueSummons, extraArgs=['invasion'])
        self.summonCogdoButton = DirectButton(parent=self, relief=None, text=TTLocalizer.SummonDlgButton3, image=buttonImage, image_scale=(1.7, 1, 1), image3_color=disabledColor, text_scale=0.06, text_pos=(0, -0.01), pos=(0.3, 0, 0.12), command=self.issueSummons, extraArgs=['cogdo'])
        self.summonSkelInvasionButton = DirectButton(parent=self, relief=None, text=TTLocalizer.SummonDlgButton4, image=buttonImage, image_scale=(1.7, 1, 1), image3_color=disabledColor, text_scale=0.051, text_pos=(0, -0.01), pos=(0.3, 0, -0.005), command=self.issueSummons, extraArgs=['skelinvasion'])
        self.summonWaiterInvasionButton = DirectButton(parent=self, relief=None, text=TTLocalizer.SummonDlgButton5, image=buttonImage, image_scale=(1.7, 1, 1), image3_color=disabledColor, text_scale=0.056, text_pos=(0, -0.01), pos=(0.3, 0, -0.13), command=self.issueSummons, extraArgs=['waiterinvasion'])
        self.summonV2InvasionButton = DirectButton(parent=self, relief=None, text=TTLocalizer.SummonDlgButton6, image=buttonImage, image_scale=(1.7, 1, 1), image3_color=disabledColor, text_scale=0.048, text_pos=(0, -0.01), pos=(0.3, 0, -0.255), command=self.issueSummons, extraArgs=['v2invasion'])
        self.summonGoldInvasionButton = DirectButton(parent=self, relief=None, text=TTLocalizer.SummonDlgButton7, image=buttonImage, image_scale=(1.7, 1, 1), image3_color=disabledColor, text_scale=0.044, text_pos=(0, -0.01), pos=(0.3, 0, -0.38), command=self.issueSummons, extraArgs=['goldinvasion'])
        self.statusLabel = DirectLabel(parent=self, relief=None, text='', text_wordwrap=12, pos=(0.3, 0, 0.3), scale=0.07)
        self.cancel = DirectButton(parent=self, relief=None, image=closeButtonImage, pos=(0.72, 0, -0.366), command=self.__cancel)
        gui.removeNode()
        guiButton.removeNode()
        self.hide()
        return

    def enter(self):
        if self.isEntered == 1:
            return None
        self.isEntered = 1
        if self.isLoaded == 0:
            self.load()
        self.disableButtons()
        self.enableButtons()
        self.popup = None
        base.transitions.fadeScreen(0.5)
        self.show()
        return

    def exit(self):
        if self.isEntered == 0:
            return None
        self.isEntered = 0
        self.cleanupDialogs()
        base.transitions.noTransitions()
        self.ignoreAll()
        self.hide()
        messenger.send(self.doneEvent, [])
        return None

    def cleanupDialogs(self):
        self.head = None
        if self.popup != None:
            self.popup.cleanup()
            self.popup = None
        return

    def cogSummonsDone(self, returnCode, suitIndex, buildingId):
        self.cancel['state'] = DGG.NORMAL
        if self.summonsType == 'building' or self.summonsType == 'cogdo':
            if returnCode == 'success':
                building = base.cr.doId2do.get(buildingId)
                dnaStore = base.cr.playGame.dnaStore
                buildingTitle = dnaStore.getTitleFromBlockNumber(building.block)
                buildingInteriorZone = building.zoneId + 500 + building.block
                npcName = TTLocalizer.SummonDlgShopkeeper
                npcId = NPCToons.zone2NpcDict.get(buildingInteriorZone)
                if npcId:
                    npcName = NPCToons.getNPCName(npcId[0])
                if buildingTitle:
                    self.statusLabel['text'] = TTLocalizer.SummonDlgBldgSuccess % (npcName, buildingTitle)
                else:
                    self.statusLabel['text'] = TTLocalizer.SummonDlgBldgSuccess2
            elif returnCode == 'badlocation':
                self.statusLabel['text'] = TTLocalizer.SummonDlgBldgBadLoc
            elif returnCode == 'fail':
                self.statusLabel['text'] = TTLocalizer.SummonDlgInvasionFail
            elif returnCode == 'disabled':
                self.statusLabel['text'] = TTLocalizer.SummonDlgBldgNoCogdos
        elif self.summonsType.endswith('invasion'):
            if returnCode == 'success':
                self.statusLabel['text'] = TTLocalizer.SummonDlgInvasionSuccess
            elif returnCode == 'busy':
                self.statusLabel['text'] = TTLocalizer.SummonDlgInvasionBusy % self.suitFullName
            elif returnCode == 'fail':
                self.statusLabel['text'] = TTLocalizer.SummonDlgInvasionFail

    def hideSummonButtons(self):
        self.summonBuildingButton.hide()
        self.summonInvasionButton.hide()
        self.summonCogdoButton.hide()
        self.summonSkelInvasionButton.hide()
        self.summonWaiterInvasionButton.hide()
        self.summonV2InvasionButton.hide()
        self.summonGoldInvasionButton.hide()

    def issueSummons(self, summonsType):
        if summonsType == 'building' or summonsType == 'cogdo':
            text = TTLocalizer.SummonDlgBuildingConf
        elif summonsType == 'invasion':
            text = TTLocalizer.SummonDlgInvasionConf
        elif summonsType == 'skelinvasion':
            text = TTLocalizer.SummonDlgSkelInvasionConf
        elif summonsType == 'waiterinvasion':
            text = TTLocalizer.SummonDlgWaiterInvasionConf
        elif summonsType == 'v2invasion':
            text = TTLocalizer.SummonDlgV2InvasionConf
        elif summonsType == 'goldinvasion':
            text = TTLocalizer.SummonDlgGoldInvasionConf
        text = text % self.suitFullName

        def handleResponse(resp):
            self.popup.cleanup()
            self.popup = None
            self.reparentTo(self.getParent(), NO_FADE_SORT_INDEX)
            base.transitions.fadeScreen(0.5)
            if resp == DGG.DIALOG_OK:
                self.notify.info('issuing %s summons for %s' % (summonsType, self.suitIndex))
                self.accept('cog-summons-response', self.cogSummonsDone)
                self.summonsType = summonsType
                self.doIssueSummonsText()
                base.localAvatar.d_reqCogSummons(self.summonsType, self.suitIndex)
                self.hideSummonButtons()
                self.cancel['state'] = DGG.DISABLED
            return

        self.reparentTo(self.getParent(), 0)
        self.popup = TTDialog.TTDialog(parent=aspect2dp, style=TTDialog.YesNo, text=text, fadeScreen=1, command=handleResponse)

    def doIssueSummonsText(self):
        self.disableButtons()
        self.statusLabel['text'] = TTLocalizer.SummonDlgDelivering

    def disableButtons(self):
        self.summonBuildingButton['state'] = DGG.DISABLED
        self.summonInvasionButton['state'] = DGG.DISABLED
        self.summonCogdoButton['state'] = DGG.DISABLED
        self.summonSkelInvasionButton['state'] = DGG.DISABLED
        self.summonWaiterInvasionButton['state'] = DGG.DISABLED
        self.summonV2InvasionButton['state'] = DGG.DISABLED
        self.summonGoldInvasionButton['state'] = DGG.DISABLED

    def enableButtons(self):
        if base.localAvatar.hasCogSummons(self.suitIndex, 'building'):
            self.summonBuildingButton['state'] = DGG.NORMAL
        if base.localAvatar.hasCogSummons(self.suitIndex, 'invasion'):
            self.summonInvasionButton['state'] = DGG.NORMAL
        if base.localAvatar.hasCogSummons(self.suitIndex, 'cogdo'):
            self.summonCogdoButton['state'] = DGG.NORMAL
        if base.localAvatar.hasCogSummons(self.suitIndex, 'skelinvasion'):
            self.summonSkelInvasionButton['state'] = DGG.NORMAL
        if base.localAvatar.hasCogSummons(self.suitIndex, 'waiterinvasion'):
            self.summonWaiterInvasionButton['state'] = DGG.NORMAL
        if base.localAvatar.hasCogSummons(self.suitIndex, 'v2invasion'):
            self.summonV2InvasionButton['state'] = DGG.NORMAL
        if base.localAvatar.hasCogSummons(self.suitIndex, 'goldinvasion'):
            self.summonGoldInvasionButton['state'] = DGG.NORMAL

    def __cancel(self):
        self.exit()
