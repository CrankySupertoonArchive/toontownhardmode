from toontown.safezone import SafeZoneLoader
from toontown.safezone import CZPlayground
from direct.gui import DirectGui
from panda3d.core import *
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from direct.distributed.ClockDelta import *
from direct.interval.IntervalGlobal import *
import random
from direct.directnotify import DirectNotifyGlobal
from pandac.PandaModules import NodePath
from toontown.toon import NPCToons, Toon
from toontown.pets import Pet
from direct.task.Task import Task
from direct.actor.Actor import Actor

class CZSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playgroundClass = CZPlayground.CZPlayground
        self.musicFile = 'phase_14/audio/bgm/CZ_nbrhood.ogg'
        self.activityMusicFile = 'phase_14/audio/bgm/CZ_SZ_activity.ogg'
        self.dnaFile = 'phase_14/dna/construction_zone_sz.pdna'
        self.safeZoneStorageDNAFile = 'phase_14/dna/storage_CZ_sz.pdna'


    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)
        top = self.geom.find('**/linktunnel_cz_14000_DNARoot')
        sign = top.find('**/Sign_5')
        sign.node().setEffect(DecalEffect.make())
        locator = top.find('**/sign_origin')
        signText = DirectGui.OnscreenText(text=TextEncoder.upper(TTLocalizer.GovernbotHQ[-1]), font=ToontownGlobals.getSuitFont(), scale=TTLocalizer.GZSZLsignText, fg=(0, 0, 0, 1), mayChange=False, parent=sign)
        signText.setPosHpr(locator, 0, 0, -0.3, 0, 0, 0)
        signText.setDepthWrite(0)
        self.underwaterSound = base.loadSfx('phase_4/audio/sfx/AV_ambient_water.ogg')
        self.swimSound = base.loadSfx('phase_4/audio/sfx/AV_swim_single_stroke.ogg')
        self.submergeSound = base.loadSfx('phase_5.5/audio/sfx/AV_jump_in_water.ogg')

        water = self.geom.find('**/water')

        self.flippy = NPCToons.createLocalNPC(2001)
        self.flippy.loop('neutral')
        self.flippy.setPos(-145.04, -51.44, 2.56)
        self.flippy.setH(40)
        self.flippySpeech = self.flippy.createTalkSequence(TTLocalizer.FlippyChatter, 15)
        self.flippySpeech.loop(0) 
        self.flippy.reparentTo(self.geom)
        self.flippy.initializeBodyCollisions('toon-flippy')
        self.flippy.addActive()
        self.fluffy = Pet.Pet()
        self.fluffy.setDNA(ToontownGlobals.NPCDoodleDNA['Fluffy'])
        self.fluffySequence = Sequence(Func(self.fluffy.loop, 'neutralHappy'), Wait(4.0), ActorInterval(self.fluffy, 'toDig'), Func(self.fluffy.loop, 'dig'), Wait(1.5), ActorInterval(self.fluffy, 'fromDig'), Func(self.fluffy.loop, 'neutralHappy'), Wait(4.0), ActorInterval(self.fluffy, 'jump'), Func(self.fluffy.loop, 'neutralHappy'), Wait(4.0), ActorInterval(self.fluffy, 'dance'), Func(self.fluffy.loop, 'neutralHappy'), Wait(5.0), ActorInterval(self.fluffy, 'backflip'), Func(self.fluffy.loop, 'neutralHappy'))
        self.fluffySequence.loop()
        self.fluffy.loop('dance')
        self.fluffy.setPos(-153.7, 85.4, 2.56)
        self.fluffy.setH(-137)
        self.fluffy.setName(TTLocalizer.NPCDoodleNames['Fluffy'])
        self.fluffy.reparentTo(self.geom)
        self.fluffy.initializeBodyCollisions('pet-fluffy')
        self.fluffy.setPickable(0)
        self.fluffy.addActive()
        self.fluff = Pet.Pet()
        self.fluff.setDNA(ToontownGlobals.NPCDoodleDNA1['Fluff'])
        self.fluffSequence = Sequence(Func(self.fluff.loop, 'neutralHappy'), Wait(3.0), ActorInterval(self.fluff, 'toDig'), Func(self.fluff.loop, 'dig'), Wait(1.0), ActorInterval(self.fluff, 'fromDig'), Func(self.fluff.loop, 'neutralHappy'), Wait(3.0), ActorInterval(self.fluff, 'jump'), Func(self.fluff.loop, 'neutralHappy'), Wait(3.0), ActorInterval(self.fluff, 'dance'), Func(self.fluff.loop, 'neutralHappy'), Wait(4.0), ActorInterval(self.fluff, 'backflip'), Func(self.fluff.loop, 'neutralHappy'))
        self.fluffSequence.loop()
        self.fluff.loop('dance')
        self.fluff.setPos(-169.1, 66.4, 2.56)
        self.fluff.setH(-157)
        self.fluff.setName(TTLocalizer.NPCDoodleNames1['Fluff'])
        self.fluff.reparentTo(self.geom)
        self.fluff.initializeBodyCollisions('pet-fluff')
        self.fluff.setPickable(0)
        self.fluff.addActive()

        self.laffy = Pet.Pet()
        self.laffy.setDNA(ToontownGlobals.NPCDoodleDNA2['Laffy'])
        self.laffySequence = Sequence(Func(self.laffy.loop, 'neutralHappy'), Wait(4.0), ActorInterval(self.laffy, 'toDig'), Func(self.laffy.loop, 'dig'), Wait(1.5), ActorInterval(self.laffy, 'fromDig'), Func(self.laffy.loop, 'neutralHappy'), Wait(4.0), ActorInterval(self.laffy, 'jump'), Func(self.laffy.loop, 'neutralHappy'), Wait(4.0), ActorInterval(self.laffy, 'dance'), Func(self.laffy.loop, 'neutralHappy'), Wait(5.0), ActorInterval(self.laffy, 'backflip'), Func(self.laffy.loop, 'neutralHappy'))
        self.laffySequence.loop()
        self.laffy.loop('dance')
        self.laffy.setPos(84.56, 17.84, 88.57)
        self.laffy.setH(-137)
        self.laffy.setName(TTLocalizer.NPCDoodleNames2['Laffy'])
        self.laffy.reparentTo(self.geom)
        self.laffy.initializeBodyCollisions('pet-laffy')
        self.laffy.setPickable(0)
        self.laffy.addActive()
        self.taffy = Pet.Pet()
        self.taffy.setDNA(ToontownGlobals.NPCDoodleDNA3['Taffy'])
        self.taffySequence = Sequence(Func(self.taffy.loop, 'neutralHappy'), Wait(3.0), ActorInterval(self.taffy, 'toDig'), Func(self.taffy.loop, 'dig'), Wait(1.0), ActorInterval(self.taffy, 'fromDig'), Func(self.taffy.loop, 'neutralHappy'), Wait(3.0), ActorInterval(self.taffy, 'jump'), Func(self.taffy.loop, 'neutralHappy'), Wait(3.0), ActorInterval(self.taffy, 'dance'), Func(self.taffy.loop, 'neutralHappy'), Wait(4.0), ActorInterval(self.taffy, 'backflip'), Func(self.taffy.loop, 'neutralHappy'))
        self.taffySequence.loop()
        self.taffy.loop('dance')
        self.taffy.setPos(123.047, 20.36, 88.57)
        self.taffy.setH(-157)
        self.taffy.setName(TTLocalizer.NPCDoodleNames3['Taffy'])
        self.taffy.reparentTo(self.geom)
        self.taffy.initializeBodyCollisions('pet-taffy')
        self.taffy.setPickable(0)
        self.taffy.addActive()
        self.activeSequences = []
        self.restockSfx = None
        return

    def delete(self):
        for sequence in self.activeSequences:
            del sequence

        del self.activeSequences
        del self.flippySequence
        del self.fluffySequence
        self.flippy.delete()
        self.fluffy.delete()
        self.fluff.delete()
        self.laffy.delete()
        self.taffy.delete()
       
    def unload(self):
        SafeZoneLoader.SafeZoneLoader.unload(self)
        del self.underwaterSound
        del self.swimSound
        del self.submergeSound
       
        del self.flippySpeech
        del self.flippy