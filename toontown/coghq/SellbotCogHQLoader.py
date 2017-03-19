from direct.directnotify import DirectNotifyGlobal
from direct.fsm import StateData
import CogHQLoader
from toontown.toonbase import ToontownGlobals
from direct.gui import DirectGui
from toontown.toonbase import TTLocalizer
from toontown.toon import Toon
from direct.fsm import State
from direct.actor.Actor import Actor
import MegaCorpInterior
import HardFactoryInterior
import UnfairFactoryInterior
import FactoryExterior
import FactoryInterior
import SellbotHQExterior
import SellbotHQBossBattle
from toontown.battle import BattleParticles
from direct.interval.LerpInterval import LerpHprInterval
from direct.interval.IntervalGlobal import *
import random
from pandac.PandaModules import DecalEffect, NodePath
aspectSF = 0.7227

class SellbotCogHQLoader(CogHQLoader.CogHQLoader):
    notify = DirectNotifyGlobal.directNotify.newCategory('SellbotCogHQLoader')

    def __init__(self, hood, parentFSMState, doneEvent):
        CogHQLoader.CogHQLoader.__init__(self, hood, parentFSMState, doneEvent)
        self.fsm.addState(State.State('factoryExterior', self.enterFactoryExterior, self.exitFactoryExterior, ['quietZone', 'factoryInterior', 'cogHQExterior']))
        for stateName in ['start', 'cogHQExterior', 'quietZone']:
            state = self.fsm.getStateNamed(stateName)
            state.addTransition('factoryExterior')

        self.fsm.addState(State.State('factoryInterior', self.enterFactoryInterior, self.exitFactoryInterior, ['quietZone', 'factoryExterior']))
        self.fsm.addState(State.State('megaCorpInterior', self.enterMegaCorpInterior, self.exitMegaCorpInterior, ['quietZone', 'factoryExterior']))
        self.fsm.addState(State.State('hardFactoryInterior', self.enterHardFactoryInterior, self.exitHardFactoryInterior, ['quietZone', 'factoryExterior']))
        self.fsm.addState(State.State('unfairFactoryInterior', self.enterUnfairFactoryInterior, self.exitUnfairFactoryInterior, ['quietZone', 'factoryExterior']))
        for stateName in ['quietZone']:
            state = self.fsm.getStateNamed(stateName)
            state.addTransition('factoryInterior')

        self.musicFile = 'phase_9/audio/bgm/SellbotHQ.ogg'
        self.cogHQExteriorModelPath = 'phase_9/models/cogHQ/SellbotHQExterior'
        self.cogHQLobbyModelPath = 'phase_9/models/cogHQ/SellbotHQLobby'
        self.factoryExteriorModelPath = 'phase_9/models/cogHQ/SellbotFactoryExterior'
        self.geom = None
        self.rain = None
        self.rainRender = None
        self.rainSound = None
        return


    def load(self, zoneId):
        CogHQLoader.CogHQLoader.load(self, zoneId)
        Toon.loadSellbotHQAnims()

    def startRain(self):     
        self.rain = BattleParticles.loadParticleFile('raindisk.ptf')
        self.rain.setPos(0, 0, 20)
        self.rainRender = self.geom.attachNewNode('rainRender')
        self.rainRender.setDepthWrite(0)
        self.rainRender.setBin('fixed', 1)
        self.rain.start(camera, self.rainRender)
        self.rainSound = base.loadSfx('phase_12/audio/sfx/CHQ_rain_ambient.ogg')
        base.playSfx(self.rainSound, looping=1, volume=0.1)
        return

    def stopRain(self):
        if self.rain:
            self.rain.cleanup()
            self.rainSound.stop()

    def unload(self):      
        del self.rain
        del self.rainRender
        del self.rainSound
        Toon.unloadBossbotHQAnims()
        CogHQLoader.CogHQLoader.unload(self)


    def unloadPlaceGeom(self):
        if self.geom:
            self.geom.removeNode()
            self.geom = None
        CogHQLoader.CogHQLoader.unloadPlaceGeom(self)

    def loadPlaceGeom(self, zoneId):
        self.notify.info('loadPlaceGeom: %s' % zoneId)
        zoneId = zoneId - zoneId % 100
        if zoneId == ToontownGlobals.SellbotHQ:
            self.geom = loader.loadModel(self.cogHQExteriorModelPath)
            dgLinkTunnel = self.geom.find('**/Tunnel1')
            dgLinkTunnel.setName('linktunnel_dg_5316_DNARoot')
            factoryLinkTunnel = self.geom.find('**/Tunnel2')
            factoryLinkTunnel.setName('linktunnel_sellhq_11200_DNARoot')
            cogSignModel = loader.loadModel('phase_4/models/props/sign_sellBotHeadHQ')
            cogSign = cogSignModel.find('**/sign_sellBotHeadHQ').copyTo(NodePath())
            cogSign.flattenStrong()
            cogSignModel.removeNode()
            cogSignSF = 23
            dgSign = cogSign.copyTo(dgLinkTunnel)
            dgSign.setPosHprScale(0.0, -291.5, 29, 180.0, 0.0, 0.0, cogSignSF, cogSignSF, cogSignSF * aspectSF)
            dgSign.node().setEffect(DecalEffect.make())
            dgText = DirectGui.OnscreenText(text=TTLocalizer.DaisyGardens[-1], font=ToontownGlobals.getSuitFont(), pos=(0, -0.3), scale=TTLocalizer.SCHQLdgText, mayChange=False, parent=dgSign)
            dgText.setDepthWrite(0)
            dgText.flattenStrong()
            factorySign = cogSign.copyTo(factoryLinkTunnel)
            factorySign.setPosHprScale(148.625, -155, 27, -90.0, 0.0, 0.0, cogSignSF, cogSignSF, cogSignSF * aspectSF)
            factorySign.node().setEffect(DecalEffect.make())
            factoryTypeText = DirectGui.OnscreenText(text=TTLocalizer.Sellbot, font=ToontownGlobals.getSuitFont(), pos=TTLocalizer.SellbotFactoryPosPart1, scale=TTLocalizer.SellbotFactoryScalePart1, mayChange=False, parent=factorySign)
            factoryTypeText.setDepthWrite(0)
            factoryTypeText.flattenStrong()
            factoryText = DirectGui.OnscreenText(text=TTLocalizer.Factory, font=ToontownGlobals.getSuitFont(), pos=TTLocalizer.SellbotFactoryPosPart2, scale=TTLocalizer.SellbotFactoryScalePart2, mayChange=False, parent=factorySign)
            factoryText.setDepthWrite(0)
            factoryText.flattenStrong()
            doors = self.geom.find('**/doors')
            door0 = doors.find('**/door_0')
            door1 = doors.find('**/door_1')
            door2 = doors.find('**/door_2')
            door3 = doors.find('**/door_3')
            for door in [door0, door1, door2, door3]:
                doorFrame = door.find('**/doorDoubleFlat/+GeomNode')
                door.find('**/doorFrameHoleLeft').wrtReparentTo(doorFrame)
                door.find('**/doorFrameHoleRight').wrtReparentTo(doorFrame)
                doorTrigger = door.find('**/door_trigger*')
                doorTrigger.setY(doorTrigger.getY() - 1.5)
                doorFrame.node().setEffect(DecalEffect.make())
                doorFrame.flattenStrong()
                door.flattenMedium()
            cogSign.removeNode()
            self.geom.flattenMedium()
            self.botcam1 = Actor("phase_9/models/char/BotCam-zero.bam",{"botcamneutral":"phase_9/models/char/BotCam-neutral.bam"})
            self.botcam1.reparentTo(self.geom)
            self.botcam1.setPos(-0.01,-39.3,24)
            self.botcam1.loop('botcamneutral')
        elif zoneId == ToontownGlobals.SellbotFactoryExt:
            self.geom = loader.loadModel(self.factoryExteriorModelPath)
            factoryLinkTunnel = self.geom.find('**/tunnel_group2')
            factoryLinkTunnel.setName('linktunnel_sellhq_11000_DNARoot')
            factoryLinkTunnel.find('**/tunnel_sphere').setName('tunnel_trigger')
            cogSignModel = loader.loadModel('phase_4/models/props/sign_sellBotHeadHQ')
            cogSign = cogSignModel.find('**/sign_sellBotHeadHQ').copyTo(NodePath())
            cogSign.flattenStrong()
            cogSignModel.removeNode()
            cogSignSF = 23
            elevatorSignSF = 15
            hqSign = cogSign.copyTo(factoryLinkTunnel)
            hqSign.setPosHprScale(0.0, -353, 27.5, -180.0, 0.0, 0.0, cogSignSF, cogSignSF, cogSignSF * aspectSF)
            hqSign.node().setEffect(DecalEffect.make())
            hqTypeText = DirectGui.OnscreenText(text=TTLocalizer.Sellbot, font=ToontownGlobals.getSuitFont(), pos=(0, -0.25), scale=0.075, mayChange=False, parent=hqSign)
            hqTypeText.setDepthWrite(0)
            hqTypeText.flattenStrong()
            hqText = DirectGui.OnscreenText(text=TTLocalizer.Headquarters, font=ToontownGlobals.getSuitFont(), pos=(0, -0.34), scale=0.1, mayChange=False, parent=hqSign)
            hqText.setDepthWrite(0)
            hqText.flattenStrong()
            frontDoor = self.geom.find('**/doorway1')
            fdSign = cogSign.copyTo(frontDoor)
            fdSign.setPosHprScale(62.74, -87.99, 17.26, 2.72, 0.0, 0.0, elevatorSignSF, elevatorSignSF, elevatorSignSF * aspectSF)
            fdSign.node().setEffect(DecalEffect.make())
            fdTypeText = DirectGui.OnscreenText(text=TTLocalizer.Factory, font=ToontownGlobals.getSuitFont(), pos=(0, -0.25), scale=TTLocalizer.SCHQLfdTypeText, mayChange=False, parent=fdSign)
            fdTypeText.setDepthWrite(0)
            fdTypeText.flattenStrong()
            fdText = DirectGui.OnscreenText(text=TTLocalizer.SellbotFrontEntrance, font=ToontownGlobals.getSuitFont(), pos=(0, -0.34), scale=TTLocalizer.SCHQLdgText, mayChange=False, parent=fdSign)
            fdText.setDepthWrite(0)
            fdText.flattenStrong()
            sideDoor = self.geom.find('**/doorway2')
            sdSign = cogSign.copyTo(sideDoor)
            sdSign.setPosHprScale(-164.78, 26.28, 17.25, -89.89, 0.0, 0.0, elevatorSignSF, elevatorSignSF, elevatorSignSF * aspectSF)
            sdSign.node().setEffect(DecalEffect.make())
            sdTypeText = DirectGui.OnscreenText(text=TTLocalizer.Factory, font=ToontownGlobals.getSuitFont(), pos=(0, -0.25), scale=0.075, mayChange=False, parent=sdSign)
            sdTypeText.setDepthWrite(0)
            sdTypeText.flattenStrong()
            sdText = DirectGui.OnscreenText(text=TTLocalizer.SellbotSideEntrance, font=ToontownGlobals.getSuitFont(), pos=(0, -0.34), scale=0.1, mayChange=False, parent=sdSign)
            sdText.setDepthWrite(0)
            sdText.flattenStrong()
            hardDoor = self.geom.find('**/doorway1')
            hdSign = cogSign.copyTo(hardDoor)
            hdSign.setPosHprScale(17.765, -43.83, 17.26, -88.72, 0.0, 0.0, elevatorSignSF, elevatorSignSF, elevatorSignSF * aspectSF)
            hdSign.node().setEffect(DecalEffect.make())
            hdTypeText = DirectGui.OnscreenText(text=TTLocalizer.Factory, font=ToontownGlobals.getSuitFont(), pos=(0, -0.25), scale=TTLocalizer.SCHQLfdTypeText, mayChange=False, parent=hdSign)
            hdTypeText.setDepthWrite(0)
            hdTypeText.flattenStrong()
            hdText = DirectGui.OnscreenText(text=TTLocalizer.HardSellbotEntrance, font=ToontownGlobals.getSuitFont(), pos=(0, -0.34), scale=TTLocalizer.SCHQLdgText, mayChange=False, parent=hdSign)
            hdText.setDepthWrite(0)
            hdText.flattenStrong()
            unfairDoor = self.geom.find('**/doorway1')
            udSign = cogSign.copyTo(unfairDoor)
            udSign.setPosHprScale(-104.03, 26.43, 17.25, 91.89, 0.0, 0.0, elevatorSignSF, elevatorSignSF, elevatorSignSF * aspectSF)
            udSign.node().setEffect(DecalEffect.make())
            udTypeText = DirectGui.OnscreenText(text=TTLocalizer.Factory, font=ToontownGlobals.getSuitFont(), pos=(0, -0.25), scale=0.075, mayChange=False, parent=udSign)
            udTypeText.setDepthWrite(0)
            udTypeText.flattenStrong()
            udText = DirectGui.OnscreenText(text=TTLocalizer.UnfairSellbotEntrance, font=ToontownGlobals.getSuitFont(), pos=(0, -0.34), scale=0.1, mayChange=False, parent=udSign)
            udText.setDepthWrite(0)
            udText.flattenStrong()
            cogSign.removeNode()
            self.geom.flattenMedium()
        elif zoneId == ToontownGlobals.SellbotLobby:
            if base.config.GetBool('want-qa-regression', 0):
                self.notify.info('QA-REGRESSION: COGHQ: Visit SellbotLobby')
            self.geom = loader.loadModel(self.cogHQLobbyModelPath)
            front = self.geom.find('**/frontWall')
            front.node().setEffect(DecalEffect.make())
            door = self.geom.find('**/door_0')
            parent = door.getParent()
            door.wrtReparentTo(front)
            doorFrame = door.find('**/doorDoubleFlat/+GeomNode')
            door.find('**/doorFrameHoleLeft').wrtReparentTo(doorFrame)
            door.find('**/doorFrameHoleRight').wrtReparentTo(doorFrame)
            doorFrame.node().setEffect(DecalEffect.make())
            door.find('**/leftDoor').wrtReparentTo(parent)
            door.find('**/rightDoor').wrtReparentTo(parent)
            self.geom.flattenStrong()
        else:
            self.notify.warning('loadPlaceGeom: unclassified zone %s' % zoneId)
        CogHQLoader.CogHQLoader.loadPlaceGeom(self, zoneId)

    def unload(self):
        CogHQLoader.CogHQLoader.unload(self)
        Toon.unloadSellbotHQAnims()

    def enterFactoryExterior(self, requestStatus):
        self.placeClass = FactoryExterior.FactoryExterior
        self.enterPlace(requestStatus)
        self.hood.spawnTitleText(requestStatus['zoneId'])
        self.startRain()

    def exitFactoryExterior(self):
        self.stopRain()
        taskMgr.remove('titleText')
        self.hood.hideTitleText()
        self.exitPlace()
        self.placeClass = None
        return

    def enterMegaCorpInterior(self, requestStatus):
        self.placeClass = MegaCorpInterior.MegaCorpInterior
        self.enterPlace(requestStatus)

    def exitMegaCorpInterior(self):
        self.exitPlace()
        self.placeClass = None

    def enterHardFactoryInterior(self, requestStatus):
        self.placeClass = HardFactoryInterior.HardFactoryInterior
        self.enterPlace(requestStatus)

    def exitHardFactoryInterior(self):
        self.exitPlace()
        self.placeClass = None

    def enterUnfairFactoryInterior(self, requestStatus):
        self.placeClass = UnfairFactoryInterior.UnfairFactoryInterior
        self.enterPlace(requestStatus)

    def exitUnfairFactoryInterior(self):
        self.exitPlace()
        self.placeClass = None

    def enterCogHQExterior(self, requestStatus):
        self.placeClass = self.getExteriorPlaceClass()
        self.enterPlace(requestStatus)
        self.startRain()

    def exitCogHQExterior(self):
        self.stopRain()
        self.exitPlace()
        self.placeClass = None
        return

    def enterFactoryInterior(self, requestStatus):
        self.placeClass = FactoryInterior.FactoryInterior
        self.enterPlace(requestStatus)

    def exitFactoryInterior(self):
        self.exitPlace()
        self.placeClass = None

    def getExteriorPlaceClass(self):
        return SellbotHQExterior.SellbotHQExterior

    def getBossPlaceClass(self):
        return SellbotHQBossBattle.SellbotHQBossBattle
