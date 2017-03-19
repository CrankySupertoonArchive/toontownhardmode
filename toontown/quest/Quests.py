from direct.directnotify import DirectNotifyGlobal
from direct.showbase import PythonUtil
from toontown.toonbase import ToontownBattleGlobals
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.battle import SuitBattleGlobals
from toontown.coghq import CogDisguiseGlobals
from toontown.toon import NPCToons
from toontown.hood import ZoneUtil
from otp.otpbase import OTPGlobals
import random
import copy
import string
import time
import types
import random

notify = DirectNotifyGlobal.directNotify.newCategory('Quests')
ItemDict = TTLocalizer.QuestsItemDict
CompleteString = TTLocalizer.QuestsCompleteString
NotChosenString = TTLocalizer.QuestsNotChosenString
DefaultGreeting = TTLocalizer.QuestsDefaultGreeting
DefaultIncomplete = TTLocalizer.QuestsDefaultIncomplete
DefaultIncompleteProgress = TTLocalizer.QuestsDefaultIncompleteProgress
DefaultIncompleteWrongNPC = TTLocalizer.QuestsDefaultIncompleteWrongNPC
DefaultComplete = TTLocalizer.QuestsDefaultComplete
DefaultLeaving = TTLocalizer.QuestsDefaultLeaving
DefaultReject = TTLocalizer.QuestsDefaultReject
DefaultTierNotDone = TTLocalizer.QuestsDefaultTierNotDone
DefaultQuest = TTLocalizer.QuestsDefaultQuest
DefaultVisitQuestDialog = TTLocalizer.QuestsDefaultVisitQuestDialog
GREETING = 0
QUEST = 1
INCOMPLETE = 2
INCOMPLETE_PROGRESS = 3
INCOMPLETE_WRONG_NPC = 4
COMPLETE = 5
LEAVING = 6
Any = 1
OBSOLETE = 'OBSOLETE'
Start = 1
Cont = 0
Anywhere = 1
NA = 2
Same = 3
AnyFish = 4
AnyCashbotSuitPart = 5
AnyLawbotSuitPart = 6
AnyBossbotSuitPart = 7
AnyGovernbotSuitPart = 8
AnyEurekabotSuitPart = 9
AnyBuildbotSuitPart = 10
AnyViralbotSuitPart = 11
ToonTailor = 999
ToonHQ = 1000
InVP = 0
InFO = 1
WithCheat = 2
QuestDictTierIndex = 0
QuestDictStartIndex = 1
QuestDictDescIndex = 2
QuestDictFromNpcIndex = 3
QuestDictToNpcIndex = 4
QuestDictRewardIndex = 5
QuestDictNextQuestIndex = 6
QuestDictDialogIndex = 7
VeryEasy = 100
Easy = 80
Medium = 60
Hard = 30
VeryHard = 25
Fun = 15
TT_TIER = 0
DD_TIER = 4
DG_TIER = 7
MM_TIER = 8
BR_TIER = 11
DL_TIER = 14
LAWBOT_HQ_TIER = 18
BOSSBOT_HQ_TIER = 32
GOVERNBOT_HQ_TIER = 40
EUREKABOT_HQ_TIER = 41
BUILDBOT_HQ_TIER = 42
VIRALBOT_HQ_TIER = 43
PRE_ELDER_TIER = 49
ELDER_TIER = 50
LOOPING_FINAL_TIER = ELDER_TIER
VISIT_QUEST_ID = 1000
TROLLEY_QUEST_ID = 110
FIRST_COG_QUEST_ID = 145
FRIEND_QUEST_ID = 150
PHONE_QUEST_ID = 175
from toontown.toonbase.ToontownGlobals import FT_FullSuit, FT_Leg, FT_Arm, FT_Torso
QuestRandGen = random.Random()

def seedRandomGen(npcId, avId, tier, rewardHistory):
    QuestRandGen.seed(npcId * 100 + avId + tier + len(rewardHistory))


def seededRandomChoice(seq):
    return QuestRandGen.choice(seq)


def getCompleteStatusWithNpc(questComplete, toNpcId, npc):
    if questComplete:
        if npc:
            if npcMatches(toNpcId, npc):
                return COMPLETE
            else:
                return INCOMPLETE_WRONG_NPC
        else:
            return COMPLETE
    elif npc:
        if npcMatches(toNpcId, npc):
            return INCOMPLETE_PROGRESS
        else:
            return INCOMPLETE
    else:
        return INCOMPLETE


def npcMatches(toNpcId, npc):
    return toNpcId == npc.getNpcId() or toNpcId == Any or toNpcId == ToonHQ and npc.getHq() or toNpcId == ToonTailor and npc.getTailor()


def calcRecoverChance(numberNotDone, chance, cap = 1):
    avgNum2Kill = 1.0 / (chance / 100.0)
    diff = float(numberNotDone - avgNum2Kill * 0.5)
    luck = 1.0 + abs(diff / (avgNum2Kill * 0.5))
    chance *= luck
    return chance


def simulateRecoveryVar(numNeeded, baseChance, list = 0, cap = 1):
    numHave = 0
    numTries = 0
    greatestFailChain = 0
    currentFail = 0
    capHits = 0
    attemptList = {}
    while numHave < numNeeded:
        numTries += 1
        chance = calcRecoverChance(currentFail, baseChance, cap)
        test = random.random() * 100
        if chance == 1000:
            capHits += 1
        if test < chance:
            numHave += 1
            if currentFail > greatestFailChain:
                greatestFailChain = currentFail
            if attemptList.get(currentFail):
                attemptList[currentFail] += 1
            else:
                attemptList[currentFail] = 1
            currentFail = 0
        else:
            currentFail += 1

    print 'Test results: %s tries, %s longest failure chain, %s cap hits' % (numTries, greatestFailChain, capHits)
    if list:
        print 'failures for each succes %s' % attemptList


def simulateRecoveryFix(numNeeded, baseChance, list = 0):
    numHave = 0
    numTries = 0
    greatestFailChain = 0
    currentFail = 0
    attemptList = {}
    while numHave < numNeeded:
        numTries += 1
        chance = baseChance
        test = random.random() * 100
        if test < chance:
            numHave += 1
            if currentFail > greatestFailChain:
                greatestFailChain = currentFail
            if attemptList.get(currentFail):
                attemptList[currentFail] += 1
            else:
                attemptList[currentFail] = 1
            currentFail = 0
        else:
            currentFail += 1

    print 'Test results: %s tries, %s longest failure chain' % (numTries, greatestFailChain)
    if list:
        print 'failures for each success %s' % attemptList


class Quest:
    _cogTracks = [Any,
     'c',
     'l',
     'm',
     's',
     'v',
     'e',
     'b',
     'z']
    _factoryTypes = [Any,
     FT_FullSuit,
     FT_Leg,
     FT_Arm,
     FT_Torso]

    def check(self, cond, msg):
        pass

    def checkLocation(self, location):
        locations = [Anywhere] + TTLocalizer.GlobalStreetNames.keys()
        self.check(location in locations, 'invalid location: %s' % location)

    def checkNumCogs(self, num):
        self.check(1, 'invalid number of cogs: %s' % num)

    def checkCogType(self, type):
        types = [Any] + SuitBattleGlobals.SuitAttributes.keys()
        self.check(type in types, 'invalid cog type: %s' % type)

    def checkCogTrack(self, track):
        self.check(track in self._cogTracks, 'invalid cog track: %s' % track)

    def checkCogLevel(self, level):
        self.check(level >= 1 and level <= 15, 'invalid cog level: %s' % level)

    def checkNumSkelecogs(self, num):
        self.check(1, 'invalid number of cogs: %s' % num)

    def checkSkelecogTrack(self, track):
        self.check(track in self._cogTracks, 'invalid cog track: %s' % track)

    def checkSkelecogLevel(self, level):
        self.check(level >= 1 and level <= 15, 'invalid cog level: %s' % level)

    def checkNumSkeleRevives(self, num):
        self.check(1, 'invalid number of cogs: %s' % num)

    def checkNumForemen(self, num):
        self.check(num > 0, 'invalid number of foremen: %s' % num)

    def checkNumBosses(self, num):
        self.check(num > 0, 'invalid number of bosses: %s' % num)

    def checkNumSupervisors(self, num):
        self.check(num > 0, 'invalid number of supervisors: %s' % num)

    def checkNumBuildings(self, num):
        self.check(1, 'invalid num buildings: %s' % num)

    def checkBuildingTrack(self, track):
        self.check(track in self._cogTracks, 'invalid building track: %s' % track)

    def checkBuildingFloors(self, floors):
        self.check(floors >= 1 and floors <= 7, 'invalid num floors: %s' % floors)

    def checkBuildingType(self, cogdo):
        self.check(cogdo != 0 and cogdo != 1, 'invalid cogdo value: %s' % cogdo)

    def checkNumFactories(self, num):
        self.check(1, 'invalid num factories: %s' % num)

    def checkFactoryType(self, type):
        self.check(type in self._factoryTypes, 'invalid factory type: %s' % type)

    def checkNumMints(self, num):
        self.check(1, 'invalid num mints: %s' % num)

    def checkNumCogParts(self, num):
        self.check(1, 'invalid num cog parts: %s' % num)

    def checkNumGags(self, num):
        self.check(1, 'invalid num gags: %s' % num)

    def checkGagTrack(self, track):
        self.check(track >= ToontownBattleGlobals.MIN_TRACK_INDEX and track <= ToontownBattleGlobals.MAX_TRACK_INDEX, 'invalid gag track: %s' % track)

    def checkGagItem(self, item):
        self.check(item >= ToontownBattleGlobals.MIN_LEVEL_INDEX and item <= ToontownBattleGlobals.MAX_LEVEL_INDEX, 'invalid gag item: %s' % item)

    def checkDeliveryItem(self, item):
        self.check(item in ItemDict, 'invalid delivery item: %s' % item)

    def checkNumItems(self, num):
        self.check(1, 'invalid num items: %s' % num)

    def checkRecoveryItem(self, item):
        self.check(item in ItemDict, 'invalid recovery item: %s' % item)

    def checkPercentChance(self, chance):
        self.check(chance > 0 and chance <= 100, 'invalid percent chance: %s' % chance)

    def checkRecoveryItemHolderAndType(self, holder, holderType = 'type'):
        holderTypes = ['type', 'level', 'track']
        self.check(holderType in holderTypes, 'invalid recovery item holderType: %s' % holderType)
        if holderType == 'type':
            holders = [Any, AnyFish] + SuitBattleGlobals.SuitAttributes.keys()
            self.check(holder in holders, 'invalid recovery item holder: %s for holderType: %s' % (holder, holderType))
        elif holderType == 'level':
            pass
        elif holderType == 'track':
            self.check(holder in self._cogTracks, 'invalid recovery item holder: %s for holderType: %s' % (holder, holderType))

    def checkTrackChoice(self, option):
        self.check(option >= ToontownBattleGlobals.MIN_TRACK_INDEX and option <= ToontownBattleGlobals.MAX_TRACK_INDEX, 'invalid track option: %s' % option)

    def checkNumFriends(self, num):
        self.check(1, 'invalid number of friends: %s' % num)

    def checkNumMinigames(self, num):
        self.check(1, 'invalid number of minigames: %s' % num)

    def filterFunc(avatar):
        return 1

    filterFunc = staticmethod(filterFunc)

    def __init__(self, id, quest):
        self.id = id
        self.quest = quest

    def getId(self):
        return self.id

    def getType(self):
        return self.__class__

    def getObjectiveStrings(self):
        return ['']

    def getString(self):
        return self.getObjectiveStrings()[0]

    def getRewardString(self, progressString):
        return self.getString() + ' : ' + progressString

    def getChooseString(self):
        return self.getString()

    def getPosterString(self):
        return self.getString()

    def getHeadlineString(self):
        return self.getString()

    def getDefaultQuestDialog(self):
        return self.getString() + TTLocalizer.Period

    def getNumQuestItems(self):
        return -1

    def addArticle(self, num, oString):
        if len(oString) == 0:
            return oString
        if num == 1:
            return oString
        else:
            return '%d %s' % (num, oString)

    def __repr__(self):
        return 'Quest type: %s id: %s params: %s' % (self.__class__.__name__, self.id, self.quest[0:])

    def doesCogCount(self, avId, cogDict, zoneId):
        return 0

    def doesFactoryCount(self, avId, location):
        return 0

    def doesMintCount(self, avId, location):
        return 0

    def doesCogPartCount(self, avId, location):
        return 0

    def getCompletionStatus(self, av, questDesc, npc = None):
        notify.error('Pure virtual - please override me')
        return None


class LocationBasedQuest(Quest):
    def __init__(self, id, quest):
        Quest.__init__(self, id, quest)
        self.checkLocation(self.quest[0])

    def getLocation(self):
        return self.quest[0]

    def getLocationName(self):
        loc = self.getLocation()
        if loc == Anywhere:
            locName = ''
        elif loc in ToontownGlobals.hoodNameMap:
            locName = TTLocalizer.QuestInLocationString % {'inPhrase': ToontownGlobals.hoodNameMap[loc][1],
             'location': ToontownGlobals.hoodNameMap[loc][-1] + TTLocalizer.QuestsLocationArticle}
        elif loc in ToontownGlobals.StreetBranchZones:
            locName = TTLocalizer.QuestInLocationString % {'inPhrase': ToontownGlobals.StreetNames[loc][1],
             'location': ToontownGlobals.StreetNames[loc][-1] + TTLocalizer.QuestsLocationArticle}
        return locName

    def isLocationMatch(self, zoneId):
        loc = self.getLocation()
        if loc is Anywhere:
            return 1
        if ZoneUtil.isPlayground(loc):
            if loc == ZoneUtil.getCanonicalHoodId(zoneId):
                return 1
            else:
                return 0
        elif loc == ZoneUtil.getCanonicalBranchZone(zoneId):
            return 1
        elif loc == zoneId:
            return 1
        else:
            return 0

    def getChooseString(self):
        return TTLocalizer.QuestsLocationString % {'string': self.getString(),
         'location': self.getLocationName()}

    def getPosterString(self):
        return TTLocalizer.QuestsLocationString % {'string': self.getString(),
         'location': self.getLocationName()}

    def getDefaultQuestDialog(self):
        return (TTLocalizer.QuestsLocationString + TTLocalizer.Period) % {'string': self.getString(),
         'location': self.getLocationName()}

class CogQuest(LocationBasedQuest):
    def __init__(self, id, quest):
        LocationBasedQuest.__init__(self, id, quest)
        if self.__class__ == CogQuest:
            self.checkNumCogs(self.quest[1])
            self.checkCogType(self.quest[2])

    def getCogType(self):
        return self.quest[2]

    def getNumQuestItems(self):
        return self.getNumCogs()

    def getNumCogs(self):
        return self.quest[1]

    def getCompletionStatus(self, av, questDesc, npc = None):
        questId, fromNpcId, toNpcId, rewardId, toonProgress = questDesc
        questComplete = toonProgress >= self.getNumCogs()
        return getCompleteStatusWithNpc(questComplete, toNpcId, npc)

    def getProgressString(self, avatar, questDesc):
        if self.getCompletionStatus(avatar, questDesc) == COMPLETE:
            return CompleteString
        elif self.getNumCogs() == 1:
            return ''
        else:
            return TTLocalizer.QuestsCogQuestProgress % {'progress': questDesc[4],
             'numCogs': self.getNumCogs()}

    def getCogNameString(self):
        numCogs = self.getNumCogs()
        cogType = self.getCogType()
        if numCogs == 1:
            if cogType == Any:
                return TTLocalizer.Cog
            else:
                return SuitBattleGlobals.SuitAttributes[cogType]['singularname']
        elif cogType == Any:
            return TTLocalizer.Cogs
        else:
            return SuitBattleGlobals.SuitAttributes[cogType]['pluralname']

    def getObjectiveStrings(self):
        cogName = self.getCogNameString()
        numCogs = self.getNumCogs()
        if numCogs == 1:
            text = cogName
        else:
            text = TTLocalizer.QuestsCogQuestDefeatDesc % {'numCogs': numCogs,
             'cogName': cogName}
        return (text,)

    def getString(self):
        return TTLocalizer.QuestsCogQuestDefeat % self.getObjectiveStrings()[0]

    def getSCStrings(self, toNpcId, progress):
        if progress >= self.getNumCogs():
            return getFinishToonTaskSCStrings(toNpcId)
        cogName = self.getCogNameString()
        numCogs = self.getNumCogs()
        if numCogs == 1:
            text = TTLocalizer.QuestsCogQuestSCStringS
        else:
            text = TTLocalizer.QuestsCogQuestSCStringP
        cogLoc = self.getLocationName()
        return text % {'cogName': cogName,
         'cogLoc': cogLoc}

    def getHeadlineString(self):
        return TTLocalizer.QuestsCogQuestHeadline

    def doesCogCount(self, avId, cogDict, zoneId):
        questCogType = self.getCogType()
        return (questCogType is Any or questCogType is cogDict['type']) and avId in cogDict['activeToons'] and self.isLocationMatch(zoneId)


class CogTrackQuest(CogQuest):
    trackCodes = ['c',
     'l',
     'm',
     's',
     'v',
     'e',
     'b',
     'z']
    trackNamesS = [TTLocalizer.BossbotS,
     TTLocalizer.LawbotS,
     TTLocalizer.CashbotS,
     TTLocalizer.SellbotS,
     TTLocalizer.GovernbotS,
     TTLocalizer.EurekabotS,
     TTLocalizer.BuildbotS,
     TTLocalizer.ViralbotS]
    trackNamesP = [TTLocalizer.BossbotP,
     TTLocalizer.LawbotP,
     TTLocalizer.CashbotP,
     TTLocalizer.SellbotP,
     TTLocalizer.GovernbotP,
     TTLocalizer.EurekabotP,
     TTLocalizer.BuildbotP,
     TTLocalizer.ViralbotP]

    def __init__(self, id, quest):
        CogQuest.__init__(self, id, quest)
        if self.__class__ == CogTrackQuest:
            self.checkNumCogs(self.quest[1])
            self.checkCogTrack(self.quest[2])

    def getCogTrack(self):
        return self.quest[2]

    def getProgressString(self, avatar, questDesc):
        if self.getCompletionStatus(avatar, questDesc) == COMPLETE:
            return CompleteString
        elif self.getNumCogs() == 1:
            return ''
        else:
            return TTLocalizer.QuestsCogTrackQuestProgress % {'progress': questDesc[4],
             'numCogs': self.getNumCogs()}

    def getObjectiveStrings(self):
        numCogs = self.getNumCogs()
        track = self.trackCodes.index(self.getCogTrack())
        if numCogs == 1:
            text = self.trackNamesS[track]
        else:
            text = TTLocalizer.QuestsCogTrackDefeatDesc % {'numCogs': numCogs,
             'trackName': self.trackNamesP[track]}
        return (text,)

    def getString(self):
        return TTLocalizer.QuestsCogTrackQuestDefeat % self.getObjectiveStrings()[0]

    def getSCStrings(self, toNpcId, progress):
        if progress >= self.getNumCogs():
            return getFinishToonTaskSCStrings(toNpcId)
        numCogs = self.getNumCogs()
        track = self.trackCodes.index(self.getCogTrack())
        if numCogs == 1:
            cogText = self.trackNamesS[track]
            text = TTLocalizer.QuestsCogTrackQuestSCStringS
        else:
            cogText = self.trackNamesP[track]
            text = TTLocalizer.QuestsCogTrackQuestSCStringP
        cogLocName = self.getLocationName()
        return text % {'cogText': cogText,
         'cogLoc': cogLocName}

    def getHeadlineString(self):
        return TTLocalizer.QuestsCogTrackQuestHeadline

    def doesCogCount(self, avId, cogDict, zoneId):
        questCogTrack = self.getCogTrack()
        return questCogTrack == cogDict['track'] and avId in cogDict['activeToons'] and self.isLocationMatch(zoneId)


class CogLevelQuest(CogQuest):
    def __init__(self, id, quest):
        CogQuest.__init__(self, id, quest)
        self.checkNumCogs(self.quest[1])
        self.checkCogLevel(self.quest[2])

    def getCogType(self):
        return Any

    def getCogLevel(self):
        return self.quest[2]

    def getProgressString(self, avatar, questDesc):
        if self.getCompletionStatus(avatar, questDesc) == COMPLETE:
            return CompleteString
        elif self.getNumCogs() == 1:
            return ''
        else:
            return TTLocalizer.QuestsCogLevelQuestProgress % {'progress': questDesc[4],
             'numCogs': self.getNumCogs()}

    def getObjectiveStrings(self):
        count = self.getNumCogs()
        level = self.getCogLevel()
        name = self.getCogNameString()
        if count == 1:
            text = TTLocalizer.QuestsCogLevelQuestDesc
        else:
            text = TTLocalizer.QuestsCogLevelQuestDescC
        return (text % {'count': count,
          'level': level,
          'name': name},)

    def getString(self):
        return TTLocalizer.QuestsCogLevelQuestDefeat % self.getObjectiveStrings()[0]

    def getSCStrings(self, toNpcId, progress):
        if progress >= self.getNumCogs():
            return getFinishToonTaskSCStrings(toNpcId)
        count = self.getNumCogs()
        level = self.getCogLevel()
        name = self.getCogNameString()
        if count == 1:
            text = TTLocalizer.QuestsCogLevelQuestDesc
        else:
            text = TTLocalizer.QuestsCogLevelQuestDescI
        objective = text % {'level': level,
         'name': name}
        location = self.getLocationName()
        return TTLocalizer.QuestsCogLevelQuestSCString % {'objective': objective,
         'location': location}

    def getHeadlineString(self):
        return TTLocalizer.QuestsCogLevelQuestHeadline

    def doesCogCount(self, avId, cogDict, zoneId):
        questCogLevel = self.getCogLevel()
        return questCogLevel <= cogDict['level'] and avId in cogDict['activeToons'] and self.isLocationMatch(zoneId)


class SkelecogQBase:
    def getCogNameString(self):
        numCogs = self.getNumCogs()
        if numCogs == 1:
            return TTLocalizer.ASkeleton
        else:
            return TTLocalizer.SkeletonP

    def doesCogCount(self, avId, cogDict, zoneId):
        return cogDict['isSkelecog'] and avId in cogDict['activeToons'] and self.isLocationMatch(zoneId)


class SkelecogQuest(CogQuest, SkelecogQBase):
    def __init__(self, id, quest):
        CogQuest.__init__(self, id, quest)
        self.checkNumSkelecogs(self.quest[1])

    def getCogType(self):
        return Any

    def getCogNameString(self):
        return SkelecogQBase.getCogNameString(self)

    def doesCogCount(self, avId, cogDict, zoneId):
        return SkelecogQBase.doesCogCount(self, avId, cogDict, zoneId)

class SkelecogTrackQuest(CogTrackQuest, SkelecogQBase):
    trackNamesS = [TTLocalizer.BossbotSkelS,
     TTLocalizer.LawbotSkelS,
     TTLocalizer.CashbotSkelS,
     TTLocalizer.SellbotSkelS,
     TTLocalizer.GovernbotSkelS,
     TTLocalizer.EurekabotSkelS,
     TTLocalizer.BuildbotSkelS,
     TTLocalizer.ViralbotSkelS]
    trackNamesP = [TTLocalizer.BossbotSkelP,
     TTLocalizer.LawbotSkelP,
     TTLocalizer.CashbotSkelP,
     TTLocalizer.SellbotSkelP,
     TTLocalizer.GovernbotSkelP,
     TTLocalizer.EurekabotSkelP,
     TTLocalizer.BuildbotSkelP,
     TTLocalizer.ViralbotSkelP]

    def __init__(self, id, quest):
        CogTrackQuest.__init__(self, id, quest)
        self.checkNumSkelecogs(self.quest[1])
        self.checkSkelecogTrack(self.quest[2])

    def getCogNameString(self):
        return SkelecogQBase.getCogNameString(self)

    def doesCogCount(self, avId, cogDict, zoneId):
        return SkelecogQBase.doesCogCount(self, avId, cogDict, zoneId) and self.getCogTrack() == cogDict['track']


class SkelecogLevelQuest(CogLevelQuest, SkelecogQBase):
    def __init__(self, id, quest):
        CogLevelQuest.__init__(self, id, quest)
        self.checkNumSkelecogs(self.quest[1])
        self.checkSkelecogLevel(self.quest[2])

    def getCogType(self):
        return Any

    def getCogNameString(self):
        return SkelecogQBase.getCogNameString(self)

    def doesCogCount(self, avId, cogDict, zoneId):
        return SkelecogQBase.doesCogCount(self, avId, cogDict, zoneId) and self.getCogLevel() <= cogDict['level']


class SkeleReviveQBase:
    def getCogNameString(self):
        numCogs = self.getNumCogs()
        if numCogs == 1:
            return TTLocalizer.Av2Cog
        else:
            return TTLocalizer.v2CogP

    def doesCogCount(self, avId, cogDict, zoneId):
        return cogDict['hasRevives'] and avId in cogDict['activeToons'] and self.isLocationMatch(zoneId)


class SkeleReviveQuest(CogQuest, SkeleReviveQBase):
    def __init__(self, id, quest):
        CogQuest.__init__(self, id, quest)
        self.checkNumSkeleRevives(self.quest[1])

    def getCogType(self):
        return Any

    def getCogNameString(self):
        return SkeleReviveQBase.getCogNameString(self)

    def doesCogCount(self, avId, cogDict, zoneId):
        return SkeleReviveQBase.doesCogCount(self, avId, cogDict, zoneId)


class ForemanQuest(CogQuest):
    def __init__(self, id, quest):
        CogQuest.__init__(self, id, quest)
        self.checkNumForemen(self.quest[1])

    def getCogType(self):
        return Any

    def getCogNameString(self):
        numCogs = self.getNumCogs()
        if numCogs == 1:
            return TTLocalizer.AForeman
        else:
            return TTLocalizer.ForemanP

    def doesCogCount(self, avId, cogDict, zoneId):
        return bool(CogQuest.doesCogCount(self, avId, cogDict, zoneId) and cogDict['isForeman'])

BOSS_NAMES = {
 Anywhere: [TTLocalizer.ACogBoss, TTLocalizer.CogBosses, 'phase_3.5/maps/boss_icon.jpg', 'blue'],
 ToontownGlobals.SellbotHQ: [TTLocalizer.ACogVP, TTLocalizer.CogVPs, 'phase_3.5/maps/vp_icon.jpg', 'red'],
 ToontownGlobals.CashbotHQ: [TTLocalizer.ACogCFO, TTLocalizer.CogCFOs, 'phase_3.5/maps/cfo_icon.jpg', 'green'],
 ToontownGlobals.LawbotHQ: [TTLocalizer.ACogCJ, TTLocalizer.CogCJs, 'phase_3.5/maps/cj_icon.jpg', 'blue'],
 ToontownGlobals.BossbotHQ: [TTLocalizer.ACogCEO, TTLocalizer.CogCEOs, 'phase_3.5/maps/ceo_icon.jpg', 'brown']
}

class TexturedQuest:
    def getModelFromTexture(self, texture):
        cardMaker = CardMaker('cm-%s' % time.time())
        cardMaker.setFrame(-0.5, 0.5, -0.5, 0.5)
        node = NodePath(cardMaker.generate())

        node.setTexture(loader.loadTexture(texture))
        return node

    def hasFrame(self):
        return True

    def getFrame(self):
        print 'getFrame from TexturedQuest not implemented!'
        return [None, None]

class BossQuest(CogQuest, TexturedQuest):
    def __init__(self, id, quest):
        CogQuest.__init__(self, id, quest)
        self.checkNumBosses(self.quest[1])

    def getFrame(self):
        boss = BOSS_NAMES[self.quest[0]]

        return [self.getModelFromTexture(boss[2]), boss[3]]

    def getCogType(self):
        return Any

    def getCogNameString(self):
        return BOSS_NAMES[self.quest[0]][self.getNumCogs() > 1]

    def doesCogCount(self, avId, cogDict, zoneId):
        return cogDict['isBoss'] > 0 and self.isLocationMatch(zoneId)

class SupervisorQuest(CogQuest):
    def __init__(self, id, quest):
        CogQuest.__init__(self, id, quest)
        self.checkNumSupervisors(self.quest[1])

    def getCogType(self):
        return Any

    def getCogNameString(self):
        numCogs = self.getNumCogs()
        if numCogs == 1:
            return TTLocalizer.ASupervisor
        else:
            return TTLocalizer.SupervisorP

    def doesCogCount(self, avId, cogDict, zoneId):
        return bool(CogQuest.doesCogCount(self, avId, cogDict, zoneId) and cogDict['isSupervisor'])

class RescueQuest(LocationBasedQuest):
    def __init__(self, id, quest):
        Quest.__init__(self, id, quest)
        self.checkNumCogs(self.quest[1])

    def getNumToons(self):
        return self.quest[1]

    def getNumQuestItems(self):
        return self.getNumToons()

    def getLocationName(self):
        return ' ' + TTLocalizer.InVP if self.quest[0] == InVP else TTLocalizer.InFieldOffice

    def getCompletionStatus(self, av, questDesc, npc = None):
        questId, fromNpcId, toNpcId, rewardId, toonProgress = questDesc
        questComplete = toonProgress >= self.getNumToons()
        return getCompleteStatusWithNpc(questComplete, toNpcId, npc)

    def getProgressString(self, avatar, questDesc):
        if self.getCompletionStatus(avatar, questDesc) == COMPLETE:
            return CompleteString
        elif self.getNumToons() == 1:
            return ''
        else:
            return TTLocalizer.QuestsRescueQuestProgress % {'progress': questDesc[4],
             'numToons': self.getNumToons()}

    def getObjectiveStrings(self):
        numToons = self.getNumToons()
        if numToons == 1:
            text = TTLocalizer.QuestsRescueQuestToonS
        else:
            text = TTLocalizer.QuestsRescueQuestRescueDesc % {'numToons': numToons}
        return (text,)

    def getString(self):
        return TTLocalizer.QuestsRescueQuestRescue % self.getObjectiveStrings()[0]

    def getSCStrings(self, toNpcId, progress):
        numToons = self.getNumToons()
        if progress >= numToons:
            return getFinishToonTaskSCStrings(toNpcId)
        if numToons == 1:
            text = TTLocalizer.QuestsRescueQuestSCStringS
        else:
            text = TTLocalizer.QuestsRescueQuestSCStringP
        return text % {'toonLoc': self.getLocationName().strip()}

    def getHeadlineString(self):
        return TTLocalizer.QuestsRescueQuestHeadline

    def isMethodMatch(self, method):
        return self.quest[0] == method

BUILDING_NAMES = {
 Any: ['phase_3.5/maps/cogdo_icon.jpg', 'brown'],
 'l': ['phase_3.5/maps/lawbot_cogdo_icon.jpg', 'blue'],
 's': ['phase_3.5/maps/sellbot_cogdo_icon.jpg', 'red']
}

class BuildingQuest(CogQuest, TexturedQuest):
    trackCodes = ['c',
     'l',
     'm',
     's',
     'v',
     'e',
     'b',
     'z']
    trackNames = [TTLocalizer.Bossbot,
     TTLocalizer.Lawbot,
     TTLocalizer.Cashbot,
     TTLocalizer.Sellbot,
     TTLocalizer.Governbot,
     TTLocalizer.Eurekabot,
     TTLocalizer.Buildbot,
     TTLocalizer.Viralbot]

    def __init__(self, id, quest):
        CogQuest.__init__(self, id, quest)
        self.checkNumBuildings(self.quest[1])
        self.checkBuildingTrack(self.quest[2])
        self.checkBuildingFloors(self.quest[3])
        self.checkBuildingType(self.quest[4])

    def hasFrame(self):
        return self.isCogdo()

    def getFrame(self):
        building = BUILDING_NAMES[self.quest[2]]

        return [self.getModelFromTexture(building[0]), building[1]]

    def getNumFloors(self):
        return self.quest[3]

    def getBuildingTrack(self):
        return self.quest[2]

    def isCogdo(self):
        return self.quest[4]

    def getNumQuestItems(self):
        return self.getNumBuildings()

    def getNumBuildings(self):
        return self.quest[1]

    def getCompletionStatus(self, av, questDesc, npc = None):
        questId, fromNpcId, toNpcId, rewardId, toonProgress = questDesc
        questComplete = toonProgress >= self.getNumBuildings()
        return getCompleteStatusWithNpc(questComplete, toNpcId, npc)

    def getProgressString(self, avatar, questDesc):
        if self.getCompletionStatus(avatar, questDesc) == COMPLETE:
            return CompleteString
        elif self.getNumBuildings() == 1:
            return ''
        else:
            return TTLocalizer.QuestsBuildingQuestProgressString % {'progress': questDesc[4],
             'num': self.getNumBuildings()}

    def getObjectiveStrings(self):
        count = self.getNumBuildings()
        buildingTrack = self.getBuildingTrack()
        if buildingTrack == Any:
            type = TTLocalizer.Cog
        else:
            type = self.trackNames[self.trackCodes.index(buildingTrack)]
        floors = ''

        if self.isCogdo():
            if buildingTrack == Any:
                text = TTLocalizer.QuestsCogdoQuestDescU if count == 1 else TTLocalizer.QuestsCogdoQuestDescUM
            else:
                text = TTLocalizer.QuestsCogdoQuestDesc if count == 1 else TTLocalizer.QuestsCogdoQuestDescM
        else:
            floors = TTLocalizer.QuestsBuildingQuestFloorNumbers[self.getNumFloors() - 1]

            if count == 1:
                text = TTLocalizer.QuestsBuildingQuestDesc if floors == '' else TTLocalizer.QuestsBuildingQuestDescF
            else:
                text = TTLocalizer.QuestsBuildingQuestDescC if floors == '' else TTLocalizer.QuestsBuildingQuestDescCF

        return (text % {'count': count,
          'floors': floors,
          'type': type},)

    def getString(self):
        return TTLocalizer.QuestsBuildingQuestString % self.getObjectiveStrings()[0]

    def getSCStrings(self, toNpcId, progress):
        if progress >= self.getNumBuildings():
            return getFinishToonTaskSCStrings(toNpcId)
        count = self.getNumBuildings()
        buildingTrack = self.getBuildingTrack()
        floors = ''

        if buildingTrack == Any:
            type = TTLocalizer.Cog
        else:
            type = self.trackNames[self.trackCodes.index(buildingTrack)]

        if self.isCogdo():
            if buildingTrack == Any:
                text = TTLocalizer.QuestsCogdoQuestDescU if count == 1 else TTLocalizer.QuestsCogdoQuestDescMI
            else:
                text = TTLocalizer.QuestsCogdoQuestDesc if count == 1 else TTLocalizer.QuestsCogdoQuestDescMUI
        else:
            floors = TTLocalizer.QuestsBuildingQuestFloorNumbers[self.getNumFloors() - 1]

            if count == 1:
                text = TTLocalizer.QuestsBuildingQuestDesc if floors == '' else TTLocalizer.QuestsBuildingQuestDescF
            else:
                text = TTLocalizer.QuestsBuildingQuestDescI if floors == '' else TTLocalizer.QuestsBuildingQuestDescIF
        objective = text % {'floors': floors,
         'type': type}
        return TTLocalizer.QuestsBuildingQuestSCString % {'objective': objective,
         'location': self.getLocationName()}

    def getHeadlineString(self):
        return TTLocalizer.QuestsBuildingQuestHeadline

    def doesCogCount(self, avId, cogDict, zoneId):
        return 0

    def doesBuildingTypeCount(self, type):
        buildingTrack = self.getBuildingTrack()
        if buildingTrack == Any or buildingTrack == type:
            return True
        return False

class FactoryQuest(LocationBasedQuest):
    factoryTypeNames = {FT_FullSuit: TTLocalizer.Cog,
     FT_Leg: TTLocalizer.FactoryTypeLeg,
     FT_Arm: TTLocalizer.FactoryTypeArm,
     FT_Torso: TTLocalizer.FactoryTypeTorso}

    def __init__(self, id, quest):
        LocationBasedQuest.__init__(self, id, quest)
        self.checkNumFactories(self.quest[1])

    def getNumQuestItems(self):
        return self.getNumFactories()

    def getNumFactories(self):
        return self.quest[1]

    def getFactoryType(self):
        loc = self.getLocation()
        type = Any
        if loc in ToontownGlobals.factoryId2factoryType:
            type = ToontownGlobals.factoryId2factoryType[loc]
        return type

    def getCompletionStatus(self, av, questDesc, npc = None):
        questId, fromNpcId, toNpcId, rewardId, toonProgress = questDesc
        questComplete = toonProgress >= self.getNumFactories()
        return getCompleteStatusWithNpc(questComplete, toNpcId, npc)

    def getProgressString(self, avatar, questDesc):
        if self.getCompletionStatus(avatar, questDesc) == COMPLETE:
            return CompleteString
        elif self.getNumFactories() == 1:
            return ''
        else:
            return TTLocalizer.QuestsFactoryQuestProgressString % {'progress': questDesc[4],
             'num': self.getNumFactories()}

    def getObjectiveStrings(self):
        count = self.getNumFactories()
        factoryType = self.getFactoryType()
        if factoryType == Any:
            type = TTLocalizer.Cog
        else:
            type = FactoryQuest.factoryTypeNames[factoryType]
        if count == 1:
            text = TTLocalizer.QuestsFactoryQuestDesc
        else:
            text = TTLocalizer.QuestsFactoryQuestDescC
        return (text % {'count': count,
          'type': type},)

    def getString(self):
        return TTLocalizer.QuestsFactoryQuestString % self.getObjectiveStrings()[0]

    def getSCStrings(self, toNpcId, progress):
        if progress >= self.getNumFactories():
            return getFinishToonTaskSCStrings(toNpcId)
        factoryType = self.getFactoryType()
        if factoryType == Any:
            type = TTLocalizer.Cog
        else:
            type = FactoryQuest.factoryTypeNames[factoryType]
        count = self.getNumFactories()
        if count == 1:
            text = TTLocalizer.QuestsFactoryQuestDesc
        else:
            text = TTLocalizer.QuestsFactoryQuestDescI
        objective = text % {'type': type}
        location = self.getLocationName()
        return TTLocalizer.QuestsFactoryQuestSCString % {'objective': objective,
         'location': location}

    def getHeadlineString(self):
        return TTLocalizer.QuestsFactoryQuestHeadline

    def doesFactoryCount(self, avId, location):
        return self.isLocationMatch(location)

class MintQuest(LocationBasedQuest):
    def __init__(self, id, quest):
        LocationBasedQuest.__init__(self, id, quest)
        self.checkNumMints(self.quest[1])

    def getNumQuestItems(self):
        return self.getNumMints()

    def getNumMints(self):
        return self.quest[1]

    def getCompletionStatus(self, av, questDesc, npc = None):
        questId, fromNpcId, toNpcId, rewardId, toonProgress = questDesc
        questComplete = toonProgress >= self.getNumMints()
        return getCompleteStatusWithNpc(questComplete, toNpcId, npc)

    def getProgressString(self, avatar, questDesc):
        if self.getCompletionStatus(avatar, questDesc) == COMPLETE:
            return CompleteString
        elif self.getNumMints() == 1:
            return ''
        else:
            return TTLocalizer.QuestsMintQuestProgressString % {'progress': questDesc[4],
             'num': self.getNumMints()}

    def getObjectiveStrings(self):
        count = self.getNumMints()
        if count == 1:
            text = TTLocalizer.QuestsMintQuestDesc
        else:
            text = TTLocalizer.QuestsMintQuestDescC % {'count': count}
        return (text,)

    def getString(self):
        return TTLocalizer.QuestsMintQuestString % self.getObjectiveStrings()[0]

    def getSCStrings(self, toNpcId, progress):
        if progress >= self.getNumMints():
            return getFinishToonTaskSCStrings(toNpcId)
        count = self.getNumMints()
        if count == 1:
            objective = TTLocalizer.QuestsMintQuestDesc
        else:
            objective = TTLocalizer.QuestsMintQuestDescI
        location = self.getLocationName()
        return TTLocalizer.QuestsMintQuestSCString % {'objective': objective,
         'location': location}

    def getHeadlineString(self):
        return TTLocalizer.QuestsMintQuestHeadline

    def doesMintCount(self, avId, location):
        return self.isLocationMatch(location)

class CogPartQuest(LocationBasedQuest):
    def __init__(self, id, quest):
        LocationBasedQuest.__init__(self, id, quest)
        self.checkNumCogParts(self.quest[1])

    def getNumQuestItems(self):
        return self.getNumParts()

    def getNumParts(self):
        return self.quest[1]

    def getCompletionStatus(self, av, questDesc, npc = None):
        questId, fromNpcId, toNpcId, rewardId, toonProgress = questDesc
        questComplete = toonProgress >= self.getNumParts()
        return getCompleteStatusWithNpc(questComplete, toNpcId, npc)

    def getProgressString(self, avatar, questDesc):
        if self.getCompletionStatus(avatar, questDesc) == COMPLETE:
            return CompleteString
        elif self.getNumParts() == 1:
            return ''
        else:
            return TTLocalizer.QuestsCogPartQuestProgressString % {'progress': questDesc[4],
             'num': self.getNumParts()}

    def getObjectiveStrings(self):
        count = self.getNumParts()
        if count == 1:
            text = TTLocalizer.QuestsCogPartQuestDesc
        else:
            text = TTLocalizer.QuestsCogPartQuestDescC
        return (text % {'count': count},)

    def getString(self):
        return TTLocalizer.QuestsCogPartQuestString % self.getObjectiveStrings()[0]

    def getSCStrings(self, toNpcId, progress):
        if progress >= self.getNumParts():
            return getFinishToonTaskSCStrings(toNpcId)
        count = self.getNumParts()
        if count == 1:
            text = TTLocalizer.QuestsCogPartQuestDesc
        else:
            text = TTLocalizer.QuestsCogPartQuestDescI
        objective = text
        location = self.getLocationName()
        return TTLocalizer.QuestsCogPartQuestSCString % {'objective': objective,
         'location': location}

    def getHeadlineString(self):
        return TTLocalizer.QuestsCogPartQuestHeadline

    def doesCogPartCount(self, avId, location):
        return self.isLocationMatch(location)

class DeliverGagQuest(Quest):
    def __init__(self, id, quest):
        Quest.__init__(self, id, quest)
        self.checkNumGags(self.quest[0])
        self.checkGagTrack(self.quest[1])
        self.checkGagItem(self.quest[2])

    def getGagType(self):
        return (self.quest[1], self.quest[2])

    def getNumQuestItems(self):
        return self.getNumGags()

    def getNumGags(self):
        return self.quest[0]

    def getCompletionStatus(self, av, questDesc, npc = None):
        questId, fromNpcId, toNpcId, rewardId, toonProgress = questDesc
        gag = self.getGagType()
        num = self.getNumGags()
        track = gag[0]
        level = gag[1]
        questComplete = npc and av.inventory and av.inventory.numItem(track, level) >= num
        return getCompleteStatusWithNpc(questComplete, toNpcId, npc)

    def getProgressString(self, avatar, questDesc):
        if self.getCompletionStatus(avatar, questDesc) == COMPLETE:
            return CompleteString
        elif self.getNumGags() == 1:
            return ''
        else:
            return TTLocalizer.QuestsDeliverGagQuestProgress % {'progress': questDesc[4],
             'numGags': self.getNumGags()}

    def getObjectiveStrings(self):
        track, item = self.getGagType()
        num = self.getNumGags()
        if num == 1:
            text = ToontownBattleGlobals.AvPropStringsSingular[track][item]
        else:
            gagName = ToontownBattleGlobals.AvPropStringsPlural[track][item]
            text = TTLocalizer.QuestsItemNameAndNum % {'num': TTLocalizer.getLocalNum(num),
             'name': gagName}
        return (text,)

    def getString(self):
        return TTLocalizer.QuestsDeliverGagQuestString % self.getObjectiveStrings()[0]

    def getRewardString(self, progress):
        return TTLocalizer.QuestsDeliverGagQuestStringLong % self.getObjectiveStrings()[0]

    def getDefaultQuestDialog(self):
        return TTLocalizer.QuestsDeliverGagQuestStringLong % self.getObjectiveStrings()[0] + '\x07' + TTLocalizer.QuestsDeliverGagQuestInstructions

    def getSCStrings(self, toNpcId, progress):
        if progress >= self.getNumGags():
            return getFinishToonTaskSCStrings(toNpcId)
        track, item = self.getGagType()
        num = self.getNumGags()
        if num == 1:
            text = TTLocalizer.QuestsDeliverGagQuestToSCStringS
            gagName = ToontownBattleGlobals.AvPropStringsSingular[track][item]
        else:
            text = TTLocalizer.QuestsDeliverGagQuestToSCStringP
            gagName = ToontownBattleGlobals.AvPropStringsPlural[track][item]
        return [text % {'gagName': gagName}, TTLocalizer.QuestsDeliverGagQuestSCString] + getVisitSCStrings(toNpcId)

    def getHeadlineString(self):
        return TTLocalizer.QuestsDeliverGagQuestHeadline

    def removeGags(self, av):
        gag = self.getGagType()
        inventory = av.inventory
        takenGags = 0
        for i in xrange(self.getNumGags()):
            if inventory.useItem(gag[0], gag[1]):
                takenGags += 1
        av.b_setInventory(inventory.makeNetString())
        return takenGags

class DeliverItemQuest(Quest):
    def __init__(self, id, quest):
        Quest.__init__(self, id, quest)
        self.checkDeliveryItem(self.quest[0])

    def getItem(self):
        return self.quest[0]

    def getCompletionStatus(self, av, questDesc, npc = None):
        questId, fromNpcId, toNpcId, rewardId, toonProgress = questDesc
        if npc and npcMatches(toNpcId, npc):
            return COMPLETE
        else:
            return INCOMPLETE_WRONG_NPC

    def getProgressString(self, avatar, questDesc):
        return TTLocalizer.QuestsDeliverItemQuestProgress

    def getObjectiveStrings(self):
        iDict = ItemDict[self.getItem()]
        article = iDict[2]
        itemName = iDict[0]
        return [article + itemName]

    def getString(self):
        return TTLocalizer.QuestsDeliverItemQuestString % self.getObjectiveStrings()[0]

    def getRewardString(self, progress):
        return TTLocalizer.QuestsDeliverItemQuestStringLong % self.getObjectiveStrings()[0]

    def getDefaultQuestDialog(self):
        return TTLocalizer.QuestsDeliverItemQuestStringLong % self.getObjectiveStrings()[0]

    def getSCStrings(self, toNpcId, progress):
        iDict = ItemDict[self.getItem()]
        article = iDict[2]
        itemName = iDict[0]
        return [TTLocalizer.QuestsDeliverItemQuestSCString % {'article': article,
          'itemName': itemName}] + getVisitSCStrings(toNpcId)

    def getHeadlineString(self):
        return TTLocalizer.QuestsDeliverItemQuestHeadline


class VisitQuest(Quest):
    def __init__(self, id, quest):
        Quest.__init__(self, id, quest)

    def getCompletionStatus(self, av, questDesc, npc = None):
        questId, fromNpcId, toNpcId, rewardId, toonProgress = questDesc
        if npc and npcMatches(toNpcId, npc):
            return COMPLETE
        else:
            return INCOMPLETE_WRONG_NPC

    def getProgressString(self, avatar, questDesc):
        return TTLocalizer.QuestsVisitQuestProgress

    def getObjectiveStrings(self):
        return ['']

    def getString(self):
        return TTLocalizer.QuestsVisitQuestStringShort

    def getChooseString(self):
        return TTLocalizer.QuestsVisitQuestStringLong

    def getRewardString(self, progress):
        return TTLocalizer.QuestsVisitQuestStringLong

    def getDefaultQuestDialog(self):
        return random.choice(DefaultVisitQuestDialog)

    def getSCStrings(self, toNpcId, progress):
        return getVisitSCStrings(toNpcId)

    def getHeadlineString(self):
        return TTLocalizer.QuestsVisitQuestHeadline


class RecoverItemQuest(LocationBasedQuest):
    def __init__(self, id, quest):
        LocationBasedQuest.__init__(self, id, quest)
        self.checkNumItems(self.quest[1])
        self.checkRecoveryItem(self.quest[2])
        self.checkPercentChance(self.quest[3])
        if len(self.quest) > 5:
            self.checkRecoveryItemHolderAndType(self.quest[4], self.quest[5])
        else:
            self.checkRecoveryItemHolderAndType(self.quest[4])

    def testRecover(self, progress):
        test = random.random() * 100
        chance = self.getPercentChance()
        numberDone = progress & pow(2, 16) - 1
        numberNotDone = progress >> 16
        returnTest = None
        avgNum2Kill = 1.0 / (chance / 100.0)
        if numberNotDone >= avgNum2Kill * 1.5:
            chance = 100
        elif numberNotDone > avgNum2Kill * 0.5:
            diff = float(numberNotDone - avgNum2Kill * 0.5)
            luck = 1.0 + abs(diff / (avgNum2Kill * 0.5))
            chance *= luck
        if test <= chance:
            returnTest = 1
            numberNotDone = 0
            numberDone += 1
        else:
            returnTest = 0
            numberNotDone += 1
            numberDone += 0
        returnCount = numberNotDone << 16
        returnCount += numberDone
        return (returnTest, returnCount)

    def testDone(self, progress):
        numberDone = progress & pow(2, 16) - 1
        print 'Quest number done %s' % numberDone
        if numberDone >= self.getNumItems():
            return 1
        else:
            return 0

    def getNumQuestItems(self):
        return self.getNumItems()

    def getNumItems(self):
        return self.quest[1]

    def getItem(self):
        return self.quest[2]

    def getPercentChance(self):
        return self.quest[3]

    def getHolder(self):
        return self.quest[4]

    def getHolderType(self):
        if len(self.quest) == 5:
            return 'type'
        else:
            return self.quest[5]

    def getCompletionStatus(self, av, questDesc, npc = None):
        questId, fromNpcId, toNpcId, rewardId, toonProgress = questDesc
        forwardProgress = toonProgress & pow(2, 16) - 1
        questComplete = forwardProgress >= self.getNumItems()
        return getCompleteStatusWithNpc(questComplete, toNpcId, npc)

    def getProgressString(self, avatar, questDesc):
        if self.getCompletionStatus(avatar, questDesc) == COMPLETE:
            return CompleteString
        elif self.getNumItems() == 1:
            return ''
        else:
            progress = questDesc[4] & pow(2, 16) - 1
            return TTLocalizer.QuestsRecoverItemQuestProgress % {'progress': progress,
             'numItems': self.getNumItems()}

    def getObjectiveStrings(self):
        holder = self.getHolder()
        holderType = self.getHolderType()
        if holder == Any:
            holderName = TTLocalizer.TheCogs
        elif holder == AnyFish:
            holderName = TTLocalizer.AFish
        elif holderType == 'type':
            holderName = SuitBattleGlobals.SuitAttributes[holder]['pluralname']
        elif holderType == 'level':
            holderName = TTLocalizer.QuestsRecoverItemQuestHolderString % {'level': TTLocalizer.Level,
             'holder': holder,
             'cogs': TTLocalizer.Cogs}
        elif holderType == 'track':
            if holder == 'c':
                holderName = TTLocalizer.BossbotP
            elif holder == 's':
                holderName = TTLocalizer.SellbotP
            elif holder == 'm':
                holderName = TTLocalizer.CashbotP
            elif holder == 'l':
                holderName = TTLocalizer.LawbotP
            elif holder == 'v':
                holderName = TTLocalizer.GovernbotP
            elif holder == 'e':
                holderName = TTLocalizer.EurekabotP
            elif holder == 'b':
                holderName = TTLocalizer.BuildbotP
            elif holder == 'z':
                holderName = TTLocalizer.ViralbotP
        item = self.getItem()
        num = self.getNumItems()
        if num == 1:
            itemName = ItemDict[item][2] + ItemDict[item][0]
        else:
            itemName = TTLocalizer.QuestsItemNameAndNum % {'num': TTLocalizer.getLocalNum(num),
             'name': ItemDict[item][1]}
        return [itemName, holderName]

    def getString(self):
        return TTLocalizer.QuestsRecoverItemQuestString % {'item': self.getObjectiveStrings()[0],
         'holder': self.getObjectiveStrings()[1]}

    def getSCStrings(self, toNpcId, progress):
        item = self.getItem()
        num = self.getNumItems()
        forwardProgress = progress & pow(2, 16) - 1
        if forwardProgress >= self.getNumItems():
            if num == 1:
                itemName = ItemDict[item][2] + ItemDict[item][0]
            else:
                itemName = TTLocalizer.QuestsItemNameAndNum % {'num': TTLocalizer.getLocalNum(num),
                 'name': ItemDict[item][1]}
            if toNpcId == ToonHQ:
                strings = [TTLocalizer.QuestsRecoverItemQuestReturnToHQSCString % itemName, TTLocalizer.QuestsRecoverItemQuestGoToHQSCString]
            elif toNpcId:
                npcName, hoodName, buildingArticle, buildingName, toStreet, streetName, isInPlayground = getNpcInfo(toNpcId)
                strings = [TTLocalizer.QuestsRecoverItemQuestReturnToSCString % {'item': itemName,
                  'npcName': npcName}]
                if isInPlayground:
                    strings.append(TTLocalizer.QuestsRecoverItemQuestGoToPlaygroundSCString % hoodName)
                else:
                    strings.append(TTLocalizer.QuestsRecoverItemQuestGoToStreetSCString % {'to': toStreet,
                     'street': streetName,
                     'hood': hoodName})
                strings.extend([TTLocalizer.QuestsRecoverItemQuestVisitBuildingSCString % (buildingArticle, buildingName), TTLocalizer.QuestsRecoverItemQuestWhereIsBuildingSCString % (buildingArticle, buildingName)])
            return strings
        holder = self.getHolder()
        holderType = self.getHolderType()
        locName = self.getLocationName()
        if holder == Any:
            holderName = TTLocalizer.TheCogs
        elif holder == AnyFish:
            holderName = TTLocalizer.TheFish
        elif holderType == 'type':
            holderName = SuitBattleGlobals.SuitAttributes[holder]['pluralname']
        elif holderType == 'level':
            holderName = TTLocalizer.QuestsRecoverItemQuestHolderString % {'level': TTLocalizer.Level,
             'holder': holder,
             'cogs': TTLocalizer.Cogs}
        elif holderType == 'track':
            if holder == 'c':
                holderName = TTLocalizer.BossbotP
            elif holder == 's':
                holderName = TTLocalizer.SellbotP
            elif holder == 'm':
                holderName = TTLocalizer.CashbotP
            elif holder == 'l':
                holderName = TTLocalizer.LawbotP
            elif holder == 'v':
                holderName = TTLocalizer.GovernbotP
            elif holder == 'e':
                holderName = TTLocalizer.EurekabotP
            elif holder == 'b':
                holderName = TTLocalizer.BuildbotP
            elif holder == 'z':
                holderName = TTLocalizer.ViralbotP
        if num == 1:
            itemName = ItemDict[item][2] + ItemDict[item][0]
        else:
            itemName = TTLocalizer.QuestsItemNameAndNum % {'num': TTLocalizer.getLocalNum(num),
             'name': ItemDict[item][1]}
        return TTLocalizer.QuestsRecoverItemQuestRecoverFromSCString % {'item': itemName,
         'holder': holderName,
         'loc': locName}

    def getHeadlineString(self):
        return TTLocalizer.QuestsRecoverItemQuestHeadline

    def doesCogCount(self, avId, cogDict, zoneId):
        questCogType = self.getHolder()
        return (questCogType is Any or questCogType is cogDict[self.getHolderType()]) and avId in cogDict['activeToons'] and self.isLocationMatch(zoneId)


class TrackChoiceQuest(Quest):
    def __init__(self, id, quest):
        Quest.__init__(self, id, quest)
        self.checkTrackChoice(self.quest[0])
        self.checkTrackChoice(self.quest[1])

    def getChoices(self):
        return (self.quest[0], self.quest[1])

    def getCompletionStatus(self, av, questDesc, npc = None):
        questId, fromNpcId, toNpcId, rewardId, toonProgress = questDesc
        if npc and npcMatches(toNpcId, npc):
            return COMPLETE
        else:
            return INCOMPLETE_WRONG_NPC

    def getProgressString(self, avatar, questDesc):
        if self.getCompletionStatus(avatar, questDesc) == COMPLETE:
            return CompleteString
        else:
            return NotChosenString

    def getObjectiveStrings(self):
        trackA, trackB = self.getChoices()
        trackAName = ToontownBattleGlobals.Tracks[trackA].capitalize()
        trackBName = ToontownBattleGlobals.Tracks[trackB].capitalize()
        return [trackAName, trackBName]

    def getString(self):
        return TTLocalizer.QuestsTrackChoiceQuestString % {'trackA': self.getObjectiveStrings()[0],
         'trackB': self.getObjectiveStrings()[1]}

    def getSCStrings(self, toNpcId, progress):
        trackA, trackB = self.getChoices()
        trackAName = ToontownBattleGlobals.Tracks[trackA].capitalize()
        trackBName = ToontownBattleGlobals.Tracks[trackB].capitalize()
        return [TTLocalizer.QuestsTrackChoiceQuestSCString % {'trackA': trackAName,
          'trackB': trackBName}, TTLocalizer.QuestsTrackChoiceQuestMaybeSCString % trackAName, TTLocalizer.QuestsTrackChoiceQuestMaybeSCString % trackBName] + getVisitSCStrings(toNpcId)

    def getHeadlineString(self):
        return TTLocalizer.QuestsTrackChoiceQuestHeadline


class FriendQuest(Quest):
    def filterFunc(avatar):
        if len(avatar.getFriendsList()) == 0:
            return 1
        else:
            return 0

    filterFunc = staticmethod(filterFunc)

    def __init__(self, id, quest):
        Quest.__init__(self, id, quest)

    def getCompletionStatus(self, av, questDesc, npc = None):
        questId, fromNpcId, toNpcId, rewardId, toonProgress = questDesc
        questComplete = toonProgress >= 1 or len(av.getFriendsList()) > 0
        return getCompleteStatusWithNpc(questComplete, toNpcId, npc)

    def getProgressString(self, avatar, questDesc):
        if self.getCompletionStatus(avatar, questDesc) == COMPLETE:
            return CompleteString
        else:
            return ''

    def getString(self):
        return TTLocalizer.QuestsFriendQuestString

    def getSCStrings(self, toNpcId, progress):
        if progress:
            return getFinishToonTaskSCStrings(toNpcId)
        return TTLocalizer.QuestsFriendQuestSCString

    def getHeadlineString(self):
        return TTLocalizer.QuestsFriendQuestHeadline

    def getObjectiveStrings(self):
        return [TTLocalizer.QuestsFriendQuestString]

class TrolleyQuest(Quest):
    def __init__(self, id, quest):
        Quest.__init__(self, id, quest)

    def getCompletionStatus(self, av, questDesc, npc = None):
        questId, fromNpcId, toNpcId, rewardId, toonProgress = questDesc
        questComplete = toonProgress >= 1
        return getCompleteStatusWithNpc(questComplete, toNpcId, npc)

    def getProgressString(self, avatar, questDesc):
        if self.getCompletionStatus(avatar, questDesc) == COMPLETE:
            return CompleteString
        else:
            return ''

    def getString(self):
        return TTLocalizer.QuestsFriendQuestString

    def getSCStrings(self, toNpcId, progress):
        if progress:
            return getFinishToonTaskSCStrings(toNpcId)
        return TTLocalizer.QuestsTrolleyQuestSCString

    def getHeadlineString(self):
        return TTLocalizer.QuestsTrolleyQuestHeadline

    def getObjectiveStrings(self):
        return [TTLocalizer.QuestsTrolleyQuestString]


class MailboxQuest(Quest):
    def __init__(self, id, quest):
        Quest.__init__(self, id, quest)

    def getCompletionStatus(self, av, questDesc, npc = None):
        questId, fromNpcId, toNpcId, rewardId, toonProgress = questDesc
        questComplete = toonProgress >= 1
        return getCompleteStatusWithNpc(questComplete, toNpcId, npc)

    def getProgressString(self, avatar, questDesc):
        if self.getCompletionStatus(avatar, questDesc) == COMPLETE:
            return CompleteString
        else:
            return ''

    def getString(self):
        return TTLocalizer.QuestsMailboxQuestString

    def getSCStrings(self, toNpcId, progress):
        if progress:
            return getFinishToonTaskSCStrings(toNpcId)
        return TTLocalizer.QuestsMailboxQuestSCString

    def getHeadlineString(self):
        return TTLocalizer.QuestsMailboxQuestHeadline

    def getObjectiveStrings(self):
        return [TTLocalizer.QuestsMailboxQuestString]


class PhoneQuest(Quest):
    def __init__(self, id, quest):
        Quest.__init__(self, id, quest)

    def getCompletionStatus(self, av, questDesc, npc = None):
        questId, fromNpcId, toNpcId, rewardId, toonProgress = questDesc
        questComplete = toonProgress >= 1
        return getCompleteStatusWithNpc(questComplete, toNpcId, npc)

    def getProgressString(self, avatar, questDesc):
        if self.getCompletionStatus(avatar, questDesc) == COMPLETE:
            return CompleteString
        else:
            return ''

    def getString(self):
        return TTLocalizer.QuestsPhoneQuestString

    def getSCStrings(self, toNpcId, progress):
        if progress:
            return getFinishToonTaskSCStrings(toNpcId)
        return TTLocalizer.QuestsPhoneQuestSCString

    def getHeadlineString(self):
        return TTLocalizer.QuestsPhoneQuestHeadline

    def getObjectiveStrings(self):
        return [TTLocalizer.QuestsPhoneQuestString]
    

DefaultDialog = {GREETING: DefaultGreeting,
 QUEST: DefaultQuest,
 INCOMPLETE: DefaultIncomplete,
 INCOMPLETE_PROGRESS: DefaultIncompleteProgress,
 INCOMPLETE_WRONG_NPC: DefaultIncompleteWrongNPC,
 COMPLETE: DefaultComplete,
 LEAVING: DefaultLeaving}

def getQuestFromNpcId(id):
    return QuestDict.get(id)[QuestDictFromNpcIndex]


def getQuestToNpcId(id):
    return QuestDict.get(id)[QuestDictToNpcIndex]

def getQuestDialog(id):
    return QuestDict.get(id)[QuestDictDialogIndex]


def getQuestReward(id, av):
    baseRewardId = QuestDict.get(id)[QuestDictRewardIndex]
    return transformReward(baseRewardId, av)


def isQuestJustForFun(questId, rewardId):
    questEntry = QuestDict.get(questId)
    if questEntry:
        tier = questEntry[QuestDictTierIndex]
        return isRewardOptional(tier, rewardId)
    else:
        return False

NoRewardTierZeroQuests = (101, 110, 175)
RewardTierZeroQuests = ()
PreClarabelleQuestIds = NoRewardTierZeroQuests + RewardTierZeroQuests
QuestDict = {
    101: (TT_TIER, Start, (CogQuest, Anywhere, 1, 'f'), Any, ToonHQ, NA, 110, DefaultDialog),
    110: (TT_TIER, Cont, (RecoverItemQuest, ToontownGlobals.ToontownCentral, 1, 4, VeryEasy, AnyFish), 2005, ToonHQ, NA, 175, DefaultDialog),
    145: (TT_TIER, Cont, (RecoverItemQuest, ToontownGlobals.ToontownCentral, 1, 20, VeryEasy, Any, 'type'), ToonHQ, ToonHQ, NA, 175, DefaultDialog),
    150: (TT_TIER, Cont, (FriendQuest,), Same, Same, NA, 175, DefaultDialog),
    175: (TT_TIER, Cont, (PhoneQuest,), Same, ToonHQ, 602, NA, TTLocalizer.QuestDialogDict[175]),
    164: (TT_TIER + 1, Start, (VisitQuest,), Any, 2001, NA, 165, TTLocalizer.QuestDialogDict[164]),
    165: (TT_TIER + 1, Start, (CogQuest, ToontownGlobals.SillyStreet, 4, Any), 2001, Same, NA, (170, 171, 172), TTLocalizer.QuestDialogDict[165]),
    170: (TT_TIER + 1, Cont, (VisitQuest,), Same, 2005, NA, 400, TTLocalizer.QuestDialogDict[170]),
    171: (TT_TIER + 1, Cont, (VisitQuest,), Same, 2003, NA, 400, TTLocalizer.QuestDialogDict[171]),
    172: (TT_TIER + 1, Cont, (VisitQuest,), Same, 2002, NA, 400, TTLocalizer.QuestDialogDict[172]),
    400: (TT_TIER + 1, Cont, (TrackChoiceQuest, ToontownBattleGlobals.SOUND_TRACK, ToontownBattleGlobals.HEAL_TRACK), Same, Same, 400, NA, TTLocalizer.QuestDialogDict[400]),
    1001: (TT_TIER + 2, Start, (CogQuest, ToontownGlobals.ToontownCentral, 5, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    1002: (TT_TIER + 2, Start, (CogQuest, ToontownGlobals.ToontownCentral, 4, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    1003: (TT_TIER + 2, Start, (CogQuest, ToontownGlobals.ToontownCentral, 5, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    1004: (TT_TIER + 2, Start, (CogQuest, ToontownGlobals.ToontownCentral, 4, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    1005: (TT_TIER + 2, Start, (CogQuest, Anywhere, 2, 'f'), Any, ToonHQ, Any, NA, DefaultDialog),
    1006: (TT_TIER + 2, Start, (CogQuest, Anywhere, 2, 'p'), Any, ToonHQ, Any, NA, DefaultDialog),
    1007: (TT_TIER + 2, Start, (CogQuest, Anywhere, 2, 'bf'), Any, ToonHQ, Any, NA, DefaultDialog),
    1008: (TT_TIER + 2, Start, (CogQuest, Anywhere, 2, 'b'), Any, ToonHQ, Any, NA, DefaultDialog),
    1009: (TT_TIER + 2, Start, (CogQuest, Anywhere, 2, 'sc'), Any, ToonHQ, Any, NA, DefaultDialog),
    1010: (TT_TIER + 2, Start, (CogQuest, Anywhere, 2, 'pp'), Any, ToonHQ, Any, NA, DefaultDialog),
    1011: (TT_TIER + 2, Start, (CogQuest, Anywhere, 2, 'cc'), Any, ToonHQ, Any, NA, DefaultDialog),
    1012: (TT_TIER + 2, Start, (CogQuest, Anywhere, 2, 'tm'), Any, ToonHQ, Any, NA, DefaultDialog),
    1013: (TT_TIER + 2, Start, (CogQuest, Anywhere, 3, 'f'), Any, ToonHQ, Any, NA, DefaultDialog),
    1014: (TT_TIER + 2, Start, (CogQuest, Anywhere, 2, 'p'), Any, ToonHQ, Any, NA, DefaultDialog),
    1015: (TT_TIER + 2, Start, (CogQuest, Anywhere, 3, 'bf'), Any, ToonHQ, Any, NA, DefaultDialog),
    1016: (TT_TIER + 2, Start, (CogQuest, Anywhere, 4, 'b'), Any, ToonHQ, Any, NA, DefaultDialog),
    1017: (TT_TIER + 2, Start, (CogQuest, Anywhere, 1, 'ym'), Any, ToonHQ, Any, NA, DefaultDialog),
    1018: (TT_TIER + 2, Start, (CogQuest, Anywhere, 1, 'nd'), Any, ToonHQ, Any, NA, DefaultDialog),
    1019: (TT_TIER + 2, Start, (CogQuest, Anywhere, 1, 'tw'), Any, ToonHQ, Any, NA, DefaultDialog),
    1020: (TT_TIER + 2, Start, (CogQuest, Anywhere, 1, 'dt'), Any, ToonHQ, Any, NA, DefaultDialog),
    1021: (TT_TIER + 2, Start, (CogLevelQuest, ToontownGlobals.ToontownCentral, 2, 2), Any, ToonHQ, Any, NA, DefaultDialog),
    1022: (TT_TIER + 2, Start, (CogLevelQuest, ToontownGlobals.ToontownCentral, 4, 2), Any, ToonHQ, Any, NA, DefaultDialog),
    1023: (TT_TIER + 2, Start, (CogLevelQuest, ToontownGlobals.ToontownCentral, 3, 2), Any, ToonHQ, Any, NA, DefaultDialog),
    1024: (TT_TIER + 2, Start, (CogLevelQuest, ToontownGlobals.ToontownCentral, 4, 2), Any, ToonHQ, Any, NA, DefaultDialog),
    1025: (TT_TIER + 2, Start, (CogLevelQuest, ToontownGlobals.ToontownCentral, 3, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    1026: (TT_TIER + 2, Start, (CogLevelQuest, ToontownGlobals.ToontownCentral, 5, 2), Any, ToonHQ, Any, NA, DefaultDialog),
    1027: (TT_TIER + 2, Start, (CogTrackQuest, ToontownGlobals.ToontownCentral, 2, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    1028: (TT_TIER + 2, Start, (CogTrackQuest, ToontownGlobals.ToontownCentral, 2, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    1029: (TT_TIER + 2, Start, (CogTrackQuest, ToontownGlobals.ToontownCentral, 2, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    1030: (TT_TIER + 2, Start, (CogTrackQuest, ToontownGlobals.ToontownCentral, 2, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    1031: (TT_TIER + 2, Start, (CogTrackQuest, ToontownGlobals.ToontownCentral, 3, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    1032: (TT_TIER + 2, Start, (CogTrackQuest, ToontownGlobals.ToontownCentral, 3, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    1033: (TT_TIER + 2, Start, (CogTrackQuest, ToontownGlobals.ToontownCentral, 3, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    1034: (TT_TIER + 2, Start, (CogTrackQuest, ToontownGlobals.ToontownCentral, 3, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    1035: (TT_TIER + 2, Start, (CogTrackQuest, ToontownGlobals.ToontownCentral, 5, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    1036: (TT_TIER + 2, Start, (CogTrackQuest, ToontownGlobals.ToontownCentral, 2, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    1037: (TT_TIER + 2, Start, (CogTrackQuest, ToontownGlobals.ToontownCentral, 3, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    1038: (TT_TIER + 2, Start, (CogTrackQuest, ToontownGlobals.ToontownCentral, 3, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    1039: (TT_TIER + 2, Start, (VisitQuest,), Any, 2108, NA, 1041, TTLocalizer.QuestDialogDict[1039]),
    1040: (TT_TIER + 2, Start, (VisitQuest,), Any, 2122, NA, 1041, TTLocalizer.QuestDialogDict[1040]),
    1041: (TT_TIER + 2, Cont, (VisitQuest,), Same, 2319, NA, 1044, TTLocalizer.QuestDialogDict[1041]),
    1044: (TT_TIER + 2, Cont, (RecoverItemQuest, Anywhere, 3, 21, VeryEasy, Any, 'type'), Same, Same, NA, 1045, TTLocalizer.QuestDialogDict[1044]),
    1045: (TT_TIER + 2, Cont, (DeliverItemQuest, 8), Same, ToonHQ, 300, NA, TTLocalizer.QuestDialogDict[1045]),
    1046: (TT_TIER + 2, Start, (VisitQuest,), Any, 2315, NA, 1047, TTLocalizer.QuestDialogDict[1046]),
    1047: (TT_TIER + 2, Start, (RecoverItemQuest, Anywhere, 3, 9, VeryEasy, 'm', 'track'), 2103, Same, NA, 1048, TTLocalizer.QuestDialogDict[1047]),
    1048: (TT_TIER + 2, Cont, (DeliverItemQuest, 9), Same, 2309, NA, 1049, TTLocalizer.QuestDialogDict[1048]),
    1049: (TT_TIER + 2, Cont, (RecoverItemQuest, Anywhere, 2, 2007, VeryEasy, 3, 'level'), Same, Same, NA, 1053, TTLocalizer.QuestDialogDict[1049]),
    1053: (TT_TIER + 2, Cont, (DeliverItemQuest, 3), Same, 2316, 700, NA, TTLocalizer.QuestDialogDict[1053]),
    1054: (TT_TIER + 2, Start, (VisitQuest,), Any, 2209, NA, 1055, TTLocalizer.QuestDialogDict[1054]),
    1055: (TT_TIER + 2, Start, (RecoverItemQuest, Anywhere, 3, 10, Easy, AnyFish), 2128, Same, NA, 1056, TTLocalizer.QuestDialogDict[1055]),
    1056: (TT_TIER + 2, Cont, (VisitQuest,), Same, 2213, NA, 1057, TTLocalizer.QuestDialogDict[1056]),
    1057: (TT_TIER + 2, Cont, (CogLevelQuest, ToontownGlobals.ToontownCentral, 3, 3), Same, Same, NA, 1058, TTLocalizer.QuestDialogDict[1057]),
    1058: (TT_TIER + 2, Cont, (DeliverItemQuest, 11), Same, 2221, 200, NA, TTLocalizer.QuestDialogDict[1058]),
    1059: (TT_TIER + 2, Start, (VisitQuest,), Any, 2216, NA, 1060, TTLocalizer.QuestDialogDict[1059]),
    1060: (TT_TIER + 2, Start, (RecoverItemQuest, Anywhere, 1, 12, Medium, AnyFish), 2216, Same, NA, 1062, TTLocalizer.QuestDialogDict[1060]),
    1061: (TT_TIER + 2, Cont, (CogQuest, ToontownGlobals.ToontownCentral, 2, 'p'), Same, Same, 100, NA, TTLocalizer.QuestDialogDict[1061]),
    1062: (TT_TIER + 2, Cont, (CogQuest, ToontownGlobals.ToontownCentral, 2, 'b'), Same, Same, 100, NA, TTLocalizer.QuestDialogDict[1062]),
    900: (TT_TIER + 3, Start, (VisitQuest,), Any, 2201, NA, 1063, TTLocalizer.QuestDialogDict[900]),
    1063: (TT_TIER + 3, Start, (RecoverItemQuest, Anywhere, 1, 13, Easy, 3, 'level'), 2201, Same, NA, 1067, TTLocalizer.QuestDialogDict[1063]),
    1067: (TT_TIER + 3, Cont, (DeliverItemQuest, 13), Same, 2207, NA, 1068, TTLocalizer.QuestDialogDict[1067]),
    1068: (TT_TIER + 3, Cont, (CogQuest, ToontownGlobals.ToontownCentral, 5, Any), Same, Same, NA, (1069, 1070, 1071), TTLocalizer.QuestDialogDict[1068]),
    1069: (TT_TIER + 3, Cont, (RecoverItemQuest, Anywhere, 1, 13, Easy, 'm', 'track'), Same, Same, NA, 1072, TTLocalizer.QuestDialogDict[1069]),
    1070: (TT_TIER + 3, Cont, (RecoverItemQuest, Anywhere, 1, 13, Easy, 's', 'track'), Same, Same, NA, 1072, TTLocalizer.QuestDialogDict[1070]),
    1071: (TT_TIER + 3, Cont, (RecoverItemQuest, Anywhere, 1, 13, VeryEasy, 'c', 'track'), Same, Same, NA, 1072, TTLocalizer.QuestDialogDict[1071]),
    1072: (TT_TIER + 3, Cont, (DeliverItemQuest, 13), Same, 2301, NA, 1073, TTLocalizer.QuestDialogDict[1072]),
    1073: (TT_TIER + 3, Cont, (VisitQuest,), Any, 2201, NA, 1074, TTLocalizer.QuestDialogDict[1073]),
    1074: (TT_TIER + 3, Cont, (RecoverItemQuest, Anywhere, 1, 13, Medium, Any), Same, Same, NA, 1075, TTLocalizer.QuestDialogDict[1074]),
    1075: (TT_TIER + 3, Cont, (DeliverItemQuest, 13), Same, 2301, 900, NA, TTLocalizer.QuestDialogDict[1075]),
    1076: (TT_TIER + 2, Start, (VisitQuest,), Any, 2217, NA, 1077, TTLocalizer.QuestDialogDict[1076]),
    1077: (TT_TIER + 2, Start, (RecoverItemQuest, Anywhere, 1, 14, Easy, Any), 2217, Same, NA, 1078, TTLocalizer.QuestDialogDict[1077]),
    1078: (TT_TIER + 2, Cont, (DeliverItemQuest, 14), Same, 2221, NA, 1079, TTLocalizer.QuestDialogDict[1078]),
    1079: (TT_TIER + 2, Cont, (RecoverItemQuest, Anywhere, 1, 15, Easy, 'bf'), Same, 2217, NA, 1080, TTLocalizer.QuestDialogDict[1079]),
    1092: (TT_TIER + 2, Cont, (RecoverItemQuest, Anywhere, 1, 15, Easy, 'sc'), Same, 2217, NA, 1080, TTLocalizer.QuestDialogDict[1092]),
    1080: (TT_TIER + 2, Cont, (RecoverItemQuest, Anywhere, 4, 15, Easy, 'l', 'track'), Same, Same, 500, NA, TTLocalizer.QuestDialogDict[1080]),
    1081: (TT_TIER + 2, Start, (VisitQuest,), Any, 2220, NA, 1082, TTLocalizer.QuestDialogDict[1081]),
    1082: (TT_TIER + 2, Start, (RecoverItemQuest, Anywhere, 1, 16, VeryEasy, 's', 'track'), 2220, Same, NA, 1083, TTLocalizer.QuestDialogDict[1082]),
    1083: (TT_TIER + 2, Cont, (RecoverItemQuest, Anywhere, 1, 17, Easy, 'l', 'track'), Same, Same, NA, 1084, TTLocalizer.QuestDialogDict[1083]),
    1084: (TT_TIER + 2, Cont, (RecoverItemQuest, Anywhere, 1, 18, VeryEasy, 'm', 'track'), Same, Same, 102, NA, TTLocalizer.QuestDialogDict[1084]),
    1085: (TT_TIER + 2, Start, (VisitQuest,), Any, 2302, NA, 1086, TTLocalizer.QuestDialogDict[1085]),
    1086: (TT_TIER + 2, Start, (RecoverItemQuest, Anywhere, 3, 20, Easy, 'p'), 2316, Same, NA, 1089, TTLocalizer.QuestDialogDict[1086]),
    1089: (TT_TIER + 2, Cont, (DeliverItemQuest, 19), Same, ToonHQ, 101, NA, TTLocalizer.QuestDialogDict[1089]),
    1090: (TT_TIER + 2, Start, (VisitQuest,), Any, 2316, NA, 1091, TTLocalizer.QuestDialogDict[1090]),
    1091: (TT_TIER + 2, Start, (CogLevelQuest, ToontownGlobals.ToontownCentral, 5, Any), 2316, ToonHQ, 101, NA, TTLocalizer.QuestDialogDict[1091]),
    1100: (TT_TIER + 2, Start, (CogQuest, ToontownGlobals.ToontownCentral, 4, Any), Any, ToonHQ, NA, 1101, DefaultDialog),
    1101: (TT_TIER + 2, Cont, (DeliverItemQuest, 1000), Any, 2004, 1000, NA, DefaultDialog),
    1102: (TT_TIER + 2, Start, (CogLevelQuest, ToontownGlobals.ToontownCentral, 4, 2), Any, ToonHQ, NA, 1103, DefaultDialog),
    1103: (TT_TIER + 2, Cont, (DeliverItemQuest, 1000), Any, 2004, 1000, NA, DefaultDialog),
    1105: (TT_TIER + 2, Start, (CogQuest, Anywhere, 2, 'f'), Any, ToonHQ, Any, NA, DefaultDialog),
    1106: (TT_TIER + 2, Start, (CogQuest, Anywhere, 2, 'p'), Any, ToonHQ, Any, NA, DefaultDialog),
    1107: (TT_TIER + 2, Start, (CogQuest, Anywhere, 2, 'bf'), Any, ToonHQ, Any, NA, DefaultDialog),
    1108: (TT_TIER + 2, Start, (CogQuest, Anywhere, 2, 'b'), Any, ToonHQ, Any, NA, DefaultDialog),
    1109: (TT_TIER + 2, Start, (CogQuest, Anywhere, 2, 'sc'), Any, ToonHQ, Any, NA, DefaultDialog),
    1110: (TT_TIER + 2, Start, (CogQuest, Anywhere, 2, 'pp'), Any, ToonHQ, Any, NA, DefaultDialog),
    1111: (TT_TIER + 2, Start, (CogQuest, Anywhere, 2, 'cc'), Any, ToonHQ, Any, NA, DefaultDialog),
    1112: (TT_TIER + 2, Start, (CogQuest, Anywhere, 2, 'tm'), Any, ToonHQ, Any, NA, DefaultDialog),
    1205: (TT_TIER + 3, Start, (CogQuest, Anywhere, 3, 'f'), Any, ToonHQ, Any, NA, DefaultDialog),
    1206: (TT_TIER + 3, Start, (CogQuest, Anywhere, 3, 'p'), Any, ToonHQ, Any, NA, DefaultDialog),
    1207: (TT_TIER + 3, Start, (CogQuest, Anywhere, 3, 'bf'), Any, ToonHQ, Any, NA, DefaultDialog),
    1208: (TT_TIER + 3, Start, (CogQuest, Anywhere, 3, 'b'), Any, ToonHQ, Any, NA, DefaultDialog),
    1209: (TT_TIER + 3, Start, (CogQuest, Anywhere, 2, 'sc'), Any, ToonHQ, Any, NA, DefaultDialog),
    1210: (TT_TIER + 3, Start, (CogQuest, Anywhere, 2, 'pp'), Any, ToonHQ, Any, NA, DefaultDialog),
    1211: (TT_TIER + 3, Start, (CogQuest, Anywhere, 2, 'cc'), Any, ToonHQ, Any, NA, DefaultDialog),
    1212: (TT_TIER + 3, Start, (CogQuest, Anywhere, 2, 'tm'), Any, ToonHQ, Any, NA, DefaultDialog),
    401: (DD_TIER, Start, (TrackChoiceQuest, ToontownBattleGlobals.TRAP_TRACK, ToontownBattleGlobals.LURE_TRACK), Any, ToonHQ, 400, NA, TTLocalizer.QuestDialogDict[401]),
    2001: (DD_TIER, Start, (CogQuest, Anywhere, 3, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    2002: (DD_TIER, Start, (CogQuest, Anywhere, 4, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    2003: (DD_TIER, Start, (CogQuest, Anywhere, 5, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    2004: (DD_TIER, Start, (CogQuest, Anywhere, 6, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    2005: (DD_TIER, Start, (CogQuest, Anywhere, 7, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    2006: (DD_TIER, Start, (CogQuest, Anywhere, 8, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    2007: (DD_TIER, Start, (CogQuest, Anywhere, 9, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    2008: (DD_TIER, Start, (CogQuest, Anywhere, 10, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    2009: (DD_TIER, Start, (CogQuest, Anywhere, 10, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    2010: (DD_TIER, Start, (CogLevelQuest, Anywhere, 2, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    2011: (DD_TIER, Start, (CogLevelQuest, Anywhere, 3, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    2012: (DD_TIER, Start, (CogLevelQuest, Anywhere, 2, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    2013: (DD_TIER, Start, (CogLevelQuest, Anywhere, 4, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    2014: (DD_TIER, Start, (CogLevelQuest, Anywhere, 4, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    2015: (DD_TIER, Start, (CogLevelQuest, Anywhere, 5, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    2816: (DD_TIER, Start, (CogLevelQuest, Anywhere, 4, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    2817: (DD_TIER, Start, (CogLevelQuest, Anywhere, 3, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    2818: (DD_TIER, Start, (CogLevelQuest, Anywhere, 3, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    2819: (DD_TIER, Start, (CogLevelQuest, Anywhere, 4, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    2020: (DD_TIER, Start, (CogQuest, Anywhere, 10, Any), Any, ToonHQ, NA, 2021, DefaultDialog),
    2021: (DD_TIER, Cont, (DeliverItemQuest, 1000), Any, 1007, 1000, NA, DefaultDialog),
    2101: (DD_TIER + 1, Start, (CogQuest, ToontownGlobals.DonaldsDock, 3, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    2102: (DD_TIER + 1, Start, (CogQuest, ToontownGlobals.DonaldsDock, 4, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    2103: (DD_TIER + 1, Start, (CogQuest, ToontownGlobals.DonaldsDock, 5, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    2104: (DD_TIER + 1, Start, (CogQuest, Anywhere, 6, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    2105: (DD_TIER + 1, Start, (CogQuest, Anywhere, 7, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    2106: (DD_TIER + 1, Start, (CogQuest, Anywhere, 8, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    2107: (DD_TIER + 1, Start, (CogQuest, Anywhere, 5, 'f'), Any, ToonHQ, Any, NA, DefaultDialog),
    2108: (DD_TIER + 1, Start, (CogQuest, Anywhere, 4, 'p'), Any, ToonHQ, Any, NA, DefaultDialog),
    2109: (DD_TIER + 1, Start, (CogQuest, Anywhere, 4, 'ym'), Any, ToonHQ, Any, NA, DefaultDialog),
    2110: (DD_TIER + 1, Start, (CogQuest, Anywhere, 3, 'mm'), Any, ToonHQ, Any, NA, DefaultDialog),
    2111: (DD_TIER + 1, Start, (CogQuest, Anywhere, 2, 'ds'), Any, ToonHQ, Any, NA, DefaultDialog),
    2112: (DD_TIER + 1, Start, (CogQuest, Anywhere, 1, 'hh'), Any, ToonHQ, Any, NA, DefaultDialog),
    2113: (DD_TIER + 1, Start, (CogQuest, Anywhere, 4, 'cc'), Any, ToonHQ, Any, NA, DefaultDialog),
    2114: (DD_TIER + 1, Start, (CogQuest, Anywhere, 4, 'tm'), Any, ToonHQ, Any, NA, DefaultDialog),
    2115: (DD_TIER + 1, Start, (CogQuest, Anywhere, 2, 'nd'), Any, ToonHQ, Any, NA, DefaultDialog),
    2116: (DD_TIER + 1, Start, (CogQuest, Anywhere, 3, 'gh'), Any, ToonHQ, Any, NA, DefaultDialog),
    2117: (DD_TIER + 1, Start, (CogQuest, Anywhere, 2, 'ms'), Any, ToonHQ, Any, NA, DefaultDialog),
    2118: (DD_TIER + 1, Start, (CogQuest, Anywhere, 1, 'tf'), Any, ToonHQ, Any, NA, DefaultDialog),
    2119: (DD_TIER + 1, Start, (CogQuest, Anywhere, 4, 'sc'), Any, ToonHQ, Any, NA, DefaultDialog),
    2120: (DD_TIER + 1, Start, (CogQuest, Anywhere, 4, 'pp'), Any, ToonHQ, Any, NA, DefaultDialog),
    2121: (DD_TIER + 1, Start, (CogQuest, Anywhere, 3, 'tw'), Any, ToonHQ, Any, NA, DefaultDialog),
    2122: (DD_TIER + 1, Start, (CogQuest, Anywhere, 3, 'bc'), Any, ToonHQ, Any, NA, DefaultDialog),
    2123: (DD_TIER + 1, Start, (CogQuest, Anywhere, 2, 'nc'), Any, ToonHQ, Any, NA, DefaultDialog),
    2124: (DD_TIER + 1, Start, (CogQuest, Anywhere, 1, 'mb'), Any, ToonHQ, Any, NA, DefaultDialog),
    2125: (DD_TIER + 1, Start, (CogQuest, Anywhere, 5, 'bf'), Any, ToonHQ, Any, NA, DefaultDialog),
    2126: (DD_TIER + 1, Start, (CogQuest, Anywhere, 4, 'b'), Any, ToonHQ, Any, NA, DefaultDialog),
    2127: (DD_TIER + 1, Start, (CogQuest, Anywhere, 4, 'dt'), Any, ToonHQ, Any, NA, DefaultDialog),
    2128: (DD_TIER + 1, Start, (CogQuest, Anywhere, 3, 'ac'), Any, ToonHQ, Any, NA, DefaultDialog),
    2129: (DD_TIER + 1, Start, (CogQuest, Anywhere, 2, 'bs'), Any, ToonHQ, Any, NA, DefaultDialog),
    2130: (DD_TIER + 1, Start, (CogQuest, Anywhere, 1, 'sd'), Any, ToonHQ, Any, NA, DefaultDialog),
    2131: (DD_TIER + 1, Start, (CogLevelQuest, ToontownGlobals.DonaldsDock, 2, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    2132: (DD_TIER + 1, Start, (CogLevelQuest, ToontownGlobals.DonaldsDock, 3, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    2133: (DD_TIER + 1, Start, (CogLevelQuest, ToontownGlobals.DonaldsDock, 2, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    2134: (DD_TIER + 1, Start, (CogLevelQuest, ToontownGlobals.DonaldsDock, 4, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    2135: (DD_TIER + 1, Start, (CogLevelQuest, ToontownGlobals.DonaldsDock, 3, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    2136: (DD_TIER + 1, Start, (CogLevelQuest, ToontownGlobals.DonaldsDock, 4, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    2137: (DD_TIER + 1, Start, (CogLevelQuest, ToontownGlobals.DonaldsDock, 3, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    2138: (DD_TIER + 1, Start, (CogLevelQuest, ToontownGlobals.DonaldsDock, 4, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    2139: (DD_TIER + 1, Start, (CogTrackQuest, ToontownGlobals.DonaldsDock, 3, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    2140: (DD_TIER + 1, Start, (CogTrackQuest, ToontownGlobals.DonaldsDock, 3, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    2141: (DD_TIER + 1, Start, (CogTrackQuest, ToontownGlobals.DonaldsDock, 3, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    2142: (DD_TIER + 1, Start, (CogTrackQuest, ToontownGlobals.DonaldsDock, 3, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    2143: (DD_TIER + 1, Start, (CogTrackQuest, ToontownGlobals.DonaldsDock, 4, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    2144: (DD_TIER + 1, Start, (CogTrackQuest, ToontownGlobals.DonaldsDock, 4, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    2145: (DD_TIER + 1, Start, (CogTrackQuest, ToontownGlobals.DonaldsDock, 4, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    2146: (DD_TIER + 1, Start, (CogTrackQuest, ToontownGlobals.DonaldsDock, 4, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    2147: (DD_TIER + 1, Start, (CogTrackQuest, Anywhere, 5, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    2148: (DD_TIER + 1, Start, (CogTrackQuest, Anywhere, 5, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    2149: (DD_TIER + 1, Start, (CogTrackQuest, Anywhere, 5, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    2150: (DD_TIER + 1, Start, (CogTrackQuest, Anywhere, 5, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    2151: (DD_TIER + 1, Start, (BuildingQuest, Anywhere, 1, Any, 1, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    2152: (DD_TIER + 1, Start, (BuildingQuest, Anywhere, 1, Any, 2, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    2153: (DD_TIER + 1, Start, (BuildingQuest, Anywhere, 1, Any, 1, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    2154: (DD_TIER + 1, Start, (BuildingQuest, Anywhere, 1, Any, 2, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    2155: (DD_TIER + 1, Start, (BuildingQuest, Anywhere, 1, 'm', 1, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    2156: (DD_TIER + 1, Start, (BuildingQuest, Anywhere, 1, 's', 1, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    2157: (DD_TIER + 1, Start, (BuildingQuest, Anywhere, 1, 'c', 1, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    2158: (DD_TIER + 1, Start, (BuildingQuest, Anywhere, 1, 'l', 1, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    2201: (DD_TIER + 1, Start, (VisitQuest,), Any, 1101, NA, 2202, TTLocalizer.QuestDialogDict[2201]),
    2202: (DD_TIER + 1, Start, (RecoverItemQuest, Anywhere, 1, 2001, Medium, 'pp'), 1101, Same, 101, NA, TTLocalizer.QuestDialogDict[2202]),
    2203: (DD_TIER + 1, Start, (VisitQuest,), Any, 1106, NA, 2204, TTLocalizer.QuestDialogDict[2203]),
    2204: (DD_TIER + 1, Start, (DeliverItemQuest, 2002), 1106, 1104, NA, 2205, TTLocalizer.QuestDialogDict[2204]),
    2205: (DD_TIER + 1, Cont, (RecoverItemQuest, Anywhere, 1, 2008, Medium, 'f'), Same, Same, NA, 2206, TTLocalizer.QuestDialogDict[2205]),
    2206: (DD_TIER + 1, Cont, (DeliverItemQuest, 2004), Same, 1106, 201, NA, TTLocalizer.QuestDialogDict[2206]),
    2207: (DD_TIER + 1, Start, (VisitQuest,), Any, 1202, NA, 2208, TTLocalizer.QuestDialogDict[2207]),
    2208: (DD_TIER + 1, Start, (RecoverItemQuest, Anywhere, 1, 2005, Easy, 'bs'), 1202, Same, 701, NA, TTLocalizer.QuestDialogDict[2208]),
    2209: (DD_TIER + 1, Start, (VisitQuest,), Any, 1302, NA, 2210, TTLocalizer.QuestDialogDict[2209]),
    2210: (DD_TIER + 1, Start, (VisitQuest,), 1302, 1313, NA, 2211, TTLocalizer.QuestDialogDict[2210]),
    2211: (DD_TIER + 1, Cont, (CogQuest, ToontownGlobals.DonaldsDock, 3, 'mm'), Same, Same, NA, 2212, TTLocalizer.QuestDialogDict[2211]),
    2212: (DD_TIER + 1, Cont, (DeliverItemQuest, 2006), Same, 1302, NA, 2213, TTLocalizer.QuestDialogDict[2212]),
    2213: (DD_TIER + 1, Cont, (VisitQuest,), Same, 1322, NA, 2214, TTLocalizer.QuestDialogDict[2213]),
    2214: (DD_TIER + 1, Cont, (RecoverItemQuest, ToontownGlobals.DonaldsDock, 3, 2007, Easy, Any), Same, Same, NA, 2215, TTLocalizer.QuestDialogDict[2214]),
    2215: (DD_TIER + 1, Cont, (DeliverItemQuest, 2008), Same, 1302, 301, NA, TTLocalizer.QuestDialogDict[2215]),
    2500: (DD_TIER + 1, Start, (CogQuest, ToontownGlobals.DonaldsDock, 10, Any), Any, ToonHQ, NA, 2501, DefaultDialog),
    2501: (DD_TIER + 1, Cont, (DeliverItemQuest, 1000), Any, 1007, 1000, NA, DefaultDialog),
    2801: (DD_TIER + 2, Start, (CogQuest, Anywhere, 3, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    2802: (DD_TIER + 2, Start, (CogQuest, Anywhere, 4, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    2803: (DD_TIER + 2, Start, (CogQuest, Anywhere, 5, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    2804: (DD_TIER + 2, Start, (CogQuest, Anywhere, 6, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    2805: (DD_TIER + 2, Start, (CogQuest, Anywhere, 7, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    2806: (DD_TIER + 2, Start, (CogQuest, Anywhere, 8, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    2807: (DD_TIER + 2, Start, (CogQuest, Anywhere, 9, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    2808: (DD_TIER + 2, Start, (CogQuest, Anywhere, 10, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    2809: (DD_TIER + 2, Start, (CogQuest, Anywhere, 10, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    2810: (DD_TIER + 2, Start, (CogLevelQuest, Anywhere, 2, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    2811: (DD_TIER + 2, Start, (CogLevelQuest, Anywhere, 3, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    2812: (DD_TIER + 2, Start, (CogLevelQuest, Anywhere, 2, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    2813: (DD_TIER + 2, Start, (CogLevelQuest, Anywhere, 3, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    2814: (DD_TIER + 2, Start, (CogLevelQuest, Anywhere, 2, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    2815: (DD_TIER + 2, Start, (CogLevelQuest, Anywhere, 3, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    2816: (DD_TIER + 2, Start, (CogLevelQuest, Anywhere, 4, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    2817: (DD_TIER + 2, Start, (CogLevelQuest, Anywhere, 2, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    2818: (DD_TIER + 2, Start, (CogLevelQuest, Anywhere, 3, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    2819: (DD_TIER + 2, Start, (CogLevelQuest, Anywhere, 4, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    2820: (DD_TIER + 2, Start, (CogQuest, Anywhere, 15, Any), Any, ToonHQ, NA, 2821, DefaultDialog),
    2821: (DD_TIER + 2, Cont, (DeliverItemQuest, 1000), Any, 1007, 1000, NA, DefaultDialog),
    901: (DD_TIER + 2, Start, (VisitQuest,), Any, 1203, NA, 2902, TTLocalizer.QuestDialogDict[901]),
    2902: (DD_TIER + 2, Start, (VisitQuest,), 1203, 1118, NA, 2903, TTLocalizer.QuestDialogDict[2902]),
    2903: (DD_TIER + 2, Cont, (DeliverItemQuest, 2009), Same, 1106, NA, 2904, TTLocalizer.QuestDialogDict[2903]),
    2904: (DD_TIER + 2, Cont, (DeliverItemQuest, 2010), Same, 1203, NA, 2905, TTLocalizer.QuestDialogDict[2904]),
    2905: (DD_TIER + 2, Cont, (VisitQuest, 2009), Same, 1201, NA, 2907, TTLocalizer.QuestDialogDict[2905]),
    2907: (DD_TIER + 2, Cont, (DeliverItemQuest, 2011), Same, 1203, NA, (2910, 2915, 2920), TTLocalizer.QuestDialogDict[2907]),
    2910: (DD_TIER + 2, Cont, (VisitQuest,), Same, 1107, NA, 2911, TTLocalizer.QuestDialog_2910),
    2911: (DD_TIER + 2, Cont, (CogTrackQuest, ToontownGlobals.DonaldsDock, 4, 'm'), Same, Same, NA, 2925, TTLocalizer.QuestDialogDict[2911]),
    2915: (DD_TIER + 2, Cont, (VisitQuest,), Same, 1204, NA, 2916, TTLocalizer.QuestDialog_2910),
    2916: (DD_TIER + 2, Cont, (CogTrackQuest, ToontownGlobals.DonaldsDock, 2, 's'), Same, Same, NA, 2925, TTLocalizer.QuestDialogDict[2916]),
    2920: (DD_TIER + 2, Cont, (VisitQuest,), Same, 1204, NA, 2921, TTLocalizer.QuestDialog_2910),
    2921: (DD_TIER + 2, Cont, (CogTrackQuest, ToontownGlobals.DonaldsDock, 4, 'c'), Same, Same, NA, 2925, TTLocalizer.QuestDialogDict[2921]),
    2925: (DD_TIER + 2, Cont, (DeliverItemQuest, 2012), Same, 1203, NA, 2926, TTLocalizer.QuestDialogDict[2925]),
    2926: (DD_TIER + 2, Cont, (BuildingQuest, ToontownGlobals.DonaldsDock, 1, Any, 2, 0), Same, Same, 900, NA, TTLocalizer.QuestDialogDict[2926]),
    3101: (DG_TIER, Start, (CogQuest, ToontownGlobals.DaisyGardens, 7, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    3102: (DG_TIER, Start, (CogQuest, ToontownGlobals.DaisyGardens, 8, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    3103: (DG_TIER, Start, (CogQuest, ToontownGlobals.DaisyGardens, 10, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    3104: (DG_TIER, Start, (CogQuest, Anywhere, 10, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    3105: (DG_TIER, Start, (CogQuest, Anywhere, 10, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    3106: (DG_TIER, Start, (CogQuest, Anywhere, 12, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    3107: (DG_TIER, Start, (CogQuest, Anywhere, 6, 'f'), Any, ToonHQ, Any, NA, DefaultDialog),
    3108: (DG_TIER, Start, (CogQuest, Anywhere, 5, 'p'), Any, ToonHQ, Any, NA, DefaultDialog),
    3109: (DG_TIER, Start, (CogQuest, Anywhere, 5, 'ym'), Any, ToonHQ, Any, NA, DefaultDialog),
    3110: (DG_TIER, Start, (CogQuest, Anywhere, 4, 'mm'), Any, ToonHQ, Any, NA, DefaultDialog),
    3111: (DG_TIER, Start, (CogQuest, Anywhere, 4, 'ds'), Any, ToonHQ, Any, NA, DefaultDialog),
    3112: (DG_TIER, Start, (CogQuest, Anywhere, 4, 'hh'), Any, ToonHQ, Any, NA, DefaultDialog),
    3113: (DG_TIER, Start, (CogQuest, Anywhere, 7, 'cc'), Any, ToonHQ, Any, NA, DefaultDialog),
    3114: (DG_TIER, Start, (CogQuest, Anywhere, 5, 'tm'), Any, ToonHQ, Any, NA, DefaultDialog),
    3115: (DG_TIER, Start, (CogQuest, Anywhere, 4, 'nd'), Any, ToonHQ, Any, NA, DefaultDialog),
    3116: (DG_TIER, Start, (CogQuest, Anywhere, 4, 'gh'), Any, ToonHQ, Any, NA, DefaultDialog),
    3117: (DG_TIER, Start, (CogQuest, Anywhere, 4, 'ms'), Any, ToonHQ, Any, NA, DefaultDialog),
    3118: (DG_TIER, Start, (CogQuest, Anywhere, 5, 'tf'), Any, ToonHQ, Any, NA, DefaultDialog),
    3119: (DG_TIER, Start, (CogQuest, Anywhere, 6, 'sc'), Any, ToonHQ, Any, NA, DefaultDialog),
    3120: (DG_TIER, Start, (CogQuest, Anywhere, 6, 'pp'), Any, ToonHQ, Any, NA, DefaultDialog),
    3121: (DG_TIER, Start, (CogQuest, Anywhere, 4, 'tw'), Any, ToonHQ, Any, NA, DefaultDialog),
    3122: (DG_TIER, Start, (CogQuest, Anywhere, 4, 'bc'), Any, ToonHQ, Any, NA, DefaultDialog),
    3123: (DG_TIER, Start, (CogQuest, Anywhere, 4, 'nc'), Any, ToonHQ, Any, NA, DefaultDialog),
    3124: (DG_TIER, Start, (CogQuest, Anywhere, 4, 'mb'), Any, ToonHQ, Any, NA, DefaultDialog),
    3125: (DG_TIER, Start, (CogQuest, Anywhere, 7, 'bf'), Any, ToonHQ, Any, NA, DefaultDialog),
    3126: (DG_TIER, Start, (CogQuest, Anywhere, 6, 'b'), Any, ToonHQ, Any, NA, DefaultDialog),
    3127: (DG_TIER, Start, (CogQuest, Anywhere, 6, 'dt'), Any, ToonHQ, Any, NA, DefaultDialog),
    3128: (DG_TIER, Start, (CogQuest, Anywhere, 4, 'ac'), Any, ToonHQ, Any, NA, DefaultDialog),
    3129: (DG_TIER, Start, (CogQuest, Anywhere, 4, 'bs'), Any, ToonHQ, Any, NA, DefaultDialog),
    3130: (DG_TIER, Start, (CogQuest, Anywhere, 4, 'sd'), Any, ToonHQ, Any, NA, DefaultDialog),
    3131: (DG_TIER, Start, (CogLevelQuest, Anywhere, 7, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    3132: (DG_TIER, Start, (CogLevelQuest, Anywhere, 10, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    3133: (DG_TIER, Start, (CogLevelQuest, Anywhere, 5, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    3134: (DG_TIER, Start, (CogLevelQuest, Anywhere, 8, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    3135: (DG_TIER, Start, (CogLevelQuest, Anywhere, 3, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    3136: (DG_TIER, Start, (CogLevelQuest, Anywhere, 3, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    3137: (DG_TIER, Start, (CogLevelQuest, Anywhere, 3, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    3138: (DG_TIER, Start, (CogLevelQuest, Anywhere, 8, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    3139: (DG_TIER, Start, (CogTrackQuest, ToontownGlobals.DaisyGardens, 6, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    3140: (DG_TIER, Start, (CogTrackQuest, ToontownGlobals.DaisyGardens, 5, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    3141: (DG_TIER, Start, (CogTrackQuest, ToontownGlobals.DaisyGardens, 5, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    3142: (DG_TIER, Start, (CogTrackQuest, ToontownGlobals.DaisyGardens, 5, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    3143: (DG_TIER, Start, (CogTrackQuest, ToontownGlobals.DaisyGardens, 8, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    3144: (DG_TIER, Start, (CogTrackQuest, ToontownGlobals.DaisyGardens, 8, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    3145: (DG_TIER, Start, (CogTrackQuest, ToontownGlobals.DaisyGardens, 8, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    3146: (DG_TIER, Start, (CogTrackQuest, ToontownGlobals.DaisyGardens, 8, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    3147: (DG_TIER, Start, (CogTrackQuest, Anywhere, 10, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    3148: (DG_TIER, Start, (CogTrackQuest, Anywhere, 10, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    3149: (DG_TIER, Start, (CogTrackQuest, Anywhere, 10, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    3150: (DG_TIER, Start, (CogTrackQuest, Anywhere, 10, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    3151: (DG_TIER, Start, (BuildingQuest, Anywhere, 1, Any, 2, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    3152: (DG_TIER, Start, (BuildingQuest, Anywhere, 1, Any, 2, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    3153: (DG_TIER, Start, (BuildingQuest, Anywhere, 1, Any, 2, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    3154: (DG_TIER, Start, (BuildingQuest, Anywhere, 2, Any, 2, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    3155: (DG_TIER, Start, (BuildingQuest, Anywhere, 1, 'm', 2, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    3156: (DG_TIER, Start, (BuildingQuest, Anywhere, 1, 's', 2, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    3157: (DG_TIER, Start, (BuildingQuest, Anywhere, 1, 'c', 2, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    3158: (DG_TIER, Start, (BuildingQuest, Anywhere, 1, 'l', 2, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    3200: (DG_TIER, Start, (VisitQuest,), Any, 5101, NA, 3201, TTLocalizer.QuestDialogDict[3200]),
    3201: (DG_TIER, Start, (DeliverItemQuest, 5001), 5101, 5228, NA, 3203, TTLocalizer.QuestDialogDict[3201]),
    3203: (DG_TIER, Cont, (RecoverItemQuest, ToontownGlobals.DaisyGardens, 1, 5002, Hard, Any), Same, Same, 100, NA, TTLocalizer.QuestDialogDict[3203]),
    3204: (DG_TIER, Start, (VisitQuest,), Any, 5122, NA, 3205, TTLocalizer.QuestDialogDict[3204]),
    3205: (DG_TIER, Start, (RecoverItemQuest, Anywhere, 1, 5003, Medium, 'b'), 5122, Same, 100, NA, TTLocalizer.QuestDialogDict[3205]),
    3206: (DG_TIER, Start, (VisitQuest,), Any, 5107, NA, 3207, TTLocalizer.QuestDialogDict[3206]),
    3207: (DG_TIER, Start, (RecoverItemQuest, ToontownGlobals.DaisyGardens, 10, 5004, VeryEasy, 'dt'), 5107, Same, 101, NA, TTLocalizer.QuestDialogDict[3207]),
    3211: (DG_TIER, Start, (CogQuest, 5200, 5, Any), Same, Same, 100, NA, TTLocalizer.QuestDialogDict[3211]),
    3217: (DG_TIER, Start, (RecoverItemQuest, Anywhere, 1, 5010, VeryEasy, 'nd'), ToonHQ, ToonHQ, NA, 3218, TTLocalizer.QuestDialogDict[3217]),
    3218: (DG_TIER, Cont, (RecoverItemQuest, Anywhere, 1, 5010, Medium, 'gh'), Same, Same, NA, 3219, TTLocalizer.QuestDialogDict[3218]),
    3219: (DG_TIER, Cont, (RecoverItemQuest, Anywhere, 1, 5010, Easy, 'ms'), Same, Same, 101, NA, TTLocalizer.QuestDialogDict[3219]),
    3244: (DG_TIER, Start, (RecoverItemQuest, Anywhere, 1, 5010, VeryEasy, 'ac'), ToonHQ, ToonHQ, NA, 3245, TTLocalizer.QuestDialogDict[3244]),
    3245: (DG_TIER, Cont, (RecoverItemQuest, Anywhere, 1, 5010, Hard, 'bs'), Same, Same, NA, 3246, TTLocalizer.QuestDialogDict[3245]),
    3246: (DG_TIER, Cont, (RecoverItemQuest, Anywhere, 1, 5010, Medium, 'sd'), Same, Same, 101, NA, TTLocalizer.QuestDialogDict[3246]),
    3220: (DG_TIER, Start, (VisitQuest,), Any, 5222, NA, 3221, TTLocalizer.QuestDialogDict[3220]),
    3221: (DG_TIER, Start, (CogQuest, ToontownGlobals.DaisyGardens, 10, Any), 5222, Same, 100, NA, TTLocalizer.QuestDialogDict[3221]),
    3222: (DG_TIER, Start, (BuildingQuest, Anywhere, 1, Any, 1, 0), ToonHQ, ToonHQ, NA, 3223, TTLocalizer.QuestDialogDict[3222]),
    3223: (DG_TIER, Cont, (BuildingQuest, Anywhere, 1, Any, 2, 0), Same, Same, NA, 3224, TTLocalizer.QuestDialogDict[3223]),
    3224: (DG_TIER, Cont, (BuildingQuest, Anywhere, 1, Any, 3, 0), Same, Same, 501, NA, TTLocalizer.QuestDialogDict[3224]),
    3225: (DG_TIER, Start, (VisitQuest,), Any, 5108, NA, (3226, 3227, 3228, 3229, 3230, 3231, 3232, 3233, 3234), TTLocalizer.QuestDialogDict[3225]),
    3226: (DG_TIER, Start, (DeliverItemQuest, 5011), 5108, 5201, NA, 3235, TTLocalizer.QuestDialog_3225),
    3227: (DG_TIER, Start, (DeliverItemQuest, 5011), 5108, 5203, NA, 3235, TTLocalizer.QuestDialog_3225),
    3228: (DG_TIER, Start, (DeliverItemQuest, 5011), 5108, 5204, NA, 3235, TTLocalizer.QuestDialog_3225),
    3229: (DG_TIER, Start, (DeliverItemQuest, 5011), 5108, 5205, NA, 3235, TTLocalizer.QuestDialog_3225),
    3230: (DG_TIER, Start, (DeliverItemQuest, 5011), 5108, 5102, NA, 3235, TTLocalizer.QuestDialog_3225),
    3231: (DG_TIER, Start, (DeliverItemQuest, 5011), 5108, 5103, NA, 3235, TTLocalizer.QuestDialog_3225),
    3232: (DG_TIER, Start, (DeliverItemQuest, 5011), 5108, 5104, NA, 3235, TTLocalizer.QuestDialog_3225),
    3233: (DG_TIER, Start, (DeliverItemQuest, 5011), 5108, 5105, NA, 3235, TTLocalizer.QuestDialog_3225),
    3234: (DG_TIER, Start, (DeliverItemQuest, 5011), 5108, 5207, NA, 3235, TTLocalizer.QuestDialog_3225),
    3235: (DG_TIER, Cont, (CogQuest, ToontownGlobals.DaisyGardens, 7, Any), Same, 5108, 100, NA, TTLocalizer.QuestDialogDict[3235]),
    3238: (DG_TIER, Start, (RecoverItemQuest, Anywhere, 1, 2, VeryEasy, 'm'), Any, ToonHQ, NA, 3239, TTLocalizer.QuestDialogDict[3238]),
    3239: (DG_TIER, Cont, (RecoverItemQuest, Anywhere, 1, 5012, Medium, 'm'), Same, Same, 302, NA, TTLocalizer.QuestDialogDict[3239]),
    3242: (DG_TIER, Start, (RecoverItemQuest, Anywhere, 1, 2, VeryEasy, 'le'), Any, ToonHQ, NA, 3243, TTLocalizer.QuestDialogDict[3242]),
    3243: (DG_TIER, Cont, (RecoverItemQuest, Anywhere, 1, 5012, Hard, 'le'), Same, Same, 302, NA, TTLocalizer.QuestDialogDict[3243]),
    3250: (DG_TIER, Start, (VisitQuest,), Any, 5317, NA, 3251, TTLocalizer.QuestDialogDict[3250]),
    3251: (DG_TIER, Start, (CogTrackQuest, ToontownGlobals.SellbotHQ, 3, 's'), 5317, Same, NA, 3252, TTLocalizer.QuestDialogDict[3251]),
    3252: (DG_TIER, Cont, (VisitQuest,), Same, 5311, NA, 3253, TTLocalizer.QuestDialogDict[3252]),
    3253: (DG_TIER, Cont, (RecoverItemQuest, ToontownGlobals.SellbotHQ, 1, 5013, Medium, 's', 'track'), Same, Same, NA, 3254, TTLocalizer.QuestDialogDict[3253]),
    3254: (DG_TIER, Cont, (DeliverItemQuest, 5013), Same, 5317, 202, NA, TTLocalizer.QuestDialogDict[3254]),
    3255: (DG_TIER, Start, (VisitQuest,), Any, 5314, NA, 3258, TTLocalizer.QuestDialogDict[3255]),
    3256: (DG_TIER, Start, (VisitQuest,), Any, 5315, NA, 3258, TTLocalizer.QuestDialogDict[3256]),
    3257: (DG_TIER, Start, (VisitQuest,), Any, 5316, NA, 3258, TTLocalizer.QuestDialogDict[3257]),
    3258: (DG_TIER, Cont, (RecoverItemQuest, ToontownGlobals.SellbotHQ, 1, 5014, VeryEasy, 's', 'track'), Same, Same, NA, 3261, TTLocalizer.QuestDialogDict[3258]),
    3261: (DG_TIER, Cont, (RecoverItemQuest, ToontownGlobals.SellbotHQ, 1, 5017, Medium, 's', 'track'), Same, Same, 102, NA, TTLocalizer.QuestDialogDict[3261]),
    3262: (DG_TIER, Start, (VisitQuest,), Any, 5313, NA, 3263, TTLocalizer.QuestDialogDict[3262]),
    3263: (DG_TIER, Start, (FactoryQuest, ToontownGlobals.SellbotHQ, 1), 5319, 5319, 702, NA, TTLocalizer.QuestDialogDict[3263]),
    3500: (DG_TIER, Start, (CogQuest, ToontownGlobals.DaisyGardens, 20, Any), Any, ToonHQ, NA, 3501, DefaultDialog),
    3501: (DG_TIER, Cont, (DeliverItemQuest, 1000), Any, 5007, 1000, NA, DefaultDialog),
    3502: (DG_TIER, Start, (RescueQuest, InVP, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    3503: (DG_TIER, Start, (RescueQuest, InFO, 2), Any, ToonHQ, Any, NA, DefaultDialog),
    4001: (MM_TIER, Start, (TrackChoiceQuest, ToontownBattleGlobals.HEAL_TRACK, ToontownBattleGlobals.LURE_TRACK), Any, ToonHQ, 400, NA, TTLocalizer.QuestDialogDict[4001]),
    4002: (MM_TIER, Start, (TrackChoiceQuest, ToontownBattleGlobals.HEAL_TRACK, ToontownBattleGlobals.TRAP_TRACK), Any, ToonHQ, 400, NA, TTLocalizer.QuestDialogDict[4002]),
    4003: (MM_TIER, Start, (TrackChoiceQuest, ToontownBattleGlobals.SOUND_TRACK, ToontownBattleGlobals.LURE_TRACK), Any, ToonHQ, 400, NA, TTLocalizer.QuestDialogDict[4002]),
    4004: (MM_TIER, Start, (TrackChoiceQuest, ToontownBattleGlobals.SOUND_TRACK, ToontownBattleGlobals.TRAP_TRACK), Any, ToonHQ, 400, NA, TTLocalizer.QuestDialogDict[4002]),
    4010: (MM_TIER, Start, (CogQuest, Anywhere, 12, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4011: (MM_TIER, Start, (CogQuest, Anywhere, 14, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4012: (MM_TIER, Start, (CogQuest, Anywhere, 15, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4013: (MM_TIER, Start, (CogQuest, Anywhere, 18, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4014: (MM_TIER, Start, (CogQuest, Anywhere, 20, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4015: (MM_TIER, Start, (CogQuest, Anywhere, 22, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4016: (MM_TIER, Start, (CogQuest, Anywhere, 24, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4017: (MM_TIER, Start, (CogQuest, Anywhere, 25, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4018: (MM_TIER, Start, (CogQuest, Anywhere, 28, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4019: (MM_TIER, Start, (CogQuest, Anywhere, 30, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4020: (MM_TIER, Start, (CogLevelQuest, Anywhere, 15, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    4021: (MM_TIER, Start, (CogLevelQuest, Anywhere, 20, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    4022: (MM_TIER, Start, (CogLevelQuest, Anywhere, 12, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    4023: (MM_TIER, Start, (CogLevelQuest, Anywhere, 14, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    4024: (MM_TIER, Start, (CogLevelQuest, Anywhere, 10, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    4025: (MM_TIER, Start, (CogLevelQuest, Anywhere, 12, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    4026: (MM_TIER, Start, (CogLevelQuest, Anywhere, 10, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    4027: (MM_TIER, Start, (CogLevelQuest, Anywhere, 12, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    4028: (MM_TIER, Start, (CogLevelQuest, Anywhere, 14, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    4029: (MM_TIER, Start, (CogLevelQuest, Anywhere, 15, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    4030: (MM_TIER, Start, (CogQuest, Anywhere, 35, Any), Any, ToonHQ, NA, 4031, DefaultDialog),
    4031: (MM_TIER, Cont, (DeliverItemQuest, 1000), Any, 4008, 1000, NA, DefaultDialog),
    4040: (MM_TIER, Start, (CogQuest, ToontownGlobals.SellbotHQ, 4, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4041: (MM_TIER, Start, (CogQuest, ToontownGlobals.SellbotHQ, 4, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4042: (MM_TIER, Start, (CogLevelQuest, ToontownGlobals.SellbotHQ, 2	, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    4043: (MM_TIER, Start, (SkelecogQuest, ToontownGlobals.SellbotFactoryInt, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    4044: (MM_TIER, Start, (RescueQuest, InVP, 2), Any, ToonHQ, Any, NA, DefaultDialog),
    4045: (MM_TIER, Start, (RescueQuest, InFO, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    4101: (MM_TIER + 1, Start, (CogQuest, ToontownGlobals.MinniesMelodyland, 10, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4102: (MM_TIER + 1, Start, (CogQuest, ToontownGlobals.MinniesMelodyland, 12, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4103: (MM_TIER + 1, Start, (CogQuest, ToontownGlobals.MinniesMelodyland, 16, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4104: (MM_TIER + 1, Start, (CogQuest, ToontownGlobals.MinniesMelodyland, 20, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4105: (MM_TIER + 1, Start, (CogQuest, Anywhere, 20, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4106: (MM_TIER + 1, Start, (CogQuest, Anywhere, 25, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4107: (MM_TIER + 1, Start, (CogQuest, Anywhere, 10, 'f'), Any, ToonHQ, Any, NA, DefaultDialog),
    4108: (MM_TIER + 1, Start, (CogQuest, Anywhere, 10, 'p'), Any, ToonHQ, Any, NA, DefaultDialog),
    4109: (MM_TIER + 1, Start, (CogQuest, Anywhere, 10, 'ym'), Any, ToonHQ, Any, NA, DefaultDialog),
    4110: (MM_TIER + 1, Start, (CogQuest, Anywhere, 10, 'mm'), Any, ToonHQ, Any, NA, DefaultDialog),
    4111: (MM_TIER + 1, Start, (CogQuest, Anywhere, 10, 'ds'), Any, ToonHQ, Any, NA, DefaultDialog),
    4112: (MM_TIER + 1, Start, (CogQuest, Anywhere, 10, 'hh'), Any, ToonHQ, Any, NA, DefaultDialog),
    4113: (MM_TIER + 1, Start, (CogQuest, Anywhere, 15, 'cc'), Any, ToonHQ, Any, NA, DefaultDialog),
    4114: (MM_TIER + 1, Start, (CogQuest, Anywhere, 12, 'tm'), Any, ToonHQ, Any, NA, DefaultDialog),
    4115: (MM_TIER + 1, Start, (CogQuest, Anywhere, 12, 'nd'), Any, ToonHQ, Any, NA, DefaultDialog),
    4116: (MM_TIER + 1, Start, (CogQuest, Anywhere, 10, 'gh'), Any, ToonHQ, Any, NA, DefaultDialog),
    4117: (MM_TIER + 1, Start, (CogQuest, Anywhere, 10, 'ms'), None, ToonHQ, Any, NA, DefaultDialog),
    4118: (MM_TIER + 1, Start, (CogQuest, Anywhere, 10, 'tf'), None, ToonHQ, Any, NA, DefaultDialog),
    4119: (MM_TIER + 1, Start, (CogQuest, Anywhere, 15, 'sc'), Any, ToonHQ, Any, NA, DefaultDialog),
    4120: (MM_TIER + 1, Start, (CogQuest, Anywhere, 12, 'pp'), Any, ToonHQ, Any, NA, DefaultDialog),
    4121: (MM_TIER + 1, Start, (CogQuest, Anywhere, 12, 'tw'), Any, ToonHQ, Any, NA, DefaultDialog),
    4122: (MM_TIER + 1, Start, (CogQuest, Anywhere, 10, 'bc'), Any, ToonHQ, Any, NA, DefaultDialog),
    4123: (MM_TIER + 1, Start, (CogQuest, Anywhere, 10, 'nc'), Any, ToonHQ, Any, NA, DefaultDialog),
    4124: (MM_TIER + 1, Start, (CogQuest, Anywhere, 10, 'mb'), Any, ToonHQ, Any, NA, DefaultDialog),
    4125: (MM_TIER + 1, Start, (CogQuest, Anywhere, 15, 'bf'), Any, ToonHQ, Any, NA, DefaultDialog),
    4126: (MM_TIER + 1, Start, (CogQuest, Anywhere, 12, 'b'), Any, ToonHQ, Any, NA, DefaultDialog),
    4127: (MM_TIER + 1, Start, (CogQuest, Anywhere, 12, 'dt'), Any, ToonHQ, Any, NA, DefaultDialog),
    4128: (MM_TIER + 1, Start, (CogQuest, Anywhere, 10, 'ac'), Any, ToonHQ, Any, NA, DefaultDialog),
    4129: (MM_TIER + 1, Start, (CogQuest, Anywhere, 10, 'bs'), Any, ToonHQ, Any, NA, DefaultDialog),
    4130: (MM_TIER + 1, Start, (CogQuest, Anywhere, 10, 'sd'), Any, ToonHQ, Any, NA, DefaultDialog),
    4131: (MM_TIER + 1, Start, (CogLevelQuest, Anywhere, 10, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    4132: (MM_TIER + 1, Start, (CogLevelQuest, Anywhere, 15, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    4133: (MM_TIER + 1, Start, (CogLevelQuest, Anywhere, 10, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    4134: (MM_TIER + 1, Start, (CogLevelQuest, Anywhere, 10, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    4135: (MM_TIER + 1, Start, (CogLevelQuest, Anywhere, 7, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    4136: (MM_TIER + 1, Start, (CogLevelQuest, Anywhere, 12, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    4137: (MM_TIER + 1, Start, (CogLevelQuest, Anywhere, 10, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    4138: (MM_TIER + 1, Start, (CogLevelQuest, Anywhere, 14, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    4139: (MM_TIER + 1, Start, (CogTrackQuest, ToontownGlobals.MinniesMelodyland, 10, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    4140: (MM_TIER + 1, Start, (CogTrackQuest, ToontownGlobals.MinniesMelodyland, 10, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    4141: (MM_TIER + 1, Start, (CogTrackQuest, ToontownGlobals.MinniesMelodyland, 10, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    4142: (MM_TIER + 1, Start, (CogTrackQuest, ToontownGlobals.MinniesMelodyland, 10, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    4143: (MM_TIER + 1, Start, (CogTrackQuest, ToontownGlobals.MinniesMelodyland, 14, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    4144: (MM_TIER + 1, Start, (CogTrackQuest, ToontownGlobals.MinniesMelodyland, 14, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    4145: (MM_TIER + 1, Start, (CogTrackQuest, ToontownGlobals.MinniesMelodyland, 14, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    4146: (MM_TIER + 1, Start, (CogTrackQuest, ToontownGlobals.MinniesMelodyland, 14, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    4147: (MM_TIER + 1, Start, (CogTrackQuest, Anywhere, 20, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    4148: (MM_TIER + 1, Start, (CogTrackQuest, Anywhere, 20, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    4149: (MM_TIER + 1, Start, (CogTrackQuest, Anywhere, 20, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    4150: (MM_TIER + 1, Start, (CogTrackQuest, Anywhere, 20, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    4151: (MM_TIER + 1, Start, (BuildingQuest, Anywhere, 1, Any, 2, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    4152: (MM_TIER + 1, Start, (BuildingQuest, Anywhere, 2, Any, 2, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    4153: (MM_TIER + 1, Start, (BuildingQuest, Anywhere, 2, Any, 2, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    4154: (MM_TIER + 1, Start, (BuildingQuest, Anywhere, 2, Any, 2, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    4155: (MM_TIER + 1, Start, (BuildingQuest, Anywhere, 2, 'm', 3, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    4156: (MM_TIER + 1, Start, (BuildingQuest, Anywhere, 2, 's', 3, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    4157: (MM_TIER + 1, Start, (BuildingQuest, Anywhere, 2, 'c', 3, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    4158: (MM_TIER + 1, Start, (BuildingQuest, Anywhere, 2, 'l', 3, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    4160: (MM_TIER + 1, Start, (CogQuest, ToontownGlobals.SellbotHQ, 7, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4161: (MM_TIER + 1, Start, (CogQuest, ToontownGlobals.SellbotHQ, 10, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4162: (MM_TIER + 1, Start, (CogLevelQuest, ToontownGlobals.SellbotHQ, 4, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    4163: (MM_TIER + 1, Start, (FactoryQuest, ToontownGlobals.SellbotHQ, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    4164: (MM_TIER + 1, Start, (FactoryQuest, ToontownGlobals.SellbotHQ, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    4165: (MM_TIER + 1, Start, (SkelecogQuest, ToontownGlobals.SellbotFactoryInt, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    4166: (MM_TIER + 1, Start, (ForemanQuest, ToontownGlobals.SellbotHQ, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    4200: (MM_TIER + 1, Start, (VisitQuest,), Any, 4101, NA, 4201, TTLocalizer.QuestDialogDict[4200]),
    4201: (MM_TIER + 1, Start, (VisitQuest,), 4101, 4201, NA, 4202, TTLocalizer.QuestDialogDict[4201]),
    4202: (MM_TIER + 1, Cont, (DeliverItemQuest, 4001), Same, 4101, NA, 4203, TTLocalizer.QuestDialogDict[4202]),
    4203: (MM_TIER + 1, Cont, (VisitQuest,), Same, 4301, NA, 4204, TTLocalizer.QuestDialogDict[4203]),
    4204: (MM_TIER + 1, Cont, (CogQuest, ToontownGlobals.MinniesMelodyland, 7, Any), Same, Same, NA, 4205, TTLocalizer.QuestDialogDict[4204]),
    4205: (MM_TIER + 1, Cont, (DeliverItemQuest, 4002), Same, 4101, NA, 4206, TTLocalizer.QuestDialogDict[4205]),
    4206: (MM_TIER + 1, Cont, (VisitQuest,), Same, 4102, NA, 4207, TTLocalizer.QuestDialogDict[4206]),
    4207: (MM_TIER + 1, Cont, (VisitQuest,), Same, 4108, NA, 4209, TTLocalizer.QuestDialogDict[4207]),
    4209: (MM_TIER + 1, Cont, (DeliverItemQuest, 4003), Same, 4102, NA, 4210, TTLocalizer.QuestDialogDict[4209]),
    4210: (MM_TIER + 1, Cont, (DeliverItemQuest, 4004), Same, 4101, 203, NA, TTLocalizer.QuestDialogDict[4210]),
    4211: (MM_TIER + 1, Start, (VisitQuest,), ToonHQ, 4103, NA, 4212, TTLocalizer.QuestDialogDict[4211]),
    4212: (MM_TIER + 1, Start, (CogQuest, ToontownGlobals.MinniesMelodyland, 5, 'nc'), 4103, Same, NA, 4213, TTLocalizer.QuestDialogDict[4212]),
    4213: (MM_TIER + 1, Cont, (CogTrackQuest, ToontownGlobals.MinniesMelodyland, 10, 'm'), Same, Same, NA, 4214, TTLocalizer.QuestDialogDict[4213]),
    4214: (MM_TIER + 1, Cont, (BuildingQuest, Anywhere, 1, 'm', Any, 0), Same, Same, 303, NA, TTLocalizer.QuestDialogDict[4214]),
    4215: (MM_TIER + 1, Start, (VisitQuest,), Any, 4302, NA, 4216, TTLocalizer.QuestDialogDict[4215]),
    4216: (MM_TIER + 1, Start, (RecoverItemQuest, Anywhere, 1, 4005, Medium, 'gh'), 4302, Same, NA, 4217, TTLocalizer.QuestDialogDict[4216]),
    4217: (MM_TIER + 1, Cont, (DeliverItemQuest, 4005), Same, 4203, NA, 4221, TTLocalizer.QuestDialogDict[4217]),
    4221: (MM_TIER + 1, Cont, (VisitQuest,), Any, 4302, NA, 4222, TTLocalizer.QuestDialogDict[4221]),
    4222: (MM_TIER + 1, Cont, (RecoverItemQuest, Anywhere, 1, 4007, Medium, 'gh'), Same, Same, NA, 4223, TTLocalizer.QuestDialogDict[4222]),
    4223: (MM_TIER + 1, Cont, (DeliverItemQuest, 4007), Same, 4202, NA, 4224, TTLocalizer.QuestDialogDict[4223]),
    4224: (MM_TIER + 1, Cont, (VisitQuest,), Any, 4302, 703, NA, TTLocalizer.QuestDialogDict[4224]),
    4500: (MM_TIER + 1, Start, (CogQuest, ToontownGlobals.MinniesMelodyland, 25, Any), Any, ToonHQ, NA, 4501, DefaultDialog),
    4501: (MM_TIER + 1, Cont, (DeliverItemQuest, 1000), Any, 4008, 1000, NA, DefaultDialog),
    4502: (MM_TIER + 1, Start, (RescueQuest, InVP, 2), Any, ToonHQ, Any, NA, DefaultDialog),
    4503: (MM_TIER + 1, Start, (RescueQuest, InFO, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    902: (MM_TIER + 2, Start, (VisitQuest,), Any, 4303, NA, 4903, TTLocalizer.QuestDialogDict[902]),
    4903: (MM_TIER + 2, Start, (DeliverItemQuest, 4008), 4303, 4136, NA, 4904, TTLocalizer.QuestDialogDict[4903]),
    4904: (MM_TIER + 2, Cont, (RecoverItemQuest, Anywhere, 1, 4009, Medium, AnyFish), Same, Same, NA, 4905, TTLocalizer.QuestDialogDict[4904]),
    4905: (MM_TIER + 2, Cont, (BuildingQuest, Anywhere, 1, Any, 1, 0), Same, Same, NA, 4906, TTLocalizer.QuestDialogDict[4905]),
    4906: (MM_TIER + 2, Cont, (DeliverItemQuest, 4010), Same, 4303, NA, 4907, TTLocalizer.QuestDialogDict[4906]),
    4907: (MM_TIER + 2, Cont, (VisitQuest,), Same, 4333, NA, 4908, TTLocalizer.QuestDialogDict[4907]),
    4908: (MM_TIER + 2, Cont, (BuildingQuest, Anywhere, 1, Any, 2, 0), Same, Same, NA, 4909, TTLocalizer.QuestDialogDict[4908]),
    4909: (MM_TIER + 2, Cont, (BuildingQuest, Anywhere, 1, Any, 3, 0), Same, Same, NA, 4910, TTLocalizer.QuestDialogDict[4909]),
    4910: (MM_TIER + 2, Cont, (DeliverItemQuest, 4011), Same, 4303, 900, NA, TTLocalizer.QuestDialogDict[4910]),
    4810: (MM_TIER + 2, Start, (CogQuest, Anywhere, 12, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4811: (MM_TIER + 2, Start, (CogQuest, Anywhere, 14, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4812: (MM_TIER + 2, Start, (CogQuest, Anywhere, 15, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4813: (MM_TIER + 2, Start, (CogQuest, Anywhere, 15, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4814: (MM_TIER + 2, Start, (CogQuest, Anywhere, 20, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4815: (MM_TIER + 2, Start, (CogQuest, Anywhere, 20, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4816: (MM_TIER + 2, Start, (CogQuest, Anywhere, 22, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4817: (MM_TIER + 2, Start, (CogQuest, Anywhere, 25, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4818: (MM_TIER + 2, Start, (CogQuest, Anywhere, 25, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4819: (MM_TIER + 2, Start, (CogQuest, Anywhere, 30, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4820: (MM_TIER + 2, Start, (CogLevelQuest, Anywhere, 10, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    4821: (MM_TIER + 2, Start, (CogLevelQuest, Anywhere, 15, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    4822: (MM_TIER + 2, Start, (CogLevelQuest, Anywhere, 10, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    4823: (MM_TIER + 2, Start, (CogLevelQuest, Anywhere, 12, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    4824: (MM_TIER + 2, Start, (CogLevelQuest, Anywhere, 10, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    4825: (MM_TIER + 2, Start, (CogLevelQuest, Anywhere, 15, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    4826: (MM_TIER + 2, Start, (CogLevelQuest, Anywhere, 10, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    4827: (MM_TIER + 2, Start, (CogLevelQuest, Anywhere, 12, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    4828: (MM_TIER + 2, Start, (CogLevelQuest, Anywhere, 15, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    4829: (MM_TIER + 2, Start, (CogLevelQuest, Anywhere, 20, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    4830: (MM_TIER + 2, Start, (CogQuest, Anywhere, 40, Any), Any, ToonHQ, NA, 4831, DefaultDialog),
    4831: (MM_TIER + 2, Cont, (DeliverItemQuest, 1000), Any, 4008, 1000, NA, DefaultDialog),
    4840: (MM_TIER + 2, Start, (CogQuest, ToontownGlobals.SellbotHQ, 10, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4841: (MM_TIER + 2, Start, (CogQuest, ToontownGlobals.SellbotHQ, 10, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    4842: (MM_TIER + 2, Start, (CogLevelQuest, ToontownGlobals.SellbotHQ, 10, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    4843: (MM_TIER + 2, Start, (CogLevelQuest, ToontownGlobals.SellbotFactoryInt, 5, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    4844: (MM_TIER + 2, Start, (FactoryQuest, ToontownGlobals.SellbotHQ, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    4845: (MM_TIER + 2, Start, (FactoryQuest, ToontownGlobals.SellbotHQ, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    4846: (MM_TIER + 2, Start, (SkelecogQuest, ToontownGlobals.SellbotFactoryInt, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    4847: (MM_TIER + 2, Start, (SkelecogLevelQuest, ToontownGlobals.SellbotHQ, 3, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    4848: (MM_TIER + 2, Start, (ForemanQuest, ToontownGlobals.SellbotHQ, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    4849: (MM_TIER + 2, Start, (RescueQuest, InVP, 2), Any, ToonHQ, Any, NA, DefaultDialog),
    4850: (MM_TIER + 2, Start, (RescueQuest, InFO, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    5247: (BR_TIER, Start, (VisitQuest,), Any, 3112, NA, 5248, TTLocalizer.QuestDialogDict[5247]),
    5248: (BR_TIER, Start, (CogLevelQuest, Anywhere, 5, 7), 3112, Same, NA, 5249, TTLocalizer.QuestDialogDict[5248]),
    5249: (BR_TIER, Cont, (RecoverItemQuest, Anywhere, 3, 3018, Medium, AnyFish), Same, Same, NA, (5250, 5258, 5259, 5260), TTLocalizer.QuestDialogDict[5249]),
    5250: (BR_TIER, Cont, (BuildingQuest, Anywhere, 1, 'l', 4, 0), Same, Same, NA, (5001, 5002, 5003, 5004), TTLocalizer.QuestDialogDict[5250]),
    5258: (BR_TIER, Cont, (BuildingQuest, Anywhere, 1, 'c', 4, 0), Same, Same, NA, (5001, 5002, 5003, 5004), TTLocalizer.QuestDialogDict[5258]),
    5259: (BR_TIER, Cont, (BuildingQuest, Anywhere, 1, 'm', 4, 0), Same, Same, NA, (5001, 5002, 5003, 5004), TTLocalizer.QuestDialogDict[5259]),
    5260: (BR_TIER, Cont, (BuildingQuest, Anywhere, 1, 's', 4, 0), Same, Same, NA, (5001, 5002, 5003, 5004), TTLocalizer.QuestDialogDict[5260]),
    5001: (BR_TIER, Cont, (TrackChoiceQuest, ToontownBattleGlobals.SOUND_TRACK, ToontownBattleGlobals.SOUND_TRACK), Same, Same, 400, NA, TTLocalizer.TheBrrrghTrackQuestDict),
    5002: (BR_TIER, Cont, (TrackChoiceQuest, ToontownBattleGlobals.LURE_TRACK, ToontownBattleGlobals.LURE_TRACK), Same, Same, 400, NA, TTLocalizer.TheBrrrghTrackQuestDict),
    5003: (BR_TIER, Cont, (TrackChoiceQuest, ToontownBattleGlobals.HEAL_TRACK, ToontownBattleGlobals.HEAL_TRACK), Same, Same, 400, NA, TTLocalizer.TheBrrrghTrackQuestDict),
    5004: (BR_TIER, Cont, (TrackChoiceQuest, ToontownBattleGlobals.TRAP_TRACK, ToontownBattleGlobals.TRAP_TRACK), Same, Same, 400, NA, TTLocalizer.TheBrrrghTrackQuestDict),
    5020: (BR_TIER, Start, (CogQuest, Anywhere, 30, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5021: (BR_TIER, Start, (CogQuest, Anywhere, 32, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5022: (BR_TIER, Start, (CogQuest, Anywhere, 35, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5023: (BR_TIER, Start, (CogQuest, Anywhere, 35, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5024: (BR_TIER, Start, (CogQuest, Anywhere, 40, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5025: (BR_TIER, Start, (CogQuest, Anywhere, 40, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5026: (BR_TIER, Start, (CogQuest, Anywhere, 45, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5027: (BR_TIER, Start, (CogQuest, Anywhere, 45, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5028: (BR_TIER, Start, (CogQuest, Anywhere, 50, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5029: (BR_TIER, Start, (CogQuest, Anywhere, 50, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5030: (BR_TIER, Start, (CogLevelQuest, Anywhere, 20, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    5031: (BR_TIER, Start, (CogLevelQuest, Anywhere, 25, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    5032: (BR_TIER, Start, (CogLevelQuest, Anywhere, 30, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    5033: (BR_TIER, Start, (CogLevelQuest, Anywhere, 5, 7), Any, ToonHQ, Any, NA, DefaultDialog),
    5034: (BR_TIER, Start, (CogLevelQuest, Anywhere, 6, 7), Any, ToonHQ, Any, NA, DefaultDialog),
    5035: (BR_TIER, Start, (CogLevelQuest, Anywhere, 10, 7), Any, ToonHQ, Any, NA, DefaultDialog),
    5036: (BR_TIER, Start, (CogLevelQuest, Anywhere, 2, 8), Any, ToonHQ, Any, NA, DefaultDialog),
    5037: (BR_TIER, Start, (CogLevelQuest, Anywhere, 4, 8), Any, ToonHQ, Any, NA, DefaultDialog),
    5038: (BR_TIER, Start, (CogLevelQuest, Anywhere, 6, 8), Any, ToonHQ, Any, NA, DefaultDialog),
    5039: (BR_TIER, Start, (CogLevelQuest, Anywhere, 8, 8), Any, ToonHQ, Any, NA, DefaultDialog),
    5040: (BR_TIER, Start, (CogQuest, ToontownGlobals.TheBrrrgh, 45, Any), Any, ToonHQ, NA, 5041, DefaultDialog),
    5041: (BR_TIER, Cont, (DeliverItemQuest, 1000), Any, 3008, 1000, NA, DefaultDialog),
    5070: (BR_TIER, Start, (CogQuest, ToontownGlobals.SellbotHQ, 10, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5071: (BR_TIER, Start, (CogQuest, ToontownGlobals.SellbotHQ, 12, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5072: (BR_TIER, Start, (CogLevelQuest, ToontownGlobals.SellbotHQ, 10, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    5073: (BR_TIER, Start, (CogLevelQuest, ToontownGlobals.SellbotHQ, 8, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    5074: (BR_TIER, Start, (CogLevelQuest, ToontownGlobals.SellbotFactoryInt, 10, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    5075: (BR_TIER, Start, (CogLevelQuest, ToontownGlobals.SellbotFactoryInt, 6, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    5076: (BR_TIER, Start, (FactoryQuest, ToontownGlobals.SellbotHQ, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    5077: (BR_TIER, Start, (FactoryQuest, ToontownGlobals.SellbotHQ, 2), Any, ToonHQ, Any, NA, DefaultDialog),
    5078: (BR_TIER, Start, (FactoryQuest, ToontownGlobals.SellbotHQ, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    5079: (BR_TIER, Start, (FactoryQuest, ToontownGlobals.SellbotHQ, 2), Any, ToonHQ, Any, NA, DefaultDialog),
    5080: (BR_TIER, Start, (SkelecogQuest, ToontownGlobals.SellbotFactoryInt, 8), Any, ToonHQ, Any, NA, DefaultDialog),
    5081: (BR_TIER, Start, (SkelecogLevelQuest, ToontownGlobals.SellbotHQ, 4, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    5082: (BR_TIER, Start, (SkelecogLevelQuest, ToontownGlobals.SellbotHQ, 2, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    5083: (BR_TIER, Start, (ForemanQuest, ToontownGlobals.SellbotHQ, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    5084: (BR_TIER, Start, (ForemanQuest, ToontownGlobals.SellbotHQ, 2), Any, ToonHQ, Any, NA, DefaultDialog),
    5085: (BR_TIER, Start, (RescueQuest, InVP, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    5086: (BR_TIER, Start, (RescueQuest, InFO, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    5101: (BR_TIER + 1, Start, (CogQuest, ToontownGlobals.TheBrrrgh, 30, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5102: (BR_TIER + 1, Start, (CogQuest, ToontownGlobals.TheBrrrgh, 35, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5103: (BR_TIER + 1, Start, (CogQuest, ToontownGlobals.TheBrrrgh, 35, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5104: (BR_TIER + 1, Start, (CogQuest, Anywhere, 35, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5105: (BR_TIER + 1, Start, (CogQuest, Anywhere, 40, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5106: (BR_TIER + 1, Start, (CogQuest, Anywhere, 45, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5107: (BR_TIER + 1, Start, (CogQuest, Anywhere, 20, 'p'), Any, ToonHQ, Any, NA, DefaultDialog),
    5108: (BR_TIER + 1, Start, (CogQuest, Anywhere, 15, 'ym'), Any, ToonHQ, Any, NA, DefaultDialog),
    5109: (BR_TIER + 1, Start, (CogQuest, Anywhere, 15, 'mm'), Any, ToonHQ, Any, NA, DefaultDialog),
    5110: (BR_TIER + 1, Start, (CogQuest, Anywhere, 10, 'ds'), Any, ToonHQ, Any, NA, DefaultDialog),
    5111: (BR_TIER + 1, Start, (CogQuest, Anywhere, 10, 'hh'), Any, ToonHQ, Any, NA, DefaultDialog),
    5112: (BR_TIER + 1, Start, (CogQuest, Anywhere, 4, 'cr'), Any, ToonHQ, Any, NA, DefaultDialog),
    5113: (BR_TIER + 1, Start, (CogQuest, Anywhere, 20, 'tm'), Any, ToonHQ, Any, NA, DefaultDialog),
    5114: (BR_TIER + 1, Start, (CogQuest, Anywhere, 15, 'nd'), Any, ToonHQ, Any, NA, DefaultDialog),
    5115: (BR_TIER + 1, Start, (CogQuest, Anywhere, 15, 'gh'), Any, ToonHQ, Any, NA, DefaultDialog),
    5116: (BR_TIER + 1, Start, (CogQuest, Anywhere, 10, 'ms'), Any, ToonHQ, Any, NA, DefaultDialog),
    5117: (BR_TIER + 1, Start, (CogQuest, Anywhere, 10, 'tf'), Any, ToonHQ, Any, NA, DefaultDialog),
    5118: (BR_TIER + 1, Start, (CogQuest, Anywhere, 6, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    5119: (BR_TIER + 1, Start, (CogQuest, Anywhere, 20, 'pp'), Any, ToonHQ, Any, NA, DefaultDialog),
    5120: (BR_TIER + 1, Start, (CogQuest, Anywhere, 15, 'tw'), Any, ToonHQ, Any, NA, DefaultDialog),
    5121: (BR_TIER + 1, Start, (CogQuest, Anywhere, 15, 'bc'), Any, ToonHQ, Any, NA, DefaultDialog),
    5122: (BR_TIER + 1, Start, (CogQuest, Anywhere, 10, 'nc'), Any, ToonHQ, Any, NA, DefaultDialog),
    5123: (BR_TIER + 1, Start, (CogQuest, Anywhere, 10, 'mb'), Any, ToonHQ, Any, NA, DefaultDialog),
    5124: (BR_TIER + 1, Start, (CogQuest, Anywhere, 4, 'ls'), Any, ToonHQ, Any, NA, DefaultDialog),
    5125: (BR_TIER + 1, Start, (CogQuest, Anywhere, 20, 'b'), Any, ToonHQ, Any, NA, DefaultDialog),
    5126: (BR_TIER + 1, Start, (CogQuest, Anywhere, 15, 'dt'), Any, ToonHQ, Any, NA, DefaultDialog),
    5127: (BR_TIER + 1, Start, (CogQuest, Anywhere, 15, 'ac'), Any, ToonHQ, Any, NA, DefaultDialog),
    5128: (BR_TIER + 1, Start, (CogQuest, Anywhere, 10, 'bs'), Any, ToonHQ, Any, NA, DefaultDialog),
    5129: (BR_TIER + 1, Start, (CogQuest, Anywhere, 10, 'sd'), Any, ToonHQ, Any, NA, DefaultDialog),
    5130: (BR_TIER + 1, Start, (CogQuest, Anywhere, 4, 'le'), Any, ToonHQ, Any, NA, DefaultDialog),
    5131: (BR_TIER + 1, Start, (CogLevelQuest, Anywhere, 15, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    5132: (BR_TIER + 1, Start, (CogLevelQuest, Anywhere, 20, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    5133: (BR_TIER + 1, Start, (CogLevelQuest, Anywhere, 12, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    5134: (BR_TIER + 1, Start, (CogLevelQuest, Anywhere, 5, 7), Any, ToonHQ, Any, NA, DefaultDialog),
    5135: (BR_TIER + 1, Start, (CogLevelQuest, Anywhere, 7, 7), Any, ToonHQ, Any, NA, DefaultDialog),
    5136: (BR_TIER + 1, Start, (CogLevelQuest, Anywhere, 15, 7), Any, ToonHQ, Any, NA, DefaultDialog),
    5137: (BR_TIER + 1, Start, (CogLevelQuest, Anywhere, 2, 8), Any, ToonHQ, Any, NA, DefaultDialog),
    5138: (BR_TIER + 1, Start, (CogLevelQuest, Anywhere, 4, 8), Any, ToonHQ, Any, NA, DefaultDialog),
    5139: (BR_TIER + 1, Start, (CogTrackQuest, ToontownGlobals.TheBrrrgh, 25, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    5140: (BR_TIER + 1, Start, (CogTrackQuest, ToontownGlobals.TheBrrrgh, 25, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    5141: (BR_TIER + 1, Start, (CogTrackQuest, ToontownGlobals.TheBrrrgh, 25, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    5142: (BR_TIER + 1, Start, (CogTrackQuest, ToontownGlobals.TheBrrrgh, 25, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    5143: (BR_TIER + 1, Start, (CogTrackQuest, ToontownGlobals.TheBrrrgh, 30, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    5144: (BR_TIER + 1, Start, (CogTrackQuest, ToontownGlobals.TheBrrrgh, 30, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    5145: (BR_TIER + 1, Start, (CogTrackQuest, ToontownGlobals.TheBrrrgh, 30, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    5146: (BR_TIER + 1, Start, (CogTrackQuest, ToontownGlobals.TheBrrrgh, 30, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    5147: (BR_TIER + 1, Start, (CogTrackQuest, Anywhere, 35, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    5148: (BR_TIER + 1, Start, (CogTrackQuest, Anywhere, 35, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    5149: (BR_TIER + 1, Start, (CogTrackQuest, Anywhere, 35, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    5150: (BR_TIER + 1, Start, (CogTrackQuest, Anywhere, 35, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    5151: (BR_TIER + 1, Start, (BuildingQuest, Anywhere, 5, Any, 3, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    5152: (BR_TIER + 1, Start, (BuildingQuest, Anywhere, 2, Any, 4, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    5153: (BR_TIER + 1, Start, (BuildingQuest, Anywhere, 3, Any, 4, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    5154: (BR_TIER + 1, Start, (BuildingQuest, Anywhere, 4, Any, 4, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    5155: (BR_TIER + 1, Start, (BuildingQuest, Anywhere, 2, 'm', 4, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    5156: (BR_TIER + 1, Start, (BuildingQuest, Anywhere, 2, 's', 4, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    5157: (BR_TIER + 1, Start, (BuildingQuest, Anywhere, 2, 'c', 4, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    5158: (BR_TIER + 1, Start, (BuildingQuest, Anywhere, 2, 'l', 4, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    5160: (BR_TIER + 1, Start, (CogQuest, ToontownGlobals.SellbotHQ, 15, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5161: (BR_TIER + 1, Start, (CogQuest, ToontownGlobals.SellbotHQ, 20, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5162: (BR_TIER + 1, Start, (CogLevelQuest, ToontownGlobals.SellbotHQ, 10, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    5163: (BR_TIER + 1, Start, (CogLevelQuest, ToontownGlobals.SellbotHQ, 10, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    5164: (BR_TIER + 1, Start, (CogLevelQuest, ToontownGlobals.SellbotFactoryInt, 10, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    5165: (BR_TIER + 1, Start, (CogLevelQuest, ToontownGlobals.SellbotFactoryInt, 7, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    5166: (BR_TIER + 1, Start, (FactoryQuest, ToontownGlobals.SellbotHQ, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    5167: (BR_TIER + 1, Start, (FactoryQuest, ToontownGlobals.SellbotHQ, 2), Any, ToonHQ, Any, NA, DefaultDialog),
    5168: (BR_TIER + 1, Start, (FactoryQuest, ToontownGlobals.SellbotHQ, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    5169: (BR_TIER + 1, Start, (FactoryQuest, ToontownGlobals.SellbotHQ, 2), Any, ToonHQ, Any, NA, DefaultDialog),
    5170: (BR_TIER + 1, Start, (SkelecogQuest, ToontownGlobals.SellbotFactoryInt, 10), Any, ToonHQ, Any, NA, DefaultDialog),
    5171: (BR_TIER + 1, Start, (SkelecogLevelQuest, ToontownGlobals.SellbotHQ, 4, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    5172: (BR_TIER + 1, Start, (SkelecogLevelQuest, ToontownGlobals.SellbotHQ, 3, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    5173: (BR_TIER + 1, Start, (ForemanQuest, ToontownGlobals.SellbotHQ, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    5174: (BR_TIER + 1, Start, (ForemanQuest, ToontownGlobals.SellbotHQ, 2), Any, ToonHQ, Any, NA, DefaultDialog),
    5200: (BR_TIER + 1, Start, (VisitQuest,), Any, 3110, NA, (5201, 5261, 5262, 5263), TTLocalizer.QuestDialogDict[5200]),
    5201: (BR_TIER + 1, Start, (RecoverItemQuest, Anywhere, 1, 3001, Hard, 'hh'), 3110, Same, 100, NA, TTLocalizer.QuestDialogDict[5201]),
    5261: (BR_TIER + 1, Start, (RecoverItemQuest, Anywhere, 1, 3001, Hard, 'tf'), 3110, Same, 100, NA, TTLocalizer.QuestDialogDict[5261]),
    5262: (BR_TIER + 1, Start, (RecoverItemQuest, Anywhere, 1, 3001, Hard, 'mb'), 3110, Same, 100, NA, TTLocalizer.QuestDialogDict[5262]),
    5263: (BR_TIER + 1, Start, (RecoverItemQuest, Anywhere, 1, 3001, Hard, 'sd'), 3110, Same, 100, NA, TTLocalizer.QuestDialogDict[5263]),
    5202: (BR_TIER + 1, Start, (VisitQuest,), Any, 3102, NA, 5203, TTLocalizer.QuestDialogDict[5202]),
    5203: (BR_TIER + 1, Start, (RecoverItemQuest, ToontownGlobals.TheBrrrgh, 1, 3002, VeryHard, Any), 3102, Same, NA, 5204, TTLocalizer.QuestDialogDict[5203]),
    5204: (BR_TIER + 1, Cont, (VisitQuest,), Same, 3205, NA, 5205, TTLocalizer.QuestDialogDict[5204]),
    5205: (BR_TIER + 1, Cont, (RecoverItemQuest, ToontownGlobals.TheBrrrgh, 3, 3003, Hard, AnyFish), Same, Same, NA, 5206, TTLocalizer.QuestDialogDict[5205]),
    5206: (BR_TIER + 1, Cont, (VisitQuest,), Same, 3210, NA, 5207, TTLocalizer.QuestDialogDict[5206]),
    5207: (BR_TIER + 1, Cont, (BuildingQuest, Anywhere, 3, Any, 4, 0), Same, Same, NA, 5208, TTLocalizer.QuestDialogDict[5207]),
    5208: (BR_TIER + 1, Cont, (VisitQuest,), Same, 3114, NA, 5209, TTLocalizer.QuestDialogDict[5208]),
    5209: (BR_TIER + 1, Cont, (CogLevelQuest, Anywhere, 10, 7), Same, Same, 204, NA, TTLocalizer.QuestDialogDict[5209]),
    5210: (BR_TIER + 1, Start, (VisitQuest,), Any, 3206, NA, (5211, 5264, 5265, 5266), TTLocalizer.QuestDialogDict[5210]),
    5211: (BR_TIER + 1, Start, (RecoverItemQuest, ToontownGlobals.TheBrrrgh, 1, 3004, Medium, 'le'), 3206, Same, NA, 5212, TTLocalizer.QuestDialogDict[5211]),
    5264: (BR_TIER + 1, Start, (RecoverItemQuest, ToontownGlobals.TheBrrrgh, 1, 3004, Hard, 'ls'), 3206, Same, NA, 5212, TTLocalizer.QuestDialogDict[5264]),
    5265: (BR_TIER + 1, Start, (RecoverItemQuest, ToontownGlobals.TheBrrrgh, 1, 3004, Easy, 'm'), 3206, Same, NA, 5212, TTLocalizer.QuestDialogDict[5265]),
    5266: (BR_TIER + 1, Start, (RecoverItemQuest, ToontownGlobals.TheBrrrgh, 1, 3004, Medium, 'cr'), 3206, Same, NA, 5212, TTLocalizer.QuestDialogDict[5266]),
    5212: (BR_TIER + 1, Cont, (DeliverItemQuest, 3004), Same, 3111, NA, 5213, TTLocalizer.QuestDialogDict[5212]),
    5213: (BR_TIER + 1, Cont, (RecoverItemQuest, ToontownGlobals.TheBrrrgh, 5, 3005, Hard, Any), Same, Same, NA, 5214, TTLocalizer.QuestDialogDict[5213]),
    5214: (BR_TIER + 1, Cont, (VisitQuest,), Same, 3103, NA, 5215, TTLocalizer.QuestDialogDict[5214]),
    5215: (BR_TIER + 1, Cont, (CogLevelQuest, Anywhere, 5, 8), Same, Same, NA, 5216, TTLocalizer.QuestDialogDict[5215]),
    5216: (BR_TIER + 1, Cont, (DeliverItemQuest, 3006), Same, 3206, 704, NA, TTLocalizer.QuestDialogDict[5216]),
    5217: (BR_TIER + 1, Start, (VisitQuest,), Any, 3103, NA, 5218, TTLocalizer.QuestDialogDict[5217]),
    5218: (BR_TIER + 1, Start, (CogQuest, Anywhere, 5, 'm'), 3113, Same, NA, 5219, TTLocalizer.QuestDialogDict[5218]),
    5219: (BR_TIER + 1, Cont, (CogQuest, Anywhere, 5, 'cr'), Same, Same, NA, 5220, TTLocalizer.QuestDialogDict[5219]),
    5220: (BR_TIER + 1, Cont, (CogQuest, Anywhere, 5, 'ls'), Same, Same, NA, 5221, TTLocalizer.QuestDialogDict[5220]),
    5221: (BR_TIER + 1, Cont, (VisitQuest,), Same, 3102, NA, 5222, TTLocalizer.QuestDialogDict[5221]),
    5222: (BR_TIER + 1, Cont, (RecoverItemQuest, Anywhere, 2, 3007, Hard, AnyFish), Same, Same, NA, 5223, TTLocalizer.QuestDialogDict[5222]),
    5223: (BR_TIER + 1, Cont, (DeliverItemQuest, 3008), Same, 3103, NA, 5224, TTLocalizer.QuestDialogDict[5223]),
    5224: (BR_TIER + 1, Cont, (CogQuest, Anywhere, 5, 'le'), Same, Same, 502, NA, TTLocalizer.QuestDialogDict[5224]),
    5225: (BR_TIER + 1, Start, (VisitQuest,), Any, 3106, NA, 5226, TTLocalizer.QuestDialogDict[5225]),
    5226: (BR_TIER + 1, Start, (BuildingQuest, Anywhere, 2, 'm', 4, 0), 3106, Same, NA, 5227, TTLocalizer.QuestDialogDict[5226]),
    5227: (BR_TIER + 1, Cont, (VisitQuest,), Same, 3208, NA, 5228, TTLocalizer.QuestDialogDict[5227]),
    5228: (BR_TIER + 1, Cont, (DeliverItemQuest, 3009), Same, 3207, NA, (5229, 5267, 5268, 5269), TTLocalizer.QuestDialogDict[5228]),
    5229: (BR_TIER + 1, Cont, (CogTrackQuest, ToontownGlobals.TheBrrrgh, 4, 'm'), Same, Same, NA, 5230, TTLocalizer.QuestDialogDict[5229]),
    5267: (BR_TIER + 1, Cont, (CogTrackQuest, ToontownGlobals.TheBrrrgh, 5, 's'), Same, Same, NA, 5230, TTLocalizer.QuestDialogDict[5267]),
    5268: (BR_TIER + 1, Cont, (CogTrackQuest, ToontownGlobals.TheBrrrgh, 6, 'l'), Same, Same, NA, 5230, TTLocalizer.QuestDialogDict[5268]),
    5269: (BR_TIER + 1, Cont, (CogTrackQuest, ToontownGlobals.TheBrrrgh, 6, 'c'), Same, Same, NA, (5230, 5270, 5271, 5272), TTLocalizer.QuestDialogDict[5269]),
    5230: (BR_TIER + 1, Cont, (RecoverItemQuest, Anywhere, 1, 3010, Easy, 'rb'), Same, Same, NA, 5231, TTLocalizer.QuestDialogDict[5230]),
    5270: (BR_TIER + 1, Cont, (RecoverItemQuest, Anywhere, 1, 3010, Hard, 'tbc'), Same, Same, NA, 5231, TTLocalizer.QuestDialogDict[5270]),
    5271: (BR_TIER + 1, Cont, (RecoverItemQuest, Anywhere, 1, 3010, Hard, 'mh'), Same, Same, NA, 5231, TTLocalizer.QuestDialogDict[5271]),
    5272: (BR_TIER + 1, Cont, (RecoverItemQuest, Anywhere, 1, 3010, Medium, 'bw'), Same, Same, NA, 5231, TTLocalizer.QuestDialogDict[5272]),
    5231: (BR_TIER + 1, Cont, (DeliverItemQuest, 3010), Same, 3208, NA, 5232, TTLocalizer.QuestDialogDict[5231]),
    5232: (BR_TIER + 1, Cont, (VisitQuest,), Same, 3106, NA, 5233, TTLocalizer.QuestDialogDict[5232]),
    5233: (BR_TIER + 1, Cont, (DeliverItemQuest, 3011), Same, 3208, 304, NA, TTLocalizer.QuestDialogDict[5233]),
    5243: (BR_TIER + 1, Start, (VisitQuest,), Any, 3318, NA, 5244, TTLocalizer.QuestDialogDict[5243]),
    5244: (BR_TIER + 1, Start, (RecoverItemQuest, Anywhere, 1, 2007, Hard, 'mm'), 3217, Same, NA, 5245, TTLocalizer.QuestDialogDict[5244]),
    5245: (BR_TIER + 1, Cont, (RecoverItemQuest, Anywhere, 1, 3017, Hard, AnyFish), Same, Same, NA, 5246, TTLocalizer.QuestDialogDict[5245]),
    5246: (BR_TIER + 1, Cont, (BuildingQuest, ToontownGlobals.TheBrrrgh, 3, Any, 1, 0), Same, Same, 101, NA, TTLocalizer.QuestDialogDict[5246]),
    5251: (BR_TIER + 1, Start, (VisitQuest,), Any, 3134, NA, 5252, TTLocalizer.QuestDialogDict[5251]),
    5252: (BR_TIER + 1, Start, (RecoverItemQuest, Anywhere, 1, 3019, Hard, Any), 3134, Same, NA, (5253, 5273, 5274, 5275), TTLocalizer.QuestDialogDict[5252]),
    5253: (BR_TIER + 1, Cont, (RecoverItemQuest, Anywhere, 1, 3020, Hard, 'cr'), Same, Same, NA, (5254, 5282, 5283, 5284), TTLocalizer.QuestDialogDict[5253]),
    5273: (BR_TIER + 1, Cont, (RecoverItemQuest, Anywhere, 1, 3020, Medium, 'm'), Same, Same, NA, (5254, 5282, 5283, 5284), TTLocalizer.QuestDialogDict[5273]),
    5274: (BR_TIER + 1, Cont, (RecoverItemQuest, Anywhere, 1, 3020, Hard, 'ls'), Same, Same, NA, (5254, 5282, 5283, 5284), TTLocalizer.QuestDialogDict[5274]),
    5275: (BR_TIER + 1, Cont, (RecoverItemQuest, Anywhere, 1, 3020, Hard, 'le'), Same, Same, NA, (5254, 5282, 5283, 5284), TTLocalizer.QuestDialogDict[5275]),
    5254: (BR_TIER + 1, Cont, (RecoverItemQuest, Anywhere, 1, 3021, VeryHard, 'mh'), Same, Same, 102, NA, TTLocalizer.QuestDialogDict[5254]),
    5282: (BR_TIER + 1, Cont, (RecoverItemQuest, Anywhere, 1, 3021, Hard, 'tbc'), Same, Same, 102, NA, TTLocalizer.QuestDialogDict[5282]),
    5283: (BR_TIER + 1, Cont, (RecoverItemQuest, Anywhere, 1, 3021, Medium, 'rb'), Same, Same, 102, NA, TTLocalizer.QuestDialogDict[5283]),
    5284: (BR_TIER + 1, Cont, (RecoverItemQuest, Anywhere, 1, 3021, Hard, 'bw'), Same, Same, 102, NA, TTLocalizer.QuestDialogDict[5284]),
    5255: (BR_TIER + 1, Start, (VisitQuest,), Any, 3228, NA, (5256, 5276), TTLocalizer.QuestDialogDict[5255]),
    5256: (BR_TIER + 1, Cont, (CogTrackQuest, Anywhere, 35, 'c'), 3228, Same, NA, (5257, 5277), TTLocalizer.QuestDialogDict[5256]),
    5276: (BR_TIER + 1, Cont, (CogTrackQuest, Anywhere, 30, 'l'), 3228, Same, NA, (5257, 5277), TTLocalizer.QuestDialogDict[5276]),
    5257: (BR_TIER + 1, Cont, (CogTrackQuest, Anywhere, 35, 's'), Same, Same, 100, NA, TTLocalizer.QuestDialogDict[5257]),
    5277: (BR_TIER + 1, Cont, (CogTrackQuest, Anywhere, 35, 'm'), Same, Same, 100, NA, TTLocalizer.QuestDialogDict[5277]),
    5301: (BR_TIER + 1, Start, (VisitQuest,), Any, 3304, NA, 5302, TTLocalizer.QuestDialogDict[5301]),
    5302: (BR_TIER + 1, Cont, (CogTrackQuest, Anywhere, 50, 'l'), Same, Same, 100, NA, TTLocalizer.QuestDialogDict[5302]),
    5303: (BR_TIER + 1, Start, (VisitQuest,), Any, 3318, NA, 5304, TTLocalizer.QuestDialogDict[5303]),
    5304: (BR_TIER + 1, Cont, (RecoverItemQuest, ToontownGlobals.TheBrrrgh, 1, 3024, VeryHard, 'l', 'track'), Same, Same, NA, 5305, TTLocalizer.QuestDialogDict[5304]),
    5305: (BR_TIER + 1, Cont, (CogLevelQuest, Anywhere, 10, 7), Same, Same, NA, 5306, TTLocalizer.QuestDialogDict[5305]),
    5306: (BR_TIER + 1, Cont, (RecoverItemQuest, ToontownGlobals.TheBrrrgh, 2, 3025, Hard, AnyFish), Same, Same, NA, 5307, TTLocalizer.QuestDialogDict[5306]),
    5307: (BR_TIER + 1, Cont, (BuildingQuest, Anywhere, 3, Any, 4, 0), Same, Same, 204, NA, TTLocalizer.QuestDialogDict[5307]),
    5308: (BR_TIER + 1, Start, (VisitQuest,), Any, 3302, NA, 5309, TTLocalizer.QuestDialogDict[5308]),
    5309: (BR_TIER + 1, Start, (CogTrackQuest, ToontownGlobals.PolarPlace, 15, 'l'), Same, Same, NA, 5310, TTLocalizer.QuestDialogDict[5309]),
    5310: (BR_TIER + 1, Cont, (VisitQuest,), Same, 3318, NA, 5311, TTLocalizer.QuestDialogDict[5310]),
    5311: (BR_TIER + 1, Cont, (RecoverItemQuest, Anywhere, 2, 3026, Medium, 'le'), Same, Same, NA, 5312, TTLocalizer.QuestDialogDict[5311]),
    5312: (BR_TIER + 1, Cont, (DeliverItemQuest, 3026), Same, 3312, 502, NA, TTLocalizer.QuestDialogDict[5312]),
    5500: (BR_TIER + 1, Start, (CogQuest, ToontownGlobals.TheBrrrgh, 55, Any), Any, ToonHQ, NA, 5501, DefaultDialog),
    5501: (BR_TIER + 1, Cont, (DeliverItemQuest, 1000), Any, 3008, 1000, NA, DefaultDialog),
    5502: (BR_TIER + 1, Start, (RescueQuest, InVP, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    5503: (BR_TIER + 1, Start, (RescueQuest, InFO, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    903: (BR_TIER + 2, Start, (VisitQuest,), Any, 3112, NA, (5234, 5278), TTLocalizer.QuestDialogDict[903]),
    5234: (BR_TIER + 2, Start, (RecoverItemQuest, Anywhere, 5, 3012, Medium, 'tbc'), 3112, Same, NA, (5235, 5279), TTLocalizer.QuestDialogDict[5234]),
    5278: (BR_TIER + 2, Start, (RecoverItemQuest, Anywhere, 6, 3022, Medium, 'mh'), 3112, Same, NA, (5235, 5279), TTLocalizer.QuestDialogDict[5278]),
    5235: (BR_TIER + 2, Cont, (RecoverItemQuest, Anywhere, 1, 3013, Hard, 'rb'), Same, Same, NA, 5236, TTLocalizer.QuestDialogDict[5235]),
    5279: (BR_TIER + 2, Cont, (RecoverItemQuest, Anywhere, 1, 3013, Medium, 'bw'), Same, Same, NA, 5236, TTLocalizer.QuestDialogDict[5279]),
    5236: (BR_TIER + 2, Cont, (RecoverItemQuest, Anywhere, 1, 3014, Hard, AnyFish), Same, Same, NA, 5237, TTLocalizer.QuestDialogDict[5236]),
    5237: (BR_TIER + 2, Cont, (VisitQuest,), Same, 3128, NA, (5238, 5280), TTLocalizer.QuestDialogDict[5237]),
    5238: (BR_TIER + 2, Cont, (RecoverItemQuest, Anywhere, 10, 3015, VeryEasy, 'mh'), Same, Same, NA, 5239, TTLocalizer.QuestDialogDict[5238]),
    5280: (BR_TIER + 2, Cont, (RecoverItemQuest, Anywhere, 10, 3015, VeryEasy, 'tbc'), Same, Same, NA, 5239, TTLocalizer.QuestDialogDict[5280]),
    5239: (BR_TIER + 2, Cont, (DeliverItemQuest, 3015), Same, 3112, NA, (5240, 5281), TTLocalizer.QuestDialogDict[5239]),
    5240: (BR_TIER + 2, Cont, (RecoverItemQuest, Anywhere, 1, 3016, Hard, 'bw'), Same, Same, NA, 5241, TTLocalizer.QuestDialogDict[5240]),
    5281: (BR_TIER + 2, Cont, (RecoverItemQuest, Anywhere, 1, 3023, Easy, 'mh'), Same, Same, NA, 5241, TTLocalizer.QuestDialogDict[5281]),
    5241: (BR_TIER + 2, Cont, (BuildingQuest, Anywhere, 15, Any, 4, 0), Same, Same, NA, 5242, TTLocalizer.QuestDialogDict[5241]),
    5242: (BR_TIER + 2, Cont, (RecoverItemQuest, Anywhere, 1, 3014, VeryHard, AnyFish), Same, Same, 900, NA, TTLocalizer.QuestDialogDict[5242]),
    5320: (BR_TIER + 2, Start, (CogQuest, Anywhere, 30, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5321: (BR_TIER + 2, Start, (CogQuest, Anywhere, 32, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5322: (BR_TIER + 2, Start, (CogQuest, Anywhere, 35, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5323: (BR_TIER + 2, Start, (CogQuest, Anywhere, 35, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5324: (BR_TIER + 2, Start, (CogQuest, Anywhere, 35, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5325: (BR_TIER + 2, Start, (CogQuest, Anywhere, 40, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5326: (BR_TIER + 2, Start, (CogQuest, Anywhere, 40, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5327: (BR_TIER + 2, Start, (CogQuest, Anywhere, 45, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5328: (BR_TIER + 2, Start, (CogQuest, Anywhere, 45, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5329: (BR_TIER + 2, Start, (CogQuest, Anywhere, 50, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5330: (BR_TIER + 2, Start, (CogLevelQuest, Anywhere, 20, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    5331: (BR_TIER + 2, Start, (CogLevelQuest, Anywhere, 25, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    5332: (BR_TIER + 2, Start, (CogLevelQuest, Anywhere, 30, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    5333: (BR_TIER + 2, Start, (CogLevelQuest, Anywhere, 5, 7), Any, ToonHQ, Any, NA, DefaultDialog),
    5334: (BR_TIER + 2, Start, (CogLevelQuest, Anywhere, 8, 7), Any, ToonHQ, Any, NA, DefaultDialog),
    5335: (BR_TIER + 2, Start, (CogLevelQuest, Anywhere, 14, 7), Any, ToonHQ, Any, NA, DefaultDialog),
    5336: (BR_TIER + 2, Start, (CogLevelQuest, Anywhere, 2, 8), Any, ToonHQ, Any, NA, DefaultDialog),
    5337: (BR_TIER + 2, Start, (CogLevelQuest, Anywhere, 4, 8), Any, ToonHQ, Any, NA, DefaultDialog),
    5338: (BR_TIER + 2, Start, (CogLevelQuest, Anywhere, 7, 8), Any, ToonHQ, Any, NA, DefaultDialog),
    5339: (BR_TIER + 2, Start, (CogLevelQuest, Anywhere, 10, 8), Any, ToonHQ, Any, NA, DefaultDialog),
    5340: (BR_TIER + 2, Start, (CogQuest, ToontownGlobals.TheBrrrgh, 50, Any), Any, ToonHQ, NA, 5341, DefaultDialog),
    5341: (BR_TIER + 2, Cont, (DeliverItemQuest, 1000), Any, 3008, 1000, NA, DefaultDialog),
    5370: (BR_TIER + 2, Start, (CogQuest, ToontownGlobals.SellbotHQ, 15, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5371: (BR_TIER + 2, Start, (CogQuest, ToontownGlobals.SellbotHQ, 20, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    5372: (BR_TIER + 2, Start, (CogLevelQuest, ToontownGlobals.SellbotHQ, 12, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    5373: (BR_TIER + 2, Start, (CogLevelQuest, ToontownGlobals.SellbotHQ, 8, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    5374: (BR_TIER + 2, Start, (CogLevelQuest, ToontownGlobals.SellbotFactoryInt, 10, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    5375: (BR_TIER + 2, Start, (CogLevelQuest, ToontownGlobals.SellbotFactoryInt, 5, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    5376: (BR_TIER + 2, Start, (FactoryQuest, ToontownGlobals.SellbotHQ, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    5377: (BR_TIER + 2, Start, (FactoryQuest, ToontownGlobals.SellbotHQ, 2), Any, ToonHQ, Any, NA, DefaultDialog),
    5378: (BR_TIER + 2, Start, (FactoryQuest, ToontownGlobals.SellbotHQ, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    5379: (BR_TIER + 2, Start, (FactoryQuest, ToontownGlobals.SellbotHQ, 2), Any, ToonHQ, Any, NA, DefaultDialog),
    5380: (BR_TIER + 2, Start, (SkelecogQuest, ToontownGlobals.SellbotFactoryInt, 12), Any, ToonHQ, Any, NA, DefaultDialog),
    5381: (BR_TIER + 2, Start, (SkelecogLevelQuest, ToontownGlobals.SellbotHQ, 5, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    5382: (BR_TIER + 2, Start, (SkelecogLevelQuest, ToontownGlobals.SellbotHQ, 3, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    5383: (BR_TIER + 2, Start, (ForemanQuest, ToontownGlobals.SellbotHQ, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    5384: (BR_TIER + 2, Start, (ForemanQuest, ToontownGlobals.SellbotHQ, 2), Any, ToonHQ, Any, NA, DefaultDialog),
    5385: (BR_TIER + 2, Start, (RescueQuest, InVP, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    5386: (BR_TIER + 2, Start, (RescueQuest, InFO, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    6101: (DL_TIER, Start, (CogQuest, ToontownGlobals.DonaldsDreamland, 50, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    6102: (DL_TIER, Start, (CogQuest, ToontownGlobals.DonaldsDreamland, 45, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    6104: (DL_TIER, Start, (CogQuest, Anywhere, 60, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    6105: (DL_TIER, Start, (CogQuest, Anywhere, 70, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    6106: (DL_TIER, Start, (CogQuest, Anywhere, 80, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    6107: (DL_TIER, Start, (CogQuest, Anywhere, 10, 'ym'), Any, ToonHQ, Any, NA, DefaultDialog),
    6108: (DL_TIER, Start, (CogQuest, Anywhere, 15, 'mm'), Any, ToonHQ, Any, NA, DefaultDialog),
    6109: (DL_TIER, Start, (CogQuest, Anywhere, 15, 'ds'), Any, ToonHQ, Any, NA, DefaultDialog),
    6110: (DL_TIER, Start, (CogQuest, Anywhere, 15, 'hh'), Any, ToonHQ, Any, NA, DefaultDialog),
    6111: (DL_TIER, Start, (CogQuest, Anywhere, 15, 'cr'), Any, ToonHQ, Any, NA, DefaultDialog),
    6112: (DL_TIER, Start, (CogQuest, Anywhere, 6, 'tbc'), Any, ToonHQ, Any, NA, DefaultDialog),
    6113: (DL_TIER, Start, (CogQuest, Anywhere, 20, 'nd'), Any, ToonHQ, Any, NA, DefaultDialog),
    6114: (DL_TIER, Start, (CogQuest, Anywhere, 20, 'gh'), Any, ToonHQ, Any, NA, DefaultDialog),
    6115: (DL_TIER, Start, (CogQuest, Anywhere, 20, 'ms'), Any, ToonHQ, Any, NA, DefaultDialog),
    6116: (DL_TIER, Start, (CogQuest, Anywhere, 20, 'tf'), Any, ToonHQ, Any, NA, DefaultDialog),
    6117: (DL_TIER, Start, (CogQuest, Anywhere, 10, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    6118: (DL_TIER, Start, (CogQuest, Anywhere, 6, 'mh'), Any, ToonHQ, Any, NA, DefaultDialog),
    6119: (DL_TIER, Start, (CogQuest, Anywhere, 20, 'tw'), Any, ToonHQ, Any, NA, DefaultDialog),
    6120: (DL_TIER, Start, (CogQuest, Anywhere, 20, 'bc'), Any, ToonHQ, Any, NA, DefaultDialog),
    6121: (DL_TIER, Start, (CogQuest, Anywhere, 20, 'nc'), Any, ToonHQ, Any, NA, DefaultDialog),
    6123: (DL_TIER, Start, (CogQuest, Anywhere, 10, 'ls'), Any, ToonHQ, Any, NA, DefaultDialog),
    6124: (DL_TIER, Start, (CogQuest, Anywhere, 6, 'rb'), Any, ToonHQ, Any, NA, DefaultDialog),
    6125: (DL_TIER, Start, (CogQuest, Anywhere, 20, 'dt'), Any, ToonHQ, Any, NA, DefaultDialog),
    6126: (DL_TIER, Start, (CogQuest, Anywhere, 20, 'ac'), Any, ToonHQ, Any, NA, DefaultDialog),
    6127: (DL_TIER, Start, (CogQuest, Anywhere, 20, 'bs'), Any, ToonHQ, Any, NA, DefaultDialog),
    6128: (DL_TIER, Start, (CogQuest, Anywhere, 20, 'sd'), Any, ToonHQ, Any, NA, DefaultDialog),
    6129: (DL_TIER, Start, (CogQuest, Anywhere, 10, 'le'), Any, ToonHQ, Any, NA, DefaultDialog),
    6130: (DL_TIER, Start, (CogQuest, Anywhere, 5, 'bw'), Any, ToonHQ, Any, NA, DefaultDialog),
    6131: (DL_TIER, Start, (CogLevelQuest, Anywhere, 40, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    6132: (DL_TIER, Start, (CogLevelQuest, Anywhere, 30, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    6133: (DL_TIER, Start, (CogLevelQuest, Anywhere, 25, 7), Any, ToonHQ, Any, NA, DefaultDialog),
    6134: (DL_TIER, Start, (CogLevelQuest, Anywhere, 20, 8), Any, ToonHQ, Any, NA, DefaultDialog),
    6135: (DL_TIER, Start, (CogLevelQuest, Anywhere, 15, 9), Any, ToonHQ, Any, NA, DefaultDialog),
    6136: (DL_TIER, Start, (CogLevelQuest, Anywhere, 15, 9), Any, ToonHQ, Any, NA, DefaultDialog),
    6137: (DL_TIER, Start, (CogLevelQuest, Anywhere, 12, 9), Any, ToonHQ, Any, NA, DefaultDialog),
    6138: (DL_TIER, Start, (CogLevelQuest, Anywhere, 7, 10), Any, ToonHQ, Any, NA, DefaultDialog),
    6139: (DL_TIER, Start, (CogTrackQuest, ToontownGlobals.DonaldsDreamland, 40, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    6140: (DL_TIER, Start, (CogTrackQuest, ToontownGlobals.DonaldsDreamland, 40, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    6142: (DL_TIER, Start, (CogTrackQuest, ToontownGlobals.DonaldsDreamland, 40, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    6144: (DL_TIER, Start, (CogTrackQuest, ToontownGlobals.DonaldsDreamland, 45, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    6145: (DL_TIER, Start, (CogTrackQuest, ToontownGlobals.DonaldsDreamland, 45, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    6146: (DL_TIER, Start, (CogTrackQuest, ToontownGlobals.DonaldsDreamland, 45, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    6148: (DL_TIER, Start, (CogTrackQuest, Anywhere, 50, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    6149: (DL_TIER, Start, (CogTrackQuest, Anywhere, 50, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    6150: (DL_TIER, Start, (CogTrackQuest, Anywhere, 50, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    6151: (DL_TIER, Start, (BuildingQuest, Anywhere, 5, Any, 2, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    6152: (DL_TIER, Start, (BuildingQuest, Anywhere, 3, Any, 4, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    6154: (DL_TIER, Start, (BuildingQuest, Anywhere, 2, Any, 5, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    6155: (DL_TIER, Start, (BuildingQuest, Anywhere, 1, 'm', 5, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    6156: (DL_TIER, Start, (BuildingQuest, Anywhere, 1, 's', 5, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    6157: (DL_TIER, Start, (BuildingQuest, Anywhere, 1, 'c', 5, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    6158: (DL_TIER, Start, (BuildingQuest, Anywhere, 1, 'l', 5, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    6201: (DL_TIER, Start, (VisitQuest,), Any, 9111, NA, 6202, TTLocalizer.QuestDialogDict[6201]),
    6202: (DL_TIER, Start, (CogQuest, ToontownGlobals.DonaldsDreamland, 50, Any), 9111, Same, 100, NA, TTLocalizer.QuestDialogDict[6202]),
    6206: (DL_TIER, Start, (VisitQuest,), Any, 9131, NA, 6207, TTLocalizer.QuestDialogDict[6206]),
    6207: (DL_TIER, Start, (BuildingQuest, ToontownGlobals.DonaldsDreamland, 8, Any, 4, 0), 9131, Same, 205, NA, TTLocalizer.QuestDialogDict[6207]),
    6211: (DL_TIER, Start, (VisitQuest,), Any, 9217, NA, 6212, TTLocalizer.QuestDialogDict[6211]),
    6212: (DL_TIER, Start, (RecoverItemQuest, Anywhere, 2, 6002, Medium, 'bc'), 9217, Same, NA, 6213, TTLocalizer.QuestDialogDict[6212]),
    6213: (DL_TIER, Cont, (RecoverItemQuest, Anywhere, 1, 6003, Medium, 'mb'), Same, Same, NA, 6214, TTLocalizer.QuestDialogDict[6213]),
    6214: (DL_TIER, Cont, (RecoverItemQuest, Anywhere, 1, 6004, Easy, 'pp'), Same, Same, 101, NA, TTLocalizer.QuestDialogDict[6214]),
    6221: (DL_TIER, Start, (VisitQuest,), Any, 9119, NA, 6222, TTLocalizer.QuestDialogDict[6221]),
    6222: (DL_TIER, Start, (CogTrackQuest, ToontownGlobals.DonaldsDreamland, 40, 'c'), 9119, Same, 102, NA, TTLocalizer.QuestDialogDict[6222]),
    6231: (DL_TIER, Start, (VisitQuest,), Any, 9203, NA, 6232, TTLocalizer.QuestDialogDict[6231]),
    6232: (DL_TIER, Start, (VisitQuest,), 9203, 9103, NA, 6233, TTLocalizer.QuestDialogDict[6232]),
    6233: (DL_TIER, Cont, (CogTrackQuest, ToontownGlobals.CashbotHQ, 7, 'm'), Same, Same, NA, 6234, TTLocalizer.QuestDialogDict[6233]),
    6234: (DL_TIER, Cont, (VisitQuest,), Same, 9203, NA, 6235, TTLocalizer.QuestDialogDict[6234]),
    6235: (DL_TIER, Cont, (RecoverItemQuest, ToontownGlobals.CashbotHQ, 1, 6001, Hard, 'm', 'track'), Same, Same, 4000, NA, TTLocalizer.QuestDialogDict[6235]),
    6241: (DL_TIER, Start, (VisitQuest,), Any, 9219, NA, 6242, TTLocalizer.QuestDialogDict[6241]),
    6242: (DL_TIER, Start, (CogQuest, ToontownGlobals.DonaldsDreamland, 15, 'nc'), 9219, Same, 705, NA, TTLocalizer.QuestDialogDict[6242]),
    6251: (DL_TIER, Start, (VisitQuest,), Any, 9221, NA, 6252, TTLocalizer.QuestDialogDict[6251]),
    6252: (DL_TIER, Start, (DeliverItemQuest, 6006), 9221, 9222, NA, 6253, TTLocalizer.QuestDialogDict[6252]),
    6253: (DL_TIER, Cont, (VisitQuest,), Same, 9221, NA, 6254, TTLocalizer.QuestDialogDict[6253]),
    6254: (DL_TIER, Cont, (DeliverItemQuest, 6007), Same, 9210, NA, 6255, TTLocalizer.QuestDialogDict[6254]),
    6255: (DL_TIER, Cont, (CogTrackQuest, Anywhere, 50, 'm'), Same, Same, NA, 6256, TTLocalizer.QuestDialogDict[6255]),
    6256: (DL_TIER, Cont, (VisitQuest,), Same, 9221, NA, 6257, TTLocalizer.QuestDialogDict[6256]),
    6257: (DL_TIER, Cont, (DeliverItemQuest, 6008), Same, 9205, NA, 6258, TTLocalizer.QuestDialogDict[6257]),
    6258: (DL_TIER, Cont, (CogQuest, Anywhere, 10, 'ms'), Same, Same, NA, 6259, TTLocalizer.QuestDialogDict[6258]),
    6259: (DL_TIER, Cont, (VisitQuest,), Same, 9221, NA, 6260, TTLocalizer.QuestDialogDict[6259]),
    6260: (DL_TIER, Cont, (DeliverItemQuest, 6009), Same, 9229, NA, 6261, TTLocalizer.QuestDialogDict[6260]),
    6261: (DL_TIER, Cont, (VisitQuest,), Same, 9221, NA, 6262, TTLocalizer.QuestDialogDict[6261]),
    6262: (DL_TIER, Cont, (DeliverItemQuest, 6010), Same, 9126, NA, 6263, TTLocalizer.QuestDialogDict[6262]),
    6263: (DL_TIER, Cont, (DeliverItemQuest, 6010), Same, 9112, NA, 6264, TTLocalizer.QuestDialogDict[6263]),
    6264: (DL_TIER, Cont, (DeliverItemQuest, 6011), Same, 9221, NA, 6265, TTLocalizer.QuestDialogDict[6264]),
    6265: (DL_TIER, Cont, (DeliverItemQuest, 6012), Same, 9115, NA, 6266, TTLocalizer.QuestDialogDict[6265]),
    6266: (DL_TIER, Cont, (VisitQuest,), Same, 9221, 103, NA, TTLocalizer.QuestDialogDict[6266]),
    6271: (DL_TIER, Start, (VisitQuest,), Any, 9208, NA, 6272, TTLocalizer.QuestDialogDict[6271]),
    6272: (DL_TIER, Start, (BuildingQuest, ToontownGlobals.DonaldsDreamland, 1, 'm', 5, 0), 9208, Same, 305, NA, TTLocalizer.QuestDialogDict[6272]),
    6281: (DL_TIER, Start, (VisitQuest,), Any, 9123, NA, 6282, TTLocalizer.QuestDialogDict[6281]),
    6282: (DL_TIER, Start, (CogTrackQuest, ToontownGlobals.DonaldsDreamland, 40, 'm'), 9123, Same, 4001, NA, TTLocalizer.QuestDialogDict[6282]),
    6291: (DL_TIER, Start, (VisitQuest,), Any, 9226, NA, 6292, TTLocalizer.QuestDialogDict[6291]),
    6292: (DL_TIER, Start, (RecoverItemQuest, ToontownGlobals.DonaldsDreamland, 1, 6005, Hard, 'm', 'track'), 9226, Same, 4002, NA, TTLocalizer.QuestDialogDict[6292]),
    6301: (DL_TIER, Start, (CogQuest, ToontownGlobals.CashbotHQ, 35, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    6302: (DL_TIER, Start, (CogQuest, ToontownGlobals.CashbotHQ, 40, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    6303: (DL_TIER, Start, (CogQuest, ToontownGlobals.CashbotHQ, 55, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    6304: (DL_TIER, Start, (CogLevelQuest, ToontownGlobals.CashbotHQ, 20, 7), Any, ToonHQ, Any, NA, DefaultDialog),
    6305: (DL_TIER, Start, (CogLevelQuest, ToontownGlobals.CashbotHQ, 15, 8), Any, ToonHQ, Any, NA, DefaultDialog),
    6306: (DL_TIER, Start, (CogLevelQuest, ToontownGlobals.CashbotHQ, 10, 9), Any, ToonHQ, Any, NA, DefaultDialog),
    6307: (DL_TIER, Start, (CogLevelQuest, ToontownGlobals.CashbotMintIntA, 10, 10), Any, ToonHQ, Any, NA, DefaultDialog),
    6310: (DL_TIER, Start, (MintQuest, ToontownGlobals.CashbotMintIntA, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    6313: (DL_TIER, Start, (SkelecogQuest, ToontownGlobals.CashbotHQ, 15), Any, ToonHQ, Any, NA, DefaultDialog),
    6314: (DL_TIER, Start, (SkelecogLevelQuest, ToontownGlobals.CashbotHQ, 7, 11), Any, ToonHQ, Any, NA, DefaultDialog),
    6315: (DL_TIER, Start, (SkelecogLevelQuest, ToontownGlobals.CashbotHQ, 3, 12), Any, ToonHQ, Any, NA, DefaultDialog),
    6318: (DL_TIER, Start, (SupervisorQuest, ToontownGlobals.CashbotMintIntA, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    6321: (DL_TIER, Start, (CogLevelQuest, ToontownGlobals.CashbotMintIntA, 8, 10), Any, ToonHQ, Any, NA, DefaultDialog),
    6322: (DL_TIER, Start, (CogLevelQuest, ToontownGlobals.CashbotMintIntA, 6, 10), Any, ToonHQ, Any, NA, DefaultDialog),
    6323: (DL_TIER, Start, (MintQuest, ToontownGlobals.CashbotMintIntA, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    6324: (DL_TIER, Start, (MintQuest, ToontownGlobals.CashbotMintIntA, 2), Any, ToonHQ, Any, NA, DefaultDialog),
    6325: (DL_TIER, Start, (SupervisorQuest, ToontownGlobals.CashbotMintIntA, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    6326: (DL_TIER, Start, (SupervisorQuest, ToontownGlobals.CashbotMintIntA, 2), Any, ToonHQ, Any, NA, DefaultDialog),
    6327: (DL_TIER, Start, (RescueQuest, InVP, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    6328: (DL_TIER, Start, (RescueQuest, InFO, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    7101: (DL_TIER + 1, Start, (CogQuest, Anywhere, 100, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    7102: (DL_TIER + 1, Start, (CogQuest, Anywhere, 100, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    7104: (DL_TIER + 1, Start, (CogQuest, Anywhere, 120, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    7105: (DL_TIER + 1, Start, (CogQuest, Anywhere, 140, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    7106: (DL_TIER + 1, Start, (CogQuest, Anywhere, 150, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    7107: (DL_TIER + 1, Start, (CogQuest, Anywhere, 40, 'ym'), Any, ToonHQ, Any, NA, DefaultDialog),
    7108: (DL_TIER + 1, Start, (CogQuest, Anywhere, 40, 'mm'), Any, ToonHQ, Any, NA, DefaultDialog),
    7109: (DL_TIER + 1, Start, (CogQuest, Anywhere, 40, 'ds'), Any, ToonHQ, Any, NA, DefaultDialog),
    7110: (DL_TIER + 1, Start, (CogQuest, Anywhere, 40, 'hh'), Any, ToonHQ, Any, NA, DefaultDialog),
    7111: (DL_TIER + 1, Start, (CogQuest, Anywhere, 20, 'cr'), Any, ToonHQ, Any, NA, DefaultDialog),
    7112: (DL_TIER + 1, Start, (CogQuest, Anywhere, 10, 'tbc'), Any, ToonHQ, Any, NA, DefaultDialog),
    7113: (DL_TIER + 1, Start, (CogQuest, Anywhere, 50, 'nd'), Any, ToonHQ, Any, NA, DefaultDialog),
    7114: (DL_TIER + 1, Start, (CogQuest, Anywhere, 40, 'gh'), Any, ToonHQ, Any, NA, DefaultDialog),
    7115: (DL_TIER + 1, Start, (CogQuest, Anywhere, 40, 'ms'), Any, ToonHQ, Any, NA, DefaultDialog),
    7116: (DL_TIER + 1, Start, (CogQuest, Anywhere, 40, 'tf'), Any, ToonHQ, Any, NA, DefaultDialog),
    7117: (DL_TIER + 1, Start, (CogQuest, Anywhere, 20, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    7118: (DL_TIER + 1, Start, (CogQuest, Anywhere, 10, 'mh'), Any, ToonHQ, Any, NA, DefaultDialog),
    7119: (DL_TIER + 1, Start, (CogQuest, Anywhere, 40, 'tw'), Any, ToonHQ, Any, NA, DefaultDialog),
    7120: (DL_TIER + 1, Start, (CogQuest, Anywhere, 40, 'bc'), Any, ToonHQ, Any, NA, DefaultDialog),
    7122: (DL_TIER + 1, Start, (CogQuest, Anywhere, 30, 'mb'), Any, ToonHQ, Any, NA, DefaultDialog),
    7123: (DL_TIER + 1, Start, (CogQuest, Anywhere, 20, 'ls'), Any, ToonHQ, Any, NA, DefaultDialog),
    7124: (DL_TIER + 1, Start, (CogQuest, Anywhere, 10, 'rb'), Any, ToonHQ, Any, NA, DefaultDialog),
    7125: (DL_TIER + 1, Start, (CogQuest, Anywhere, 40, 'dt'), Any, ToonHQ, Any, NA, DefaultDialog),
    7126: (DL_TIER + 1, Start, (CogQuest, Anywhere, 40, 'ac'), Any, ToonHQ, Any, NA, DefaultDialog),
    7127: (DL_TIER + 1, Start, (CogQuest, Anywhere, 40, 'bs'), Any, ToonHQ, Any, NA, DefaultDialog),
    7128: (DL_TIER + 1, Start, (CogQuest, Anywhere, 40, 'sd'), Any, ToonHQ, Any, NA, DefaultDialog),
    7129: (DL_TIER + 1, Start, (CogQuest, Anywhere, 20, 'le'), Any, ToonHQ, Any, NA, DefaultDialog),
    7130: (DL_TIER + 1, Start, (CogQuest, Anywhere, 10, 'bw'), Any, ToonHQ, Any, NA, DefaultDialog),
    7131: (DL_TIER + 1, Start, (CogLevelQuest, Anywhere, 80, 7), Any, ToonHQ, Any, NA, DefaultDialog),
    7132: (DL_TIER + 1, Start, (CogLevelQuest, Anywhere, 60, 8), Any, ToonHQ, Any, NA, DefaultDialog),
    7133: (DL_TIER + 1, Start, (CogLevelQuest, Anywhere, 40, 9), Any, ToonHQ, Any, NA, DefaultDialog),
    7134: (DL_TIER + 1, Start, (CogLevelQuest, Anywhere, 50, 9), Any, ToonHQ, Any, NA, DefaultDialog),
    7135: (DL_TIER + 1, Start, (CogLevelQuest, Anywhere, 30, 10), Any, ToonHQ, Any, NA, DefaultDialog),
    7136: (DL_TIER + 1, Start, (CogLevelQuest, Anywhere, 30, 10), Any, ToonHQ, Any, NA, DefaultDialog),
    7137: (DL_TIER + 1, Start, (CogLevelQuest, Anywhere, 10, 11), Any, ToonHQ, Any, NA, DefaultDialog),
    7138: (DL_TIER + 1, Start, (CogLevelQuest, Anywhere, 20, 11), Any, ToonHQ, Any, NA, DefaultDialog),
    7139: (DL_TIER + 1, Start, (CogTrackQuest, Anywhere, 80, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    7140: (DL_TIER + 1, Start, (CogTrackQuest, Anywhere, 80, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    7141: (DL_TIER + 1, Start, (CogTrackQuest, Anywhere, 80, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    7142: (DL_TIER + 1, Start, (CogTrackQuest, Anywhere, 80, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    7144: (DL_TIER + 1, Start, (CogTrackQuest, Anywhere, 100, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    7145: (DL_TIER + 1, Start, (CogTrackQuest, Anywhere, 100, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    7146: (DL_TIER + 1, Start, (CogTrackQuest, Anywhere, 100, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    7147: (DL_TIER + 1, Start, (CogTrackQuest, Anywhere, 100, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    7148: (DL_TIER + 1, Start, (CogTrackQuest, Anywhere, 100, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    7149: (DL_TIER + 1, Start, (CogTrackQuest, Anywhere, 100, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    7150: (DL_TIER + 1, Start, (CogTrackQuest, Anywhere, 100, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    7151: (DL_TIER + 1, Start, (BuildingQuest, Anywhere, 10, Any, 2, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    7153: (DL_TIER + 1, Start, (BuildingQuest, Anywhere, 5, Any, 4, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    7154: (DL_TIER + 1, Start, (BuildingQuest, Anywhere, 3, Any, 5, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    7156: (DL_TIER + 1, Start, (BuildingQuest, Anywhere, 2, 's', 5, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    7157: (DL_TIER + 1, Start, (BuildingQuest, Anywhere, 2, 'c', 5, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    7158: (DL_TIER + 1, Start, (BuildingQuest, Anywhere, 2, 'l', 5, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    7201: (DL_TIER + 1, Start, (VisitQuest,), Any, 9124, NA, 7202, TTLocalizer.QuestDialogDict[7201]),
    7202: (DL_TIER + 1, Start, (VisitQuest,), 9124, 9128, NA, 7203, TTLocalizer.QuestDialogDict[7202]),
    7203: (DL_TIER + 1, Cont, (DeliverItemQuest, 7001), Same, 9124, NA, 7204, TTLocalizer.QuestDialogDict[7203]),
    7204: (DL_TIER + 1, Cont, (VisitQuest,), Same, 9128, NA, 7205, TTLocalizer.QuestDialogDict[7204]),
    7205: (DL_TIER + 1, Cont, (CogQuest, ToontownGlobals.DonaldsDreamland, 100, Any), Same, Same, NA, 7206, TTLocalizer.QuestDialogDict[7205]),
    7206: (DL_TIER + 1, Cont, (DeliverItemQuest, 7002), Same, 9124, 4003, NA, TTLocalizer.QuestDialogDict[7206]),
    7209: (DL_TIER + 1, Start, (VisitQuest,), Any, 9232, NA, 7210, TTLocalizer.QuestDialogDict[7209]),
    7210: (DL_TIER + 1, Start, (VisitQuest,), 9232, 9101, NA, 7211, TTLocalizer.QuestDialogDict[7210]),
    7211: (DL_TIER + 1, Cont, (CogQuest, Anywhere, 10, 'nc'), Same, Same, NA, 7212, TTLocalizer.QuestDialogDict[7211]),
    7212: (DL_TIER + 1, Cont, (DeliverItemQuest, 7003), Same, 9232, NA, 7213, TTLocalizer.QuestDialogDict[7212]),
    7213: (DL_TIER + 1, Cont, (VisitQuest,), Same, 9101, NA, 7214, TTLocalizer.QuestDialogDict[7213]),
    7214: (DL_TIER + 1, Cont, (CogTrackQuest, Anywhere, 40, 'm'), Same, Same, NA, 7215, TTLocalizer.QuestDialogDict[7214]),
    7215: (DL_TIER + 1, Cont, (DeliverItemQuest, 7004), Same, 9232, 4004, NA, TTLocalizer.QuestDialogDict[7215]),
    7218: (DL_TIER + 1, Start, (VisitQuest,), Any, 9109, NA, 7219, TTLocalizer.QuestDialogDict[7218]),
    7219: (DL_TIER + 1, Start, (VisitQuest,), 9109, 9230, NA, 7220, TTLocalizer.QuestDialogDict[7219]),
    7220: (DL_TIER + 1, Cont, (DeliverItemQuest, 7005), Same, 9109, NA, 7221, TTLocalizer.QuestDialogDict[7220]),
    7221: (DL_TIER + 1, Cont, (VisitQuest,), Same, 9230, NA, 7222, TTLocalizer.QuestDialogDict[7221]),
    7222: (DL_TIER + 1, Cont, (BuildingQuest, Anywhere, 5, Any, 3, 0), Same, Same, NA, 7223, TTLocalizer.QuestDialogDict[7222]),
    7223: (DL_TIER + 1, Cont, (DeliverItemQuest, 7006), Same, 9109, 4005, NA, TTLocalizer.QuestDialogDict[7223]),
    7226: (DL_TIER + 1, Start, (VisitQuest,), Any, 9224, NA, 7227, TTLocalizer.QuestDialogDict[7226]),
    7227: (DL_TIER + 1, Start, (VisitQuest,), 9224, 9102, NA, 7228, TTLocalizer.QuestDialogDict[7227]),
    7228: (DL_TIER + 1, Cont, (DeliverItemQuest, 7007), Same, 9224, NA, 7229, TTLocalizer.QuestDialogDict[7228]),
    7229: (DL_TIER + 1, Cont, (VisitQuest,), Same, 9102, NA, 7230, TTLocalizer.QuestDialogDict[7229]),
    7230: (DL_TIER + 1, Cont, (DeliverItemQuest, 7008), Same, 9224, NA, 7231, TTLocalizer.QuestDialogDict[7230]),
    7231: (DL_TIER + 1, Cont, (VisitQuest,), Same, 9102, NA, 7232, TTLocalizer.QuestDialogDict[7231]),
    7232: (DL_TIER + 1, Cont, (VisitQuest,), Same, 9216, NA, 7233, TTLocalizer.QuestDialogDict[7232]),
    7233: (DL_TIER + 1, Cont, (DeliverItemQuest, 7009), Same, 9224, NA, 7234, TTLocalizer.QuestDialogDict[7233]),
    7234: (DL_TIER + 1, Cont, (VisitQuest,), Same, 9216, NA, 7235, TTLocalizer.QuestDialogDict[7234]),
    7235: (DL_TIER + 1, Cont, (BuildingQuest, Anywhere, 2, 'm', 5, 0), Same, Same, NA, 7236, TTLocalizer.QuestDialogDict[7235]),
    7236: (DL_TIER + 1, Cont, (DeliverItemQuest, 7010), Same, 9224, 4006, NA, TTLocalizer.QuestDialogDict[7236]),
    7239: (DL_TIER + 1, Start, (VisitQuest,), Any, 9114, NA, 7240, TTLocalizer.QuestDialogDict[7239]),
    7240: (DL_TIER + 1, Start, (VisitQuest,), 9114, 9215, NA, 7241, TTLocalizer.QuestDialogDict[7240]),
    7241: (DL_TIER + 1, Cont, (RecoverItemQuest, ToontownGlobals.DonaldsDreamland, 1, 7011, Hard, AnyFish), Same, Same, NA, 7242, TTLocalizer.QuestDialogDict[7241]),
    7242: (DL_TIER + 1, Cont, (RecoverItemQuest, ToontownGlobals.DonaldsDreamland, 1, 7012, Medium, AnyFish), Same, Same, NA, 7243, TTLocalizer.QuestDialogDict[7242]),
    7243: (DL_TIER + 1, Cont, (RecoverItemQuest, ToontownGlobals.CashbotHQ, 1, 7013, Hard, 'ls'), Same, Same, NA, 7244, TTLocalizer.QuestDialogDict[7243]),
    7244: (DL_TIER + 1, Cont, (DeliverItemQuest, 7014), Same, 9114, 4007, NA, TTLocalizer.QuestDialogDict[7244]),
    7250: (DL_TIER + 1, Start, (CogQuest, ToontownGlobals.CashbotHQ, 60, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    7251: (DL_TIER + 1, Start, (CogQuest, ToontownGlobals.CashbotHQ, 70, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    7252: (DL_TIER + 1, Start, (CogQuest, ToontownGlobals.CashbotHQ, 80, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    7253: (DL_TIER + 1, Start, (CogLevelQuest, ToontownGlobals.CashbotHQ, 40, 7), Any, ToonHQ, Any, NA, DefaultDialog),
    7254: (DL_TIER + 1, Start, (CogLevelQuest, ToontownGlobals.CashbotHQ, 30, 8), Any, ToonHQ, Any, NA, DefaultDialog),
    7255: (DL_TIER + 1, Start, (CogLevelQuest, ToontownGlobals.CashbotHQ, 25, 9), Any, ToonHQ, Any, NA, DefaultDialog),
    7256: (DL_TIER + 1, Start, (CogLevelQuest, ToontownGlobals.CashbotMintIntA, 20, 10), Any, ToonHQ, Any, NA, DefaultDialog),
    7257: (DL_TIER + 1, Start, (CogLevelQuest, ToontownGlobals.CashbotMintIntB, 20, 11), Any, ToonHQ, Any, NA, DefaultDialog),
    7259: (DL_TIER + 1, Start, (MintQuest, ToontownGlobals.CashbotMintIntA, 7), Any, ToonHQ, Any, NA, DefaultDialog),
    7260: (DL_TIER + 1, Start, (MintQuest, ToontownGlobals.CashbotMintIntB, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    7262: (DL_TIER + 1, Start, (SkelecogQuest, ToontownGlobals.CashbotHQ, 24), Any, ToonHQ, Any, NA, DefaultDialog),
    7263: (DL_TIER + 1, Start, (SkelecogLevelQuest, ToontownGlobals.CashbotHQ, 15, 11), Any, ToonHQ, Any, NA, DefaultDialog),
    7264: (DL_TIER + 1, Start, (SkelecogLevelQuest, ToontownGlobals.CashbotHQ, 7, 12), Any, ToonHQ, Any, NA, DefaultDialog),
    7265: (DL_TIER + 1, Start, (SupervisorQuest, ToontownGlobals.CashbotMintIntA, 8), Any, ToonHQ, Any, NA, DefaultDialog),
    7266: (DL_TIER + 1, Start, (SupervisorQuest, ToontownGlobals.CashbotMintIntB, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    7268: (DL_TIER + 1, Start, (CogLevelQuest, ToontownGlobals.CashbotMintIntB, 15, 11), Any, ToonHQ, Any, NA, DefaultDialog),
    7269: (DL_TIER + 1, Start, (MintQuest, ToontownGlobals.CashbotMintIntB, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    7270: (DL_TIER + 1, Start, (SupervisorQuest, ToontownGlobals.CashbotMintIntB, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    7500: (DL_TIER + 1, Start, (CogQuest, ToontownGlobals.DonaldsDreamland, 80, Any), Any, ToonHQ, NA, 7501, DefaultDialog),
    7501: (DL_TIER + 1, Cont, (DeliverItemQuest, 1000), Any, 9010, 1000, NA, DefaultDialog),
    7506: (DL_TIER + 1, Start, (RescueQuest, InVP, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    7507: (DL_TIER + 1, Start, (RescueQuest, InFO, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    8101: (DL_TIER + 2, Start, (CogQuest, Anywhere, 200, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    8102: (DL_TIER + 2, Start, (CogQuest, Anywhere, 220, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    8103: (DL_TIER + 2, Start, (CogQuest, Anywhere, 240, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    8104: (DL_TIER + 2, Start, (CogQuest, Anywhere, 275, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    8105: (DL_TIER + 2, Start, (CogQuest, Anywhere, 300, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    8106: (DL_TIER + 2, Start, (CogQuest, Anywhere, 350, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    8107: (DL_TIER + 2, Start, (CogQuest, Anywhere, 100, 'ym'), Any, ToonHQ, Any, NA, DefaultDialog),
    8108: (DL_TIER + 2, Start, (CogQuest, Anywhere, 80, 'mm'), Any, ToonHQ, Any, NA, DefaultDialog),
    8109: (DL_TIER + 2, Start, (CogQuest, Anywhere, 75, 'ds'), Any, ToonHQ, Any, NA, DefaultDialog),
    8110: (DL_TIER + 2, Start, (CogQuest, Anywhere, 75, 'hh'), Any, ToonHQ, Any, NA, DefaultDialog),
    8111: (DL_TIER + 2, Start, (CogQuest, Anywhere, 40, 'cr'), Any, ToonHQ, Any, NA, DefaultDialog),
    8112: (DL_TIER + 2, Start, (CogQuest, Anywhere, 30, 'tbc'), Any, ToonHQ, Any, NA, DefaultDialog),
    8113: (DL_TIER + 2, Start, (CogQuest, Anywhere, 100, 'nd'), Any, ToonHQ, Any, NA, DefaultDialog),
    8114: (DL_TIER + 2, Start, (CogQuest, Anywhere, 80, 'gh'), Any, ToonHQ, Any, NA, DefaultDialog),
    8115: (DL_TIER + 2, Start, (CogQuest, Anywhere, 75, 'ms'), Any, ToonHQ, Any, NA, DefaultDialog),
    8116: (DL_TIER + 2, Start, (CogQuest, Anywhere, 75, 'tf'), Any, ToonHQ, Any, NA, DefaultDialog),
    8117: (DL_TIER + 2, Start, (CogQuest, Anywhere, 40, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    8118: (DL_TIER + 2, Start, (CogQuest, Anywhere, 30, 'mh'), Any, ToonHQ, Any, NA, DefaultDialog),
    8119: (DL_TIER + 2, Start, (CogQuest, Anywhere, 100, 'tw'), Any, ToonHQ, Any, NA, DefaultDialog),
    8120: (DL_TIER + 2, Start, (CogQuest, Anywhere, 100, 'bc'), Any, ToonHQ, Any, NA, DefaultDialog),
    8121: (DL_TIER + 2, Start, (CogQuest, Anywhere, 80, 'nc'), Any, ToonHQ, Any, NA, DefaultDialog),
    8122: (DL_TIER + 2, Start, (CogQuest, Anywhere, 80, 'mb'), Any, ToonHQ, Any, NA, DefaultDialog),
    8123: (DL_TIER + 2, Start, (CogQuest, Anywhere, 40, 'ls'), Any, ToonHQ, Any, NA, DefaultDialog),
    8124: (DL_TIER + 2, Start, (CogQuest, Anywhere, 20, 'rb'), Any, ToonHQ, Any, NA, DefaultDialog),
    8125: (DL_TIER + 2, Start, (CogQuest, Anywhere, 100, 'dt'), Any, ToonHQ, Any, NA, DefaultDialog),
    8126: (DL_TIER + 2, Start, (CogQuest, Anywhere, 100, 'ac'), Any, ToonHQ, Any, NA, DefaultDialog),
    8127: (DL_TIER + 2, Start, (CogQuest, Anywhere, 80, 'bs'), Any, ToonHQ, Any, NA, DefaultDialog),
    8128: (DL_TIER + 2, Start, (CogQuest, Anywhere, 80, 'sd'), Any, ToonHQ, Any, NA, DefaultDialog),
    8129: (DL_TIER + 2, Start, (CogQuest, Anywhere, 40, 'le'), Any, ToonHQ, Any, NA, DefaultDialog),
    8130: (DL_TIER + 2, Start, (CogQuest, Anywhere, 30, 'bw'), Any, ToonHQ, Any, NA, DefaultDialog),
    8131: (DL_TIER + 2, Start, (CogLevelQuest, Anywhere, 130, 9), Any, ToonHQ, Any, NA, DefaultDialog),
    8132: (DL_TIER + 2, Start, (CogLevelQuest, Anywhere, 160, 9), Any, ToonHQ, Any, NA, DefaultDialog),
    8133: (DL_TIER + 2, Start, (CogLevelQuest, Anywhere, 100, 10), Any, ToonHQ, Any, NA, DefaultDialog),
    8134: (DL_TIER + 2, Start, (CogLevelQuest, Anywhere, 110, 10), Any, ToonHQ, Any, NA, DefaultDialog),
    8135: (DL_TIER + 2, Start, (CogLevelQuest, Anywhere, 60, 11), Any, ToonHQ, Any, NA, DefaultDialog),
    8136: (DL_TIER + 2, Start, (CogLevelQuest, Anywhere, 80, 11), Any, ToonHQ, Any, NA, DefaultDialog),
    8137: (DL_TIER + 2, Start, (CogLevelQuest, Anywhere, 25, 12), Any, ToonHQ, Any, NA, DefaultDialog),
    8138: (DL_TIER + 2, Start, (CogLevelQuest, Anywhere, 40, 12), Any, ToonHQ, Any, NA, DefaultDialog),
    8139: (DL_TIER + 2, Start, (CogTrackQuest, Anywhere, 150, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    8140: (DL_TIER + 2, Start, (CogTrackQuest, Anywhere, 150, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    8141: (DL_TIER + 2, Start, (CogTrackQuest, Anywhere, 150, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    8142: (DL_TIER + 2, Start, (CogTrackQuest, Anywhere, 150, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    8143: (DL_TIER + 2, Start, (CogTrackQuest, Anywhere, 200, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    8144: (DL_TIER + 2, Start, (CogTrackQuest, Anywhere, 200, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    8145: (DL_TIER + 2, Start, (CogTrackQuest, Anywhere, 200, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    8146: (DL_TIER + 2, Start, (CogTrackQuest, Anywhere, 200, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    8147: (DL_TIER + 2, Start, (CogTrackQuest, Anywhere, 250, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    8148: (DL_TIER + 2, Start, (CogTrackQuest, Anywhere, 250, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    8149: (DL_TIER + 2, Start, (CogTrackQuest, Anywhere, 250, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    8150: (DL_TIER + 2, Start, (CogTrackQuest, Anywhere, 250, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    8151: (DL_TIER + 2, Start, (BuildingQuest, Anywhere, 30, Any, 2, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    8152: (DL_TIER + 2, Start, (BuildingQuest, Anywhere, 10, Any, 3, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    8153: (DL_TIER + 2, Start, (BuildingQuest, Anywhere, 10, Any, 4, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    8154: (DL_TIER + 2, Start, (BuildingQuest, Anywhere, 10, Any, 5, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    8155: (DL_TIER + 2, Start, (BuildingQuest, Anywhere, 5, 'm', 5, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    8156: (DL_TIER + 2, Start, (BuildingQuest, Anywhere, 5, 's', 5, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    8157: (DL_TIER + 2, Start, (BuildingQuest, Anywhere, 5, 'c', 5, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    8158: (DL_TIER + 2, Start, (BuildingQuest, Anywhere, 5, 'l', 5, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    8188: (DL_TIER + 2, Start, (BossQuest, ToontownGlobals.SellbotHQ, 2), Any, ToonHQ, Any, NA, DefaultDialog),
    8189: (DL_TIER + 2, Start, (RescueQuest, InVP, 4), Any, ToonHQ, Any, NA, DefaultDialog),
    8197: (DL_TIER + 2, Start, (RescueQuest, InFO, 8), Any, ToonHQ, Any, NA, DefaultDialog),
    8201: (DL_TIER + 2, Start, (CogQuest, ToontownGlobals.CashbotHQ, 120, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    8202: (DL_TIER + 2, Start, (CogQuest, ToontownGlobals.CashbotHQ, 140, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    8203: (DL_TIER + 2, Start, (CogQuest, ToontownGlobals.CashbotHQ, 160, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    8204: (DL_TIER + 2, Start, (CogLevelQuest, ToontownGlobals.CashbotHQ, 80, 7), Any, ToonHQ, Any, NA, DefaultDialog),
    8205: (DL_TIER + 2, Start, (CogLevelQuest, ToontownGlobals.CashbotHQ, 70, 8), Any, ToonHQ, Any, NA, DefaultDialog),
    8206: (DL_TIER + 2, Start, (CogLevelQuest, ToontownGlobals.CashbotHQ, 60, 9), Any, ToonHQ, Any, NA, DefaultDialog),
    8207: (DL_TIER + 2, Start, (CogLevelQuest, ToontownGlobals.CashbotMintIntA, 50, 10), Any, ToonHQ, Any, NA, DefaultDialog),
    8208: (DL_TIER + 2, Start, (CogLevelQuest, ToontownGlobals.CashbotMintIntB, 40, 11), Any, ToonHQ, Any, NA, DefaultDialog),
    8209: (DL_TIER + 2, Start, (CogLevelQuest, ToontownGlobals.CashbotMintIntC, 30, 11), Any, ToonHQ, Any, NA, DefaultDialog),
    8210: (DL_TIER + 2, Start, (MintQuest, ToontownGlobals.CashbotMintIntA, 12), Any, ToonHQ, Any, NA, DefaultDialog),
    8211: (DL_TIER + 2, Start, (MintQuest, ToontownGlobals.CashbotMintIntB, 10), Any, ToonHQ, Any, NA, DefaultDialog),
    8212: (DL_TIER + 2, Start, (MintQuest, ToontownGlobals.CashbotMintIntC, 8), Any, ToonHQ, Any, NA, DefaultDialog),
    8213: (DL_TIER + 2, Start, (SkelecogQuest, ToontownGlobals.CashbotMintIntA, 70), Any, ToonHQ, Any, NA, DefaultDialog),
    8214: (DL_TIER + 2, Start, (SkelecogQuest, ToontownGlobals.CashbotMintIntB, 50), Any, ToonHQ, Any, NA, DefaultDialog),
    8215: (DL_TIER + 2, Start, (SkelecogQuest, ToontownGlobals.CashbotMintIntC, 30), Any, ToonHQ, Any, NA, DefaultDialog),
    8216: (DL_TIER + 2, Start, (SupervisorQuest, ToontownGlobals.CashbotMintIntA, 12), Any, ToonHQ, Any, NA, DefaultDialog),
    8217: (DL_TIER + 2, Start, (SupervisorQuest, ToontownGlobals.CashbotMintIntB, 10), Any, ToonHQ, Any, NA, DefaultDialog),
    8218: (DL_TIER + 2, Start, (SupervisorQuest, ToontownGlobals.CashbotMintIntC, 8), Any, ToonHQ, Any, NA, DefaultDialog),
    8219: (DL_TIER + 2, Start, (BossQuest, ToontownGlobals.CashbotHQ, 2), Any, ToonHQ, 621, NA, DefaultDialog),
    8220: (DL_TIER + 2, Start, (BuildingQuest, Anywhere, 20, Any, 0, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    8221: (DL_TIER + 2, Start, (BuildingQuest, Anywhere, 15, Any, 0, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    8224: (DL_TIER + 2, Start, (BuildingQuest, Anywhere, 10, 's', 0, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    8225: (DL_TIER + 2, Start, (BuildingQuest, Anywhere, 10, 'l', 0, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    8226: (DL_TIER + 2, Start, (RescueQuest, InFO, 8), Any, ToonHQ, Any, NA, DefaultDialog),
    9101: (DL_TIER + 3, Start, (CogQuest, Anywhere, 300, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    9102: (DL_TIER + 3, Start, (CogQuest, Anywhere, 400, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    9103: (DL_TIER + 3, Start, (CogQuest, Anywhere, 500, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    9104: (DL_TIER + 3, Start, (CogQuest, Anywhere, 600, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    9105: (DL_TIER + 3, Start, (CogQuest, Anywhere, 700, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    9106: (DL_TIER + 3, Start, (CogQuest, Anywhere, 800, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    9107: (DL_TIER + 3, Start, (CogQuest, Anywhere, 200, 'ym'), Any, ToonHQ, Any, NA, DefaultDialog),
    9108: (DL_TIER + 3, Start, (CogQuest, Anywhere, 200, 'mm'), Any, ToonHQ, Any, NA, DefaultDialog),
    9109: (DL_TIER + 3, Start, (CogQuest, Anywhere, 150, 'ds'), Any, ToonHQ, Any, NA, DefaultDialog),
    9110: (DL_TIER + 3, Start, (CogQuest, Anywhere, 150, 'hh'), Any, ToonHQ, Any, NA, DefaultDialog),
    9111: (DL_TIER + 3, Start, (CogQuest, Anywhere, 70, 'cr'), Any, ToonHQ, Any, NA, DefaultDialog),
    9112: (DL_TIER + 3, Start, (CogQuest, Anywhere, 60, 'tbc'), Any, ToonHQ, Any, NA, DefaultDialog),
    9113: (DL_TIER + 3, Start, (CogQuest, Anywhere, 200, 'nd'), Any, ToonHQ, Any, NA, DefaultDialog),
    9114: (DL_TIER + 3, Start, (CogQuest, Anywhere, 200, 'gh'), Any, ToonHQ, Any, NA, DefaultDialog),
    9115: (DL_TIER + 3, Start, (CogQuest, Anywhere, 150, 'ms'), Any, ToonHQ, Any, NA, DefaultDialog),
    9116: (DL_TIER + 3, Start, (CogQuest, Anywhere, 150, 'tf'), Any, ToonHQ, Any, NA, DefaultDialog),
    9117: (DL_TIER + 3, Start, (CogQuest, Anywhere, 80, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    9118: (DL_TIER + 3, Start, (CogQuest, Anywhere, 60, 'mh'), Any, ToonHQ, Any, NA, DefaultDialog),
    9119: (DL_TIER + 3, Start, (CogQuest, Anywhere, 200, 'tw'), Any, ToonHQ, Any, NA, DefaultDialog),
    9120: (DL_TIER + 3, Start, (CogQuest, Anywhere, 200, 'bc'), Any, ToonHQ, Any, NA, DefaultDialog),
    9121: (DL_TIER + 3, Start, (CogQuest, Anywhere, 150, 'nc'), Any, ToonHQ, Any, NA, DefaultDialog),
    9122: (DL_TIER + 3, Start, (CogQuest, Anywhere, 150, 'mb'), Any, ToonHQ, Any, NA, DefaultDialog),
    9123: (DL_TIER + 3, Start, (CogQuest, Anywhere, 80, 'ls'), Any, ToonHQ, Any, NA, DefaultDialog),
    9124: (DL_TIER + 3, Start, (CogQuest, Anywhere, 60, 'rb'), Any, ToonHQ, Any, NA, DefaultDialog),
    9125: (DL_TIER + 3, Start, (CogQuest, Anywhere, 200, 'dt'), Any, ToonHQ, Any, NA, DefaultDialog),
    9126: (DL_TIER + 3, Start, (CogQuest, Anywhere, 200, 'ac'), Any, ToonHQ, Any, NA, DefaultDialog),
    9127: (DL_TIER + 3, Start, (CogQuest, Anywhere, 150, 'bs'), Any, ToonHQ, Any, NA, DefaultDialog),
    9128: (DL_TIER + 3, Start, (CogQuest, Anywhere, 150, 'sd'), Any, ToonHQ, Any, NA, DefaultDialog),
    9129: (DL_TIER + 3, Start, (CogQuest, Anywhere, 80, 'le'), Any, ToonHQ, Any, NA, DefaultDialog),
    9130: (DL_TIER + 3, Start, (CogQuest, Anywhere, 60, 'bw'), Any, ToonHQ, Any, NA, DefaultDialog),
    9131: (DL_TIER + 3, Start, (CogLevelQuest, Anywhere, 275, 9), Any, ToonHQ, Any, NA, DefaultDialog),
    9132: (DL_TIER + 3, Start, (CogLevelQuest, Anywhere, 350, 9), Any, ToonHQ, Any, NA, DefaultDialog),
    9133: (DL_TIER + 3, Start, (CogLevelQuest, Anywhere, 200, 10), Any, ToonHQ, Any, NA, DefaultDialog),
    9134: (DL_TIER + 3, Start, (CogLevelQuest, Anywhere, 200, 10), Any, ToonHQ, Any, NA, DefaultDialog),
    9135: (DL_TIER + 3, Start, (CogLevelQuest, Anywhere, 100, 11), Any, ToonHQ, Any, NA, DefaultDialog),
    9136: (DL_TIER + 3, Start, (CogLevelQuest, Anywhere, 110, 11), Any, ToonHQ, Any, NA, DefaultDialog),
    9137: (DL_TIER + 3, Start, (CogLevelQuest, Anywhere, 60, 12), Any, ToonHQ, Any, NA, DefaultDialog),
    9138: (DL_TIER + 3, Start, (CogLevelQuest, Anywhere, 80, 12), Any, ToonHQ, Any, NA, DefaultDialog),
    9139: (DL_TIER + 3, Start, (CogTrackQuest, Anywhere, 300, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    9140: (DL_TIER + 3, Start, (CogTrackQuest, Anywhere, 300, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    9141: (DL_TIER + 3, Start, (CogTrackQuest, Anywhere, 300, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    9142: (DL_TIER + 3, Start, (CogTrackQuest, Anywhere, 300, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    9143: (DL_TIER + 3, Start, (CogTrackQuest, Anywhere, 400, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    9144: (DL_TIER + 3, Start, (CogTrackQuest, Anywhere, 400, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    9145: (DL_TIER + 3, Start, (CogTrackQuest, Anywhere, 400, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    9146: (DL_TIER + 3, Start, (CogTrackQuest, Anywhere, 400, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    9147: (DL_TIER + 3, Start, (CogTrackQuest, Anywhere, 500, 'm'), Any, ToonHQ, Any, NA, DefaultDialog),
    9148: (DL_TIER + 3, Start, (CogTrackQuest, Anywhere, 500, 's'), Any, ToonHQ, Any, NA, DefaultDialog),
    9149: (DL_TIER + 3, Start, (CogTrackQuest, Anywhere, 500, 'c'), Any, ToonHQ, Any, NA, DefaultDialog),
    9150: (DL_TIER + 3, Start, (CogTrackQuest, Anywhere, 500, 'l'), Any, ToonHQ, Any, NA, DefaultDialog),
    9151: (DL_TIER + 3, Start, (BuildingQuest, Anywhere, 300, Any, 2, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    9152: (DL_TIER + 3, Start, (BuildingQuest, Anywhere, 100, Any, 3, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    9153: (DL_TIER + 3, Start, (BuildingQuest, Anywhere, 75, Any, 4, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    9154: (DL_TIER + 3, Start, (BuildingQuest, Anywhere, 60, Any, 5, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    9155: (DL_TIER + 3, Start, (BuildingQuest, Anywhere, 50, Any, 5, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    9156: (DL_TIER + 3, Start, (BuildingQuest, Anywhere, 50, Any, 5, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    9157: (DL_TIER + 3, Start, (BuildingQuest, Anywhere, 50, Any, 5, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    9158: (DL_TIER + 3, Start, (BuildingQuest, Anywhere, 50, Any, 5, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    9188: (DL_TIER + 3, Start, (BossQuest, ToontownGlobals.SellbotHQ, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    9189: (DL_TIER + 3, Start, (RescueQuest, InVP, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    9201: (DL_TIER + 3, Start, (CogQuest, ToontownGlobals.CashbotHQ, 250, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    9202: (DL_TIER + 3, Start, (CogQuest, ToontownGlobals.CashbotHQ, 300, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    9203: (DL_TIER + 3, Start, (CogQuest, ToontownGlobals.CashbotHQ, 350, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    9204: (DL_TIER + 3, Start, (CogLevelQuest, ToontownGlobals.CashbotHQ, 100, 7), Any, ToonHQ, Any, NA, DefaultDialog),
    9205: (DL_TIER + 3, Start, (CogLevelQuest, ToontownGlobals.CashbotHQ, 90, 8), Any, ToonHQ, Any, NA, DefaultDialog),
    9206: (DL_TIER + 3, Start, (CogLevelQuest, ToontownGlobals.CashbotHQ, 70, 9), Any, ToonHQ, Any, NA, DefaultDialog),
    9207: (DL_TIER + 3, Start, (CogLevelQuest, ToontownGlobals.CashbotMintIntA, 100, 10), Any, ToonHQ, Any, NA, DefaultDialog),
    9208: (DL_TIER + 3, Start, (CogLevelQuest, ToontownGlobals.CashbotMintIntB, 80, 10), Any, ToonHQ, Any, NA, DefaultDialog),
    9209: (DL_TIER + 3, Start, (CogLevelQuest, ToontownGlobals.CashbotMintIntC, 70, 11), Any, ToonHQ, Any, NA, DefaultDialog),
    9210: (DL_TIER + 3, Start, (MintQuest, ToontownGlobals.CashbotMintIntA, 15), Any, ToonHQ, Any, NA, DefaultDialog),
    9211: (DL_TIER + 3, Start, (MintQuest, ToontownGlobals.CashbotMintIntB, 10), Any, ToonHQ, Any, NA, DefaultDialog),
    9212: (DL_TIER + 3, Start, (MintQuest, ToontownGlobals.CashbotMintIntC, 7), Any, ToonHQ, Any, NA, DefaultDialog),
    9213: (DL_TIER + 3, Start, (SkelecogQuest, ToontownGlobals.CashbotMintIntA, 100), Any, ToonHQ, Any, NA, DefaultDialog),
    9214: (DL_TIER + 3, Start, (SkelecogQuest, ToontownGlobals.CashbotMintIntB, 70), Any, ToonHQ, Any, NA, DefaultDialog),
    9215: (DL_TIER + 3, Start, (SkelecogQuest, ToontownGlobals.CashbotMintIntC, 30), Any, ToonHQ, Any, NA, DefaultDialog),
    9216: (DL_TIER + 3, Start, (SupervisorQuest, ToontownGlobals.CashbotMintIntA, 25), Any, ToonHQ, Any, NA, DefaultDialog),
    9217: (DL_TIER + 3, Start, (SupervisorQuest, ToontownGlobals.CashbotMintIntB, 20), Any, ToonHQ, Any, NA, DefaultDialog),
    9218: (DL_TIER + 3, Start, (SupervisorQuest, ToontownGlobals.CashbotMintIntC, 15), Any, ToonHQ, Any, NA, DefaultDialog),
    9219: (DL_TIER + 3, Start, (BossQuest, ToontownGlobals.CashbotHQ, 3), Any, ToonHQ, 622, NA, DefaultDialog),
    9500: (DL_TIER + 3, Start, (CogQuest, ToontownGlobals.DonaldsDreamland, 1000, Any), Any, ToonHQ, NA, 9501, DefaultDialog),
    9501: (DL_TIER + 3, Cont, (DeliverItemQuest, 1000), Any, 2004, 1000, NA, DefaultDialog),
    9502: (DL_TIER + 3, Start, (BuildingQuest, Anywhere, 20, Any, 2, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    9503: (DL_TIER + 3, Start, (BuildingQuest, Anywhere, 15, Any, 3, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    9504: (DL_TIER + 3, Start, (BuildingQuest, Anywhere, 10, 's', 5, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    9505: (DL_TIER + 3, Start, (BuildingQuest, Anywhere, 10, 'l', 5, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    9506: (DL_TIER + 3, Start, (RescueQuest, InFO, 10), Any, ToonHQ, Any, NA, DefaultDialog), 
    10100: (ELDER_TIER, Start, (CogQuest, Anywhere, 50, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    10101: (ELDER_TIER, Start, (CogQuest, Anywhere, 70, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    10102: (ELDER_TIER, Start, (CogQuest, Anywhere, 80, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    10103: (ELDER_TIER, Start, (CogQuest, Anywhere, 150, Any), Any, ToonHQ, 613, NA, DefaultDialog),
    10104: (ELDER_TIER, Start, (CogQuest, Anywhere, 150, Any), Any, ToonHQ, 615, NA, DefaultDialog),
    10105: (ELDER_TIER, Start, (CogQuest, Anywhere, 200, Any), Any, ToonHQ, 616, NA, DefaultDialog),
    10106: (ELDER_TIER, Start, (CogQuest, Anywhere, 250, Any), Any, ToonHQ, 618, NA, DefaultDialog),
    10110: (ELDER_TIER, Start, (BuildingQuest, Anywhere, 30, Any, 2, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    10111: (ELDER_TIER, Start, (BuildingQuest, Anywhere, 20, Any, 3, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    10112: (ELDER_TIER, Start, (BuildingQuest, Anywhere, 15, Any, 4, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    10113: (ELDER_TIER, Start, (BuildingQuest, Anywhere, 10, Any, 5, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    10114: (ELDER_TIER, Start, (BuildingQuest, Anywhere, 10, 'm', 5, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    10115: (ELDER_TIER, Start, (BuildingQuest, Anywhere, 10, 's', 5, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    10116: (ELDER_TIER, Start, (BuildingQuest, Anywhere, 10, 'c', 5, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    10117: (ELDER_TIER, Start, (BuildingQuest, Anywhere, 10, 'l', 5, 0), Any, ToonHQ, Any, NA, DefaultDialog),
    10118: (ELDER_TIER, Start, (BuildingQuest, Anywhere, 40, Any, 1, 0), Any, ToonHQ, 620, NA, DefaultDialog),
    10123: (ELDER_TIER, Start, (BossQuest, ToontownGlobals.SellbotHQ, 2), Any, ToonHQ, Any, NA, DefaultDialog),
    10124: (ELDER_TIER, Start, (RescueQuest, InVP, 6), Any, ToonHQ, Any, NA, DefaultDialog),
    10125: (ELDER_TIER, Start, (RescueQuest, InFO, 12), Any, ToonHQ, Any, NA, DefaultDialog),
    10140: (ELDER_TIER, Start, (CogQuest, ToontownGlobals.CashbotHQ, 50, Any), Any, ToonHQ, Any, NA, DefaultDialog),
    10141: (ELDER_TIER, Start, (MintQuest, ToontownGlobals.CashbotHQ, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    10142: (ELDER_TIER, Start, (SupervisorQuest, ToontownGlobals.CashbotHQ, 5), Any, ToonHQ, Any, NA, DefaultDialog),
    10143: (ELDER_TIER, Start, (BossQuest, ToontownGlobals.CashbotHQ, 2), Any, ToonHQ, 623, NA, DefaultDialog),
    10148: (ELDER_TIER, Start, (BossQuest, ToontownGlobals.LawbotHQ, 2), Any, ToonHQ, Any, NA, DefaultDialog),
    10149: (ELDER_TIER, Start, (BossQuest, ToontownGlobals.BossbotHQ, 2), Any, ToonHQ, Any, NA, DefaultDialog),
    10150: (ELDER_TIER, Start, (BossQuest, Anywhere, 3), Any, ToonHQ, Any, NA, DefaultDialog),
    10200: (ELDER_TIER, Start, (CogQuest, Anywhere, 70, Any), Any, ToonHQ, NA, 10201, DefaultDialog),
    10201: (ELDER_TIER, Cont, (DeliverItemQuest, 1000), Any, ToonTailor, 1000, NA, DefaultDialog),
    10202: (ELDER_TIER, Start, (BuildingQuest, Anywhere, 20, Any, 1, 0), Any, ToonHQ, NA, 10203, DefaultDialog),
    10203: (ELDER_TIER, Cont, (DeliverItemQuest, 1000), Any, ToonTailor, 1000, NA, DefaultDialog),
    10208: (ELDER_TIER, Start, (BuildingQuest, Anywhere, 15, Any, 4, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    10209: (ELDER_TIER, Start, (BuildingQuest, Anywhere, 10, 's', 5, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    10210: (ELDER_TIER, Start, (BuildingQuest, Anywhere, 10, 'l', 5, 1), Any, ToonHQ, Any, NA, DefaultDialog),
    11000: (LAWBOT_HQ_TIER, Start, (VisitQuest,), Any, 3310, NA, 11001, TTLocalizer.QuestDialogDict[11000]),
    11001: (LAWBOT_HQ_TIER, Start, (RecoverItemQuest, ToontownGlobals.SillyStreet, 1, 3027, Easy, Any), Same, Same, 4100, NA, TTLocalizer.QuestDialogDict[11001]),
    11002: (LAWBOT_HQ_TIER + 1, Start, (VisitQuest,), Any, 3310, NA, 11003, TTLocalizer.QuestDialogDict[11002]),
    11003: (LAWBOT_HQ_TIER + 1, Start, (RecoverItemQuest, ToontownGlobals.LoopyLane, 1, 3027, Easy, Any), Same, Same, 4101, NA, TTLocalizer.QuestDialogDict[11003]),
    11004: (LAWBOT_HQ_TIER + 2, Start, (VisitQuest,), Any, 3310, NA, 11005, TTLocalizer.QuestDialogDict[11004]),
    11005: (LAWBOT_HQ_TIER + 2, Start, (RecoverItemQuest, ToontownGlobals.PunchlinePlace, 1, 3027, Easy, Any), Same, Same, 4102, NA, TTLocalizer.QuestDialogDict[11005]),
    11006: (LAWBOT_HQ_TIER + 3, Start, (VisitQuest,), Any, 3310, NA, 11007, TTLocalizer.QuestDialogDict[11006]),
    11007: (LAWBOT_HQ_TIER + 3, Start, (RecoverItemQuest, ToontownGlobals.BarnacleBoulevard, 1, 3027, Easy, Any), Same, Same, 4103, NA, TTLocalizer.QuestDialogDict[11007]),
    11008: (LAWBOT_HQ_TIER + 4, Start, (VisitQuest,), Any, 3310, NA, 11009, TTLocalizer.QuestDialogDict[11008]),
    11009: (LAWBOT_HQ_TIER + 4, Start, (RecoverItemQuest, ToontownGlobals.SeaweedStreet, 1, 3027, Easy, Any), Same, Same, 4104, NA, TTLocalizer.QuestDialogDict[11009]),
    11010: (LAWBOT_HQ_TIER + 5, Start, (VisitQuest,), Any, 3310, NA, 11011, TTLocalizer.QuestDialogDict[11010]),
    11011: (LAWBOT_HQ_TIER + 5, Start, (RecoverItemQuest, ToontownGlobals.LighthouseLane, 1, 3027, Easy, Any), Same, Same, 4105, NA, TTLocalizer.QuestDialogDict[11011]),
    11012: (LAWBOT_HQ_TIER + 6, Start, (VisitQuest,), Any, 3310, NA, 11013, TTLocalizer.QuestDialogDict[11012]),
    11013: (LAWBOT_HQ_TIER + 6, Start, (RecoverItemQuest, ToontownGlobals.ElmStreet, 1, 3027, Easy, Any), Same, Same, 4106, NA, TTLocalizer.QuestDialogDict[11013]),
    11014: (LAWBOT_HQ_TIER + 7, Start, (VisitQuest,), Any, 3310, NA, 11015, TTLocalizer.QuestDialogDict[11014]),
    11015: (LAWBOT_HQ_TIER + 7, Start, (RecoverItemQuest, ToontownGlobals.MapleStreet, 1, 3027, Easy, Any), Same, Same, 4107, NA, TTLocalizer.QuestDialogDict[11015]),
    11016: (LAWBOT_HQ_TIER + 8, Start, (VisitQuest,), Any, 3310, NA, 11017, TTLocalizer.QuestDialogDict[11016]),
    11017: (LAWBOT_HQ_TIER + 8, Start, (RecoverItemQuest, ToontownGlobals.OakStreet, 1, 3027, Easy, Any), Same, Same, 4108, NA, TTLocalizer.QuestDialogDict[11017]),
    11018: (LAWBOT_HQ_TIER + 9, Start, (VisitQuest,), Any, 3310, NA, 11019, TTLocalizer.QuestDialogDict[11018]),
    11019: (LAWBOT_HQ_TIER + 9, Start, (RecoverItemQuest, ToontownGlobals.AltoAvenue, 1, 3027, VeryEasy, Any), Same, Same, 4109, NA, TTLocalizer.QuestDialogDict[11019]),
    11020: (LAWBOT_HQ_TIER + 10, Start, (VisitQuest,), Any, 3310, NA, 11021, TTLocalizer.QuestDialogDict[11020]),
    11021: (LAWBOT_HQ_TIER + 10, Start, (RecoverItemQuest, ToontownGlobals.BaritoneBoulevard, 1, 3027, Easy, Any), Same, Same, 4110, NA, TTLocalizer.QuestDialogDict[11021]),
    11022: (LAWBOT_HQ_TIER + 11, Start, (VisitQuest,), Any, 3310, NA, 11023, TTLocalizer.QuestDialogDict[11022]),
    11023: (LAWBOT_HQ_TIER + 11, Start, (RecoverItemQuest, ToontownGlobals.TenorTerrace, 1, 3027, Medium, Any), Same, Same, 4111, 4112, 4113, NA, TTLocalizer.QuestDialogDict[11023]),
    12000: (BOSSBOT_HQ_TIER, Start, (VisitQuest,), Any, 1222, NA, 12001, TTLocalizer.QuestDialogDict[12000]),
    12001: (BOSSBOT_HQ_TIER, Start, (CogQuest, Anywhere, 1, 'f'), Same, Same, 4200, NA, TTLocalizer.QuestDialogDict[12001]),
    12002: (BOSSBOT_HQ_TIER + 1, Start, (VisitQuest,), Any, 1222, NA, 12003, TTLocalizer.QuestDialogDict[12002]),
    12003: (BOSSBOT_HQ_TIER + 1, Start, (CogQuest, Anywhere, 1, 'p'), Same, Same, 4201, NA, TTLocalizer.QuestDialogDict[12003]),
    12004: (BOSSBOT_HQ_TIER + 2, Start, (VisitQuest,), Any, 1222, NA, 12005, TTLocalizer.QuestDialogDict[12004]),
    12005: (BOSSBOT_HQ_TIER + 2, Start, (CogQuest, Anywhere, 1, 'ym'), Same, Same, 4202, NA, TTLocalizer.QuestDialogDict[12005]),
    12006: (BOSSBOT_HQ_TIER + 3, Start, (VisitQuest,), Any, 1222, NA, 12007, TTLocalizer.QuestDialogDict[12006]),
    12007: (BOSSBOT_HQ_TIER + 3, Start, (CogQuest, Anywhere, 1, 'mm'), Same, Same, 4203, NA, TTLocalizer.QuestDialogDict[12007]),
    12008: (BOSSBOT_HQ_TIER + 4, Start, (VisitQuest,), Any, 1222, NA, 12009, TTLocalizer.QuestDialogDict[12008]),
    12009: (BOSSBOT_HQ_TIER + 4, Start, (CogQuest, Anywhere, 1, 'ds'), Same, Same, 4204, NA, TTLocalizer.QuestDialogDict[12009]),
    12010: (BOSSBOT_HQ_TIER + 5, Start, (VisitQuest,), Any, 1222, NA, 12011, TTLocalizer.QuestDialogDict[12010]),
    12011: (BOSSBOT_HQ_TIER + 5, Start, (CogQuest, Anywhere, 1, 'hh'), Same, Same, 4205, NA, TTLocalizer.QuestDialogDict[12011]),
    12012: (BOSSBOT_HQ_TIER + 6, Start, (VisitQuest,), Any, 1222, NA, 12013, TTLocalizer.QuestDialogDict[12012]),
    12013: (BOSSBOT_HQ_TIER + 6, Start, (CogQuest, Anywhere, 1, 'cr'), Same, Same, 4206, NA, TTLocalizer.QuestDialogDict[12013]),
    12014: (BOSSBOT_HQ_TIER + 7, Start, (VisitQuest,), Any, 1222, NA, 12015, TTLocalizer.QuestDialogDict[12014]),
    12015: (BOSSBOT_HQ_TIER + 7, Start, (CogQuest, Anywhere, 1, 'tbc'), Same, Same, 4207, NA, TTLocalizer.QuestDialogDict[12015]),
    12016: (BOSSBOT_HQ_TIER + 8, Start, (VisitQuest,), Any, 1222, NA, 12017, TTLocalizer.QuestDialogDict[12016]),
    12017: (BOSSBOT_HQ_TIER + 8, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4208, NA, TTLocalizer.QuestDialogDict[12017]),
    12018: (BOSSBOT_HQ_TIER + 9, Start, (VisitQuest,), Any, 1222, NA, 12019, TTLocalizer.QuestDialogDict[12018]),
    12019: (BOSSBOT_HQ_TIER + 9, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4209, 4210, 4211, 4212, 4213, 4214, NA, TTLocalizer.QuestDialogDict[12019]),
    12030: (BOSSBOT_HQ_TIER + 15, Start, (VisitQuest,), Any, 1222, NA, 12031, TTLocalizer.QuestDialogDict[12030]),
    12031: (BOSSBOT_HQ_TIER + 15, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4215, NA, TTLocalizer.QuestDialogDict[12031]),
    12032: (BOSSBOT_HQ_TIER + 16, Start, (VisitQuest,), Any, 2001, 4216, NA, TTLocalizer.QuestDialogDict[12032]),
    12035: (GOVERNBOT_HQ_TIER, Start, (VisitQuest,), Any, 1222, NA, 12036, TTLocalizer.QuestDialogDict[12000]),
    12036: (GOVERNBOT_HQ_TIER, Start, (CogQuest, Anywhere, 1, 'f'), Same, Same, 4300, NA, TTLocalizer.QuestDialogDict[12001]),
    12037: (GOVERNBOT_HQ_TIER + 1, Start, (VisitQuest,), Any, 1222, NA, 12038, TTLocalizer.QuestDialogDict[12002]),
    12038: (GOVERNBOT_HQ_TIER + 1, Start, (CogQuest, Anywhere, 1, 'p'), Same, Same, 4301, NA, TTLocalizer.QuestDialogDict[12003]),
    12039: (GOVERNBOT_HQ_TIER + 2, Start, (VisitQuest,), Any, 1222, NA, 12040, TTLocalizer.QuestDialogDict[12004]),
    12040: (GOVERNBOT_HQ_TIER + 2, Start, (CogQuest, Anywhere, 1, 'ym'), Same, Same, 4302, NA, TTLocalizer.QuestDialogDict[12005]),
    12041: (GOVERNBOT_HQ_TIER + 3, Start, (VisitQuest,), Any, 1222, NA, 12042, TTLocalizer.QuestDialogDict[12006]),
    12042: (GOVERNBOT_HQ_TIER + 3, Start, (CogQuest, Anywhere, 1, 'mm'), Same, Same, 4303, NA, TTLocalizer.QuestDialogDict[12007]),
    12043: (GOVERNBOT_HQ_TIER + 4, Start, (VisitQuest,), Any, 1222, NA, 12044, TTLocalizer.QuestDialogDict[12008]),
    12044: (GOVERNBOT_HQ_TIER + 4, Start, (CogQuest, Anywhere, 1, 'ds'), Same, Same, 4304, NA, TTLocalizer.QuestDialogDict[12009]),
    12045: (GOVERNBOT_HQ_TIER + 5, Start, (VisitQuest,), Any, 1222, NA, 12046, TTLocalizer.QuestDialogDict[12010]),
    12046: (GOVERNBOT_HQ_TIER + 5, Start, (CogQuest, Anywhere, 1, 'hh'), Same, Same, 4305, NA, TTLocalizer.QuestDialogDict[12011]),
    12047: (GOVERNBOT_HQ_TIER + 6, Start, (VisitQuest,), Any, 1222, NA, 12048, TTLocalizer.QuestDialogDict[12012]),
    12048: (GOVERNBOT_HQ_TIER + 6, Start, (CogQuest, Anywhere, 1, 'cr'), Same, Same, 4306, NA, TTLocalizer.QuestDialogDict[12013]),
    12049: (GOVERNBOT_HQ_TIER + 7, Start, (VisitQuest,), Any, 1222, NA, 12050, TTLocalizer.QuestDialogDict[12014]),
    12050: (GOVERNBOT_HQ_TIER + 7, Start, (CogQuest, Anywhere, 1, 'tbc'), Same, Same, 4307, NA, TTLocalizer.QuestDialogDict[12015]),
    12051: (GOVERNBOT_HQ_TIER + 8, Start, (VisitQuest,), Any, 1222, NA, 12052, TTLocalizer.QuestDialogDict[12016]),
    12052: (GOVERNBOT_HQ_TIER + 8, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4308, NA, TTLocalizer.QuestDialogDict[12017]),
    12053: (GOVERNBOT_HQ_TIER + 9, Start, (VisitQuest,), Any, 1222, NA, 12054, TTLocalizer.QuestDialogDict[12018]),
    12054: (GOVERNBOT_HQ_TIER + 9, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4309, NA, TTLocalizer.QuestDialogDict[12019]),
    12055: (GOVERNBOT_HQ_TIER + 10, Start, (VisitQuest,), Any, 1222, NA, 12056, TTLocalizer.QuestDialogDict[12018]),
    12056: (GOVERNBOT_HQ_TIER + 10, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4310, NA, TTLocalizer.QuestDialogDict[12019]),
    12057: (GOVERNBOT_HQ_TIER + 11, Start, (VisitQuest,), Any, 1222, NA, 12058, TTLocalizer.QuestDialogDict[12018]),
    12058: (GOVERNBOT_HQ_TIER + 11, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4311, NA, TTLocalizer.QuestDialogDict[12019]),
    12059: (GOVERNBOT_HQ_TIER + 12, Start, (VisitQuest,), Any, 1222, NA, 12060, TTLocalizer.QuestDialogDict[12018]),
    12060: (GOVERNBOT_HQ_TIER + 12, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4312, NA, TTLocalizer.QuestDialogDict[12019]),
    12061: (GOVERNBOT_HQ_TIER + 13, Start, (VisitQuest,), Any, 1222, NA, 12062, TTLocalizer.QuestDialogDict[12018]),
    12062: (GOVERNBOT_HQ_TIER + 13, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4313, NA, TTLocalizer.QuestDialogDict[12019]),
    12063: (GOVERNBOT_HQ_TIER + 14, Start, (VisitQuest,), Any, 1222, NA, 12064, TTLocalizer.QuestDialogDict[12018]),
    12064: (GOVERNBOT_HQ_TIER + 14, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4314, NA, TTLocalizer.QuestDialogDict[12019]),
    12065: (GOVERNBOT_HQ_TIER + 15, Start, (VisitQuest,), Any, 1222, NA, 12066, TTLocalizer.QuestDialogDict[12030]),
    12066: (GOVERNBOT_HQ_TIER + 15, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4315, NA, TTLocalizer.QuestDialogDict[12031]),
    12067: (GOVERNBOT_HQ_TIER + 16, Start, (VisitQuest,), Any, 2001, 4316, NA, TTLocalizer.QuestDialogDict[12032]),

    12068: (EUREKABOT_HQ_TIER, Start, (VisitQuest,), Any, 1222, NA, 12069, TTLocalizer.QuestDialogDict[12000]),
    12069: (EUREKABOT_HQ_TIER, Start, (CogQuest, Anywhere, 1, 'f'), Same, Same, 4400, NA, TTLocalizer.QuestDialogDict[12001]),
    12070: (EUREKABOT_HQ_TIER + 1, Start, (VisitQuest,), Any, 1222, NA, 12071, TTLocalizer.QuestDialogDict[12002]),
    12071: (EUREKABOT_HQ_TIER + 1, Start, (CogQuest, Anywhere, 1, 'p'), Same, Same, 4401, NA, TTLocalizer.QuestDialogDict[12003]),
    12072: (EUREKABOT_HQ_TIER + 2, Start, (VisitQuest,), Any, 1222, NA, 12073, TTLocalizer.QuestDialogDict[12004]),
    12073: (EUREKABOT_HQ_TIER + 2, Start, (CogQuest, Anywhere, 1, 'ym'), Same, Same, 4402, NA, TTLocalizer.QuestDialogDict[12005]),
    12074: (EUREKABOT_HQ_TIER + 3, Start, (VisitQuest,), Any, 1222, NA, 12075, TTLocalizer.QuestDialogDict[12006]),
    12075: (EUREKABOT_HQ_TIER + 3, Start, (CogQuest, Anywhere, 1, 'mm'), Same, Same, 4403, NA, TTLocalizer.QuestDialogDict[12007]),
    12076: (EUREKABOT_HQ_TIER + 4, Start, (VisitQuest,), Any, 1222, NA, 12077, TTLocalizer.QuestDialogDict[12008]),
    12077: (EUREKABOT_HQ_TIER + 4, Start, (CogQuest, Anywhere, 1, 'ds'), Same, Same, 4404, NA, TTLocalizer.QuestDialogDict[12009]),
    12078: (EUREKABOT_HQ_TIER + 5, Start, (VisitQuest,), Any, 1222, NA, 12079, TTLocalizer.QuestDialogDict[12010]),
    12079: (EUREKABOT_HQ_TIER + 5, Start, (CogQuest, Anywhere, 1, 'hh'), Same, Same, 4405, NA, TTLocalizer.QuestDialogDict[12011]),
    12080: (EUREKABOT_HQ_TIER + 6, Start, (VisitQuest,), Any, 1222, NA, 12081, TTLocalizer.QuestDialogDict[12012]),
    12081: (EUREKABOT_HQ_TIER + 6, Start, (CogQuest, Anywhere, 1, 'cr'), Same, Same, 4406, NA, TTLocalizer.QuestDialogDict[12013]),
    12082: (EUREKABOT_HQ_TIER + 7, Start, (VisitQuest,), Any, 1222, NA, 12083, TTLocalizer.QuestDialogDict[12014]),
    12083: (EUREKABOT_HQ_TIER + 7, Start, (CogQuest, Anywhere, 1, 'tbc'), Same, Same, 4407, NA, TTLocalizer.QuestDialogDict[12015]),
    12084: (EUREKABOT_HQ_TIER + 8, Start, (VisitQuest,), Any, 1222, NA, 12085, TTLocalizer.QuestDialogDict[12016]),
    12085: (EUREKABOT_HQ_TIER + 8, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4408, NA, TTLocalizer.QuestDialogDict[12017]),
    12086: (EUREKABOT_HQ_TIER + 9, Start, (VisitQuest,), Any, 1222, NA, 12087, TTLocalizer.QuestDialogDict[12018]),
    12087: (EUREKABOT_HQ_TIER + 9, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4409, NA, TTLocalizer.QuestDialogDict[12019]),
    12088: (EUREKABOT_HQ_TIER + 10, Start, (VisitQuest,), Any, 1222, NA, 12089, TTLocalizer.QuestDialogDict[12018]),
    12089: (EUREKABOT_HQ_TIER + 10, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4410, NA, TTLocalizer.QuestDialogDict[12019]),
    12090: (EUREKABOT_HQ_TIER + 11, Start, (VisitQuest,), Any, 1222, NA, 12091, TTLocalizer.QuestDialogDict[12018]),
    12091: (EUREKABOT_HQ_TIER + 11, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4411, NA, TTLocalizer.QuestDialogDict[12019]),
    12092: (EUREKABOT_HQ_TIER + 12, Start, (VisitQuest,), Any, 1222, NA, 12093, TTLocalizer.QuestDialogDict[12018]),
    12093: (EUREKABOT_HQ_TIER + 12, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4412, NA, TTLocalizer.QuestDialogDict[12019]),
    12094: (EUREKABOT_HQ_TIER + 13, Start, (VisitQuest,), Any, 1222, NA, 12095, TTLocalizer.QuestDialogDict[12018]),
    12095: (EUREKABOT_HQ_TIER + 13, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4413, NA, TTLocalizer.QuestDialogDict[12019]),
    12096: (EUREKABOT_HQ_TIER + 14, Start, (VisitQuest,), Any, 1222, NA, 12097, TTLocalizer.QuestDialogDict[12018]),
    12097: (EUREKABOT_HQ_TIER + 14, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4414, NA, TTLocalizer.QuestDialogDict[12019]),
    12098: (EUREKABOT_HQ_TIER + 15, Start, (VisitQuest,), Any, 1222, NA, 12099, TTLocalizer.QuestDialogDict[12030]),
    12099: (EUREKABOT_HQ_TIER + 15, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4415, NA, TTLocalizer.QuestDialogDict[12031]),
    13000: (EUREKABOT_HQ_TIER + 16, Start, (VisitQuest,), Any, 2001, 4416, NA, TTLocalizer.QuestDialogDict[12032]),

    13001: (BUILDBOT_HQ_TIER, Start, (VisitQuest,), Any, 1222, NA, 13002, TTLocalizer.QuestDialogDict[12000]),
    13002: (BUILDBOT_HQ_TIER, Start, (CogQuest, Anywhere, 1, 'f'), Same, Same, 4500, NA, TTLocalizer.QuestDialogDict[12001]),
    13003: (BUILDBOT_HQ_TIER + 1, Start, (VisitQuest,), Any, 1222, NA, 13004, TTLocalizer.QuestDialogDict[12002]),
    13004: (BUILDBOT_HQ_TIER + 1, Start, (CogQuest, Anywhere, 1, 'p'), Same, Same, 4501, NA, TTLocalizer.QuestDialogDict[12003]),
    13005: (BUILDBOT_HQ_TIER + 2, Start, (VisitQuest,), Any, 1222, NA, 13006, TTLocalizer.QuestDialogDict[12004]),
    13006: (BUILDBOT_HQ_TIER + 2, Start, (CogQuest, Anywhere, 1, 'ym'), Same, Same, 4502, NA, TTLocalizer.QuestDialogDict[12005]),
    13007: (BUILDBOT_HQ_TIER + 3, Start, (VisitQuest,), Any, 1222, NA, 13008, TTLocalizer.QuestDialogDict[12006]),
    13008: (BUILDBOT_HQ_TIER + 3, Start, (CogQuest, Anywhere, 1, 'mm'), Same, Same, 4503, NA, TTLocalizer.QuestDialogDict[12007]),
    13009: (BUILDBOT_HQ_TIER + 4, Start, (VisitQuest,), Any, 1222, NA, 13010, TTLocalizer.QuestDialogDict[12008]),
    13010: (BUILDBOT_HQ_TIER + 4, Start, (CogQuest, Anywhere, 1, 'ds'), Same, Same, 4504, NA, TTLocalizer.QuestDialogDict[12009]),
    13011: (BUILDBOT_HQ_TIER + 5, Start, (VisitQuest,), Any, 1222, NA, 13012, TTLocalizer.QuestDialogDict[12010]),
    13012: (BUILDBOT_HQ_TIER + 5, Start, (CogQuest, Anywhere, 1, 'hh'), Same, Same, 4505, NA, TTLocalizer.QuestDialogDict[12011]),
    13013: (BUILDBOT_HQ_TIER + 6, Start, (VisitQuest,), Any, 1222, NA, 13014, TTLocalizer.QuestDialogDict[12012]),
    13014: (BUILDBOT_HQ_TIER + 6, Start, (CogQuest, Anywhere, 1, 'cr'), Same, Same, 4506, NA, TTLocalizer.QuestDialogDict[12013]),
    13015: (BUILDBOT_HQ_TIER + 7, Start, (VisitQuest,), Any, 1222, NA, 13016, TTLocalizer.QuestDialogDict[12014]),
    13016: (BUILDBOT_HQ_TIER + 7, Start, (CogQuest, Anywhere, 1, 'tbc'), Same, Same, 4507, NA, TTLocalizer.QuestDialogDict[12015]),
    13017: (BUILDBOT_HQ_TIER + 8, Start, (VisitQuest,), Any, 1222, NA, 13018, TTLocalizer.QuestDialogDict[12016]),
    13018: (BUILDBOT_HQ_TIER + 8, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4508, NA, TTLocalizer.QuestDialogDict[12017]),
    13019: (BUILDBOT_HQ_TIER + 9, Start, (VisitQuest,), Any, 1222, NA, 13020, TTLocalizer.QuestDialogDict[12018]),
    13020: (BUILDBOT_HQ_TIER + 9, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4509, NA, TTLocalizer.QuestDialogDict[12019]),
    13021: (BUILDBOT_HQ_TIER + 10, Start, (VisitQuest,), Any, 1222, NA, 13022, TTLocalizer.QuestDialogDict[12018]),
    13022: (BUILDBOT_HQ_TIER + 10, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4510, NA, TTLocalizer.QuestDialogDict[12019]),
    13023: (BUILDBOT_HQ_TIER + 11, Start, (VisitQuest,), Any, 1222, NA, 13024, TTLocalizer.QuestDialogDict[12018]),
    13024: (BUILDBOT_HQ_TIER + 11, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4511, NA, TTLocalizer.QuestDialogDict[12019]),
    13025: (BUILDBOT_HQ_TIER + 12, Start, (VisitQuest,), Any, 1222, NA, 13026, TTLocalizer.QuestDialogDict[12018]),
    13026: (BUILDBOT_HQ_TIER + 12, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4512, NA, TTLocalizer.QuestDialogDict[12019]),
    13027: (BUILDBOT_HQ_TIER + 13, Start, (VisitQuest,), Any, 1222, NA, 13028, TTLocalizer.QuestDialogDict[12018]),
    13028: (BUILDBOT_HQ_TIER + 13, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4513, NA, TTLocalizer.QuestDialogDict[12019]),
    13029: (BUILDBOT_HQ_TIER + 14, Start, (VisitQuest,), Any, 1222, NA, 13030, TTLocalizer.QuestDialogDict[12018]),
    13030: (BUILDBOT_HQ_TIER + 14, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4514, NA, TTLocalizer.QuestDialogDict[12019]),
    13031: (BUILDBOT_HQ_TIER + 15, Start, (VisitQuest,), Any, 1222, NA, 13032, TTLocalizer.QuestDialogDict[12030]),
    13032: (BUILDBOT_HQ_TIER + 15, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4515, NA, TTLocalizer.QuestDialogDict[12031]),
    13033: (BUILDBOT_HQ_TIER + 16, Start, (VisitQuest,), Any, 2001, 4516, NA, TTLocalizer.QuestDialogDict[12032]),

    13034: (VIRALBOT_HQ_TIER, Start, (VisitQuest,), Any, 1222, NA, 13035, TTLocalizer.QuestDialogDict[12000]),
    13035: (VIRALBOT_HQ_TIER, Start, (CogQuest, Anywhere, 1, 'f'), Same, Same, 4600, NA, TTLocalizer.QuestDialogDict[12001]),
    13036: (VIRALBOT_HQ_TIER + 1, Start, (VisitQuest,), Any, 1222, NA, 13037, TTLocalizer.QuestDialogDict[12002]),
    13037: (VIRALBOT_HQ_TIER + 1, Start, (CogQuest, Anywhere, 1, 'p'), Same, Same, 4601, NA, TTLocalizer.QuestDialogDict[12003]),
    13038: (VIRALBOT_HQ_TIER + 2, Start, (VisitQuest,), Any, 1222, NA, 13039, TTLocalizer.QuestDialogDict[12004]),
    13039: (VIRALBOT_HQ_TIER + 2, Start, (CogQuest, Anywhere, 1, 'ym'), Same, Same, 4602, NA, TTLocalizer.QuestDialogDict[12005]),
    13040: (VIRALBOT_HQ_TIER + 3, Start, (VisitQuest,), Any, 1222, NA, 13041, TTLocalizer.QuestDialogDict[12006]),
    13041: (VIRALBOT_HQ_TIER + 3, Start, (CogQuest, Anywhere, 1, 'mm'), Same, Same, 4603, NA, TTLocalizer.QuestDialogDict[12007]),
    13042: (VIRALBOT_HQ_TIER + 4, Start, (VisitQuest,), Any, 1222, NA, 13043, TTLocalizer.QuestDialogDict[12008]),
    13043: (VIRALBOT_HQ_TIER + 4, Start, (CogQuest, Anywhere, 1, 'ds'), Same, Same, 4604, NA, TTLocalizer.QuestDialogDict[12009]),
    13044: (VIRALBOT_HQ_TIER + 5, Start, (VisitQuest,), Any, 1222, NA, 13045, TTLocalizer.QuestDialogDict[12010]),
    13045: (VIRALBOT_HQ_TIER + 5, Start, (CogQuest, Anywhere, 1, 'hh'), Same, Same, 4605, NA, TTLocalizer.QuestDialogDict[12011]),
    13046: (VIRALBOT_HQ_TIER + 6, Start, (VisitQuest,), Any, 1222, NA, 13047, TTLocalizer.QuestDialogDict[12012]),
    13047: (VIRALBOT_HQ_TIER + 6, Start, (CogQuest, Anywhere, 1, 'cr'), Same, Same, 4606, NA, TTLocalizer.QuestDialogDict[12013]),
    13048: (VIRALBOT_HQ_TIER + 7, Start, (VisitQuest,), Any, 1222, NA, 13049, TTLocalizer.QuestDialogDict[12014]),
    13049: (VIRALBOT_HQ_TIER + 7, Start, (CogQuest, Anywhere, 1, 'tbc'), Same, Same, 4607, NA, TTLocalizer.QuestDialogDict[12015]),
    13050: (VIRALBOT_HQ_TIER + 8, Start, (VisitQuest,), Any, 1222, NA, 13051, TTLocalizer.QuestDialogDict[12016]),
    13051: (VIRALBOT_HQ_TIER + 8, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4608, NA, TTLocalizer.QuestDialogDict[12017]),
    13052: (VIRALBOT_HQ_TIER + 9, Start, (VisitQuest,), Any, 1222, NA, 13053, TTLocalizer.QuestDialogDict[12018]),
    13053: (VIRALBOT_HQ_TIER + 9, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4609, NA, TTLocalizer.QuestDialogDict[12019]),
    13054: (VIRALBOT_HQ_TIER + 10, Start, (VisitQuest,), Any, 1222, NA, 13055, TTLocalizer.QuestDialogDict[12018]),
    13055: (VIRALBOT_HQ_TIER + 10, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4610, NA, TTLocalizer.QuestDialogDict[12019]),
    13056: (VIRALBOT_HQ_TIER + 11, Start, (VisitQuest,), Any, 1222, NA, 13057, TTLocalizer.QuestDialogDict[12018]),
    13057: (VIRALBOT_HQ_TIER + 11, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4611, NA, TTLocalizer.QuestDialogDict[12019]),
    13058: (VIRALBOT_HQ_TIER + 12, Start, (VisitQuest,), Any, 1222, NA, 13059, TTLocalizer.QuestDialogDict[12018]),
    13059: (VIRALBOT_HQ_TIER + 12, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4612, NA, TTLocalizer.QuestDialogDict[12019]),
    13060: (VIRALBOT_HQ_TIER + 13, Start, (VisitQuest,), Any, 1222, NA, 13061, TTLocalizer.QuestDialogDict[12018]),
    13061: (VIRALBOT_HQ_TIER + 13, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4613, NA, TTLocalizer.QuestDialogDict[12019]),
    13062: (VIRALBOT_HQ_TIER + 14, Start, (VisitQuest,), Any, 1222, NA, 13063, TTLocalizer.QuestDialogDict[12018]),
    13063: (VIRALBOT_HQ_TIER + 14, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4614, NA, TTLocalizer.QuestDialogDict[12019]),
    13064: (VIRALBOT_HQ_TIER + 15, Start, (VisitQuest,), Any, 1222, NA, 13065, TTLocalizer.QuestDialogDict[12030]),
    13065: (VIRALBOT_HQ_TIER + 15, Start, (SkeleReviveQuest, Anywhere, 1), Same, Same, 4615, NA, TTLocalizer.QuestDialogDict[12031]),
    13066: (VIRALBOT_HQ_TIER + 16, Start, (VisitQuest,), Any, 2001, 4616, NA, TTLocalizer.QuestDialogDict[12032])}



Tier2QuestsDict = {}

for questId, questDesc in QuestDict.items():
    if questDesc[QuestDictStartIndex] == Start:
        tier = questDesc[QuestDictTierIndex]
        if tier in Tier2QuestsDict:
            Tier2QuestsDict[tier].append(questId)
        else:
            Tier2QuestsDict[tier] = [questId]

Quest2RewardDict = {}
Tier2Reward2QuestsDict = {}
Quest2RemainingStepsDict = {}

def getAllRewardIdsForReward(rewardId):
    if rewardId is AnyCashbotSuitPart:
        return range(4000, 4011 + 1)
    if rewardId is AnyLawbotSuitPart:
        return range(4100, 4113 + 1)
    if rewardId is AnyBossbotSuitPart:
        return range(4200, 4216 + 1)
    if rewardId is AnyGovernbotSuitPart:
        return range(4300, 4316 + 1)
    if rewardId is AnyEurekabotSuitPart:
        return range(4400, 4416 + 1)
    if rewardId is AnyBuildbotSuitPart:
        return range(4500, 4516 + 1)
    if rewardId is AnyViralbotSuitPart:
        return range(4600, 4616 + 1)
    return (rewardId,)

def findFinalRewardId(questId):
    finalRewardId = Quest2RewardDict.get(questId)
    if finalRewardId:
        remainingSteps = Quest2RemainingStepsDict.get(questId)
    else:
        try:
            questDesc = QuestDict[questId]
        except KeyError:
            print 'findFinalRewardId: Quest ID: %d not found' % questId
            return -1

        nextQuestId = questDesc[QuestDictNextQuestIndex]
        if nextQuestId == NA:
            finalRewardId = questDesc[QuestDictRewardIndex]
            remainingSteps = 1
        else:
            if type(nextQuestId) == type(()):
                finalRewardId, remainingSteps = findFinalRewardId(nextQuestId[0])
                for id in nextQuestId[1:]:
                    findFinalRewardId(id)

            else:
                finalRewardId, remainingSteps = findFinalRewardId(nextQuestId)
            remainingSteps += 1
        if finalRewardId != OBSOLETE:
            if questDesc[QuestDictStartIndex] == Start:
                tier = questDesc[QuestDictTierIndex]
                tier2RewardDict = Tier2Reward2QuestsDict.setdefault(tier, {})
                rewardIds = getAllRewardIdsForReward(finalRewardId)
                for rewardId in rewardIds:
                    questList = tier2RewardDict.setdefault(rewardId, [])
                    questList.append(questId)

        else:
            finalRewardId = None
        Quest2RewardDict[questId] = finalRewardId
        Quest2RemainingStepsDict[questId] = remainingSteps
    return (finalRewardId, remainingSteps)


for questId in QuestDict.keys():
    findFinalRewardId(questId)

def getStartingQuests(tier = None):
    startingQuests = []
    for questId in QuestDict.keys():
        if isStartingQuest(questId):
            if tier is None:
                startingQuests.append(questId)
            elif questId in Tier2QuestsDict[tier]:
                startingQuests.append(questId)

    startingQuests.sort()
    return startingQuests


def getFinalRewardId(questId, fAll = 0):
    if fAll or isStartingQuest(questId):
        return Quest2RewardDict.get(questId)
    else:
        return None
    return None


def isStartingQuest(questId):
    try:
        return QuestDict[questId][QuestDictStartIndex] == Start
    except KeyError:
        return None

    return None


def getNumChoices(tier):
    if tier in (0,):
        return 0
    if tier in (1,):
        return 2
    else:
        return 3


def getAvatarRewardId(av, questId):
    for quest in av.quests:
        if questId == quest[0]:
            return quest[3]

    notify.warning('getAvatarRewardId(): quest not found on avatar')
    return None


def getNextQuest(id, currentNpc, av):
    validTrackTiers = [MM_TIER, BR_TIER, DD_TIER, TT_TIER + 1]
    nextQuest = QuestDict[id][QuestDictNextQuestIndex]
    if nextQuest == NA:
        return (NA, NA)
    elif type(nextQuest) == type(()):
        nextReward = QuestDict[nextQuest[0]][QuestDictRewardIndex]
        nextNextQuest, nextNextToNpcId = getNextQuest(nextQuest[0], currentNpc, av)
        if nextReward == 400 and nextNextQuest == NA and av.getRewardTier() in validTrackTiers:
            nextQuest = chooseTrackChoiceQuest(av.getRewardTier(), av)
        else:
            nextQuest = random.choice(nextQuest)
    if not getQuestClass(nextQuest).filterFunc(av):
        return getNextQuest(nextQuest, currentNpc, av)
    nextToNpcId = getQuestToNpcId(nextQuest)
    if nextToNpcId == Any:
        nextToNpcId = 2004
    elif nextToNpcId == Same:
        if currentNpc.getHq():
            nextToNpcId = ToonHQ
        else:
            nextToNpcId = currentNpc.getNpcId()
    elif nextToNpcId == ToonHQ:
        nextToNpcId = ToonHQ
    return (nextQuest, nextToNpcId)


def filterQuests(entireQuestPool, currentNpc, av):
    if notify.getDebug():
        notify.debug('filterQuests: entireQuestPool: %s' % entireQuestPool)
    validQuestPool = dict([ (questId, 1) for questId in entireQuestPool ])
    if isLoopingFinalTier(av.getRewardTier()):
        history = map(lambda questDesc: questDesc[0], av.quests)
    else:
        history = av.getQuestHistory()
    if notify.getDebug():
        notify.debug('filterQuests: av quest history: %s' % history)
    currentQuests = av.quests
    for questId in entireQuestPool:
        if questId in history:
            if notify.getDebug():
                notify.debug('filterQuests: Removed %s because in history' % questId)
            validQuestPool[questId] = 0
            continue
        potentialFromNpc = getQuestFromNpcId(questId)
        if not npcMatches(potentialFromNpc, currentNpc):
            if notify.getDebug():
                notify.debug('filterQuests: Removed %s: potentialFromNpc does not match currentNpc' % questId)
            validQuestPool[questId] = 0
            continue
        potentialToNpc = getQuestToNpcId(questId)
        if currentNpc.getNpcId() == potentialToNpc:
            if notify.getDebug():
                notify.debug('filterQuests: Removed %s because potentialToNpc is currentNpc' % questId)
            validQuestPool[questId] = 0
            continue
        if not getQuestClass(questId).filterFunc(av):
            if notify.getDebug():
                notify.debug('filterQuests: Removed %s because of filterFunc' % questId)
            validQuestPool[questId] = 0
            continue
        for quest in currentQuests:
            fromNpcId = quest[1]
            toNpcId = quest[2]
            if potentialToNpc == toNpcId and toNpcId != ToonHQ:
                validQuestPool[questId] = 0
                if notify.getDebug():
                    notify.debug('filterQuests: Removed %s because npc involved' % questId)
                break

    finalQuestPool = filter(lambda key: validQuestPool[key], validQuestPool.keys())
    if notify.getDebug():
        notify.debug('filterQuests: finalQuestPool: %s' % finalQuestPool)
    return finalQuestPool


def chooseTrackChoiceQuest(tier, av, fixed = 0):

    def fixAndCallAgain():
        if not fixed and av.fixTrackAccess():
            notify.info('av %s trackAccess fixed: %s' % (av.getDoId(), trackAccess))
            return chooseTrackChoiceQuest(tier, av, fixed=1)
        else:
            return None
        return None

    bestQuest = None
    trackAccess = av.getTrackAccess()
    if tier == MM_TIER:
        if trackAccess[ToontownBattleGlobals.HEAL_TRACK] == 1:
            if trackAccess[ToontownBattleGlobals.LURE_TRACK] == 1:
                bestQuest = 4004
            elif trackAccess[ToontownBattleGlobals.TRAP_TRACK] == 1:
                bestQuest = 4003
            else:
                notify.warning('av %s has bogus trackAccess: %s' % (av.getDoId(), trackAccess))
                return fixAndCallAgain()
        elif trackAccess[ToontownBattleGlobals.SOUND_TRACK] == 1:
            if trackAccess[ToontownBattleGlobals.LURE_TRACK] == 1:
                bestQuest = 4002
            elif trackAccess[ToontownBattleGlobals.TRAP_TRACK] == 1:
                bestQuest = 4001
            else:
                notify.warning('av %s has bogus trackAccess: %s' % (av.getDoId(), trackAccess))
                return fixAndCallAgain()
    elif tier == BR_TIER:
        if trackAccess[ToontownBattleGlobals.TRAP_TRACK] == 0:
            bestQuest = 5004
        elif trackAccess[ToontownBattleGlobals.HEAL_TRACK] == 0:
            bestQuest = 5003
        elif trackAccess[ToontownBattleGlobals.LURE_TRACK] == 0:
            bestQuest = 5002
        elif trackAccess[ToontownBattleGlobals.SOUND_TRACK] == 0:
            bestQuest = 5001
        else:
            notify.warning('av %s has bogus trackAccess: %s' % (av.getDoId(), trackAccess))
            return fixAndCallAgain()
    else:
        if notify.getDebug():
            notify.debug('questPool for reward 400 had no dynamic choice, tier: %s' % tier)
        bestQuest = seededRandomChoice(Tier2Reward2QuestsDict[tier][400])
    if notify.getDebug():
        notify.debug('chooseTrackChoiceQuest: avId: %s trackAccess: %s tier: %s bestQuest: %s' % (av.getDoId(),
         trackAccess,
         tier,
         bestQuest))
    return bestQuest  


def chooseMatchingQuest(tier, validQuestPool, rewardId, npc, av):
    questsMatchingReward = Tier2Reward2QuestsDict[tier].get(rewardId, [])
    if notify.getDebug():
        notify.debug('questsMatchingReward: %s tier: %s = %s' % (rewardId, tier, questsMatchingReward))
    if rewardId == 400 and QuestDict[questsMatchingReward[0]][QuestDictNextQuestIndex] == NA:
        bestQuest = chooseTrackChoiceQuest(tier, av)
        if notify.getDebug():
            notify.debug('single part track choice quest: %s tier: %s avId: %s trackAccess: %s bestQuest: %s' % (rewardId,
             tier,
             av.getDoId(),
             av.getTrackAccess(),
             bestQuest))
    else:
        validQuestsMatchingReward = PythonUtil.intersection(questsMatchingReward, validQuestPool)
        if notify.getDebug():
            notify.debug('validQuestsMatchingReward: %s tier: %s = %s' % (rewardId, tier, validQuestsMatchingReward))
        if validQuestsMatchingReward:
            bestQuest = seededRandomChoice(validQuestsMatchingReward)
        else:
            questsMatchingReward = Tier2Reward2QuestsDict[tier].get(AnyCashbotSuitPart, [])
            if notify.getDebug():
                notify.debug('questsMatchingReward: AnyCashbotSuitPart tier: %s = %s' % (tier, questsMatchingReward))
            validQuestsMatchingReward = PythonUtil.intersection(questsMatchingReward, validQuestPool)
            if validQuestsMatchingReward:
                if notify.getDebug():
                    notify.debug('validQuestsMatchingReward: AnyCashbotSuitPart tier: %s = %s' % (tier, validQuestsMatchingReward))
                bestQuest = seededRandomChoice(validQuestsMatchingReward)
            else:
                questsMatchingReward = Tier2Reward2QuestsDict[tier].get(AnyLawbotSuitPart, [])
                if notify.getDebug():
                    notify.debug('questsMatchingReward: AnyLawbotSuitPart tier: %s = %s' % (tier, questsMatchingReward))
                validQuestsMatchingReward = PythonUtil.intersection(questsMatchingReward, validQuestPool)
                if validQuestsMatchingReward:
                    if notify.getDebug():
                        notify.debug('validQuestsMatchingReward: AnyLawbotSuitPart tier: %s = %s' % (tier, validQuestsMatchingReward))
                    bestQuest = seededRandomChoice(validQuestsMatchingReward)
                else:
                    questsMatchingReward = Tier2Reward2QuestsDict[tier].get(Any, [])
                    if notify.getDebug():
                        notify.debug('questsMatchingReward: Any tier: %s = %s' % (tier, questsMatchingReward))
                    if not questsMatchingReward:
                        notify.warning('chooseMatchingQuests, no questsMatchingReward')
                        return None
                    validQuestsMatchingReward = PythonUtil.intersection(questsMatchingReward, validQuestPool)
                    if not validQuestsMatchingReward:
                        notify.warning('chooseMatchingQuests, no validQuestsMatchingReward')
                        return None
                    if notify.getDebug():
                        notify.debug('validQuestsMatchingReward: Any tier: %s = %s' % (tier, validQuestsMatchingReward))
                    bestQuest = seededRandomChoice(validQuestsMatchingReward)
    return bestQuest


def transformReward(baseRewardId, av):
    if baseRewardId == 900:
        trackId, progress = av.getTrackProgress()
        if trackId == -1:
            notify.warning('transformReward: asked to transform 900 but av is not training')
            actualRewardId = baseRewardId
        else:
            actualRewardId = 900 + 1 + trackId
        return actualRewardId
    elif baseRewardId > 800 and baseRewardId < 900:
        trackId, progress = av.getTrackProgress()
        if trackId < 0:
            notify.warning('transformReward: av: %s is training a track with none chosen!' % av.getDoId())
            return 601
        else:
            actualRewardId = baseRewardId + 200 + trackId * 100
            return actualRewardId
    else:
        return baseRewardId


def chooseBestQuests(tier, currentNpc, av):
    if isLoopingFinalTier(tier):
        rewardHistory = map(lambda questDesc: questDesc[3], av.quests)
    else:
        rewardHistory = av.getRewardHistory()[1]

    seedRandomGen(currentNpc.getNpcId(), av.getDoId(), tier, rewardHistory)
    numChoices = getNumChoices(tier)
    rewards = getNextRewards(numChoices, tier, av)
    if not rewards:
        return []
    possibleQuests = []
    possibleRewards = list(rewards)
    if Any not in possibleRewards:
        possibleRewards.append(Any)
    for rewardId in possibleRewards:
        possibleQuests.extend(Tier2Reward2QuestsDict[tier].get(rewardId, []))

    validQuestPool = filterQuests(possibleQuests, currentNpc, av)
    if not validQuestPool:
        return []
    if numChoices == 0:
        numChoices = 1
    bestQuests = []
    for i in xrange(numChoices):
        if len(validQuestPool) == 0:
            break
        if len(rewards) == 0:
            break
        rewardId = rewards.pop(0)
        bestQuestId = chooseMatchingQuest(tier, validQuestPool, rewardId, currentNpc, av)
        if bestQuestId is None:
            continue
        validQuestPool.remove(bestQuestId)
        bestQuestToNpcId = getQuestToNpcId(bestQuestId)
        if bestQuestToNpcId == Any:
            bestQuestToNpcId = 2003
        elif bestQuestToNpcId == Same:
            if currentNpc.getHq():
                bestQuestToNpcId = ToonHQ
            else:
                bestQuestToNpcId = currentNpc.getNpcId()
        elif bestQuestToNpcId == ToonHQ:
            bestQuestToNpcId = ToonHQ
        bestQuests.append([bestQuestId, rewardId, bestQuestToNpcId])

    for quest in bestQuests:
        quest[1] = transformReward(quest[1], av)

    return bestQuests


def questExists(id):
    return id in QuestDict


def getQuest(id):
    questEntry = QuestDict.get(id)
    if questEntry:
        questDesc = questEntry[QuestDictDescIndex]
        questClass = questDesc[0]
        return questClass(id, questDesc[1:])
    else:
        return None
    return None


def getQuestClass(id):
    questEntry = QuestDict.get(id)
    if questEntry:
        return questEntry[QuestDictDescIndex][0]
    else:
        return None
    return None


def getVisitSCStrings(npcId):
    if npcId == ToonHQ:
        strings = [TTLocalizer.QuestsRecoverItemQuestSeeHQSCString, TTLocalizer.QuestsRecoverItemQuestGoToHQSCString]
    elif npcId == ToonTailor:
        strings = [TTLocalizer.QuestsTailorQuestSCString]
    elif npcId:
        npcName, hoodName, buildingArticle, buildingName, toStreet, streetName, isInPlayground = getNpcInfo(npcId)
        strings = [TTLocalizer.QuestsVisitQuestSeeSCString % npcName]
        if isInPlayground:
            strings.append(TTLocalizer.QuestsRecoverItemQuestGoToPlaygroundSCString % hoodName)
        else:
            strings.append(TTLocalizer.QuestsRecoverItemQuestGoToStreetSCString % {'to': toStreet,
             'street': streetName,
             'hood': hoodName})
        strings.extend([TTLocalizer.QuestsRecoverItemQuestVisitBuildingSCString % (buildingArticle, buildingName), TTLocalizer.QuestsRecoverItemQuestWhereIsBuildingSCString % (buildingArticle, buildingName)])
    return strings


def getFinishToonTaskSCStrings(npcId):
    return [TTLocalizer.QuestsGenericFinishSCString] + getVisitSCStrings(npcId)


def chooseQuestDialog(id, status):
    questDialog = getQuestDialog(id).get(status)
    if questDialog == None:
        if status == QUEST:
            quest = getQuest(id)
            questDialog = quest.getDefaultQuestDialog()
        else:
            questDialog = DefaultDialog[status]
    if type(questDialog) == type(()):
        return random.choice(questDialog)
    else:
        return questDialog
    return


def chooseQuestDialogReject():
    return random.choice(DefaultReject)


def chooseQuestDialogTierNotDone():
    return random.choice(DefaultTierNotDone)


def getNpcInfo(npcId):
    npcName = NPCToons.getNPCName(npcId)
    npcZone = NPCToons.getNPCZone(npcId)
    hoodId = ZoneUtil.getCanonicalHoodId(npcZone)
    hoodName = base.cr.hoodMgr.getFullnameFromId(hoodId)
    buildingArticle = NPCToons.getBuildingArticle(npcZone)
    buildingName = NPCToons.getBuildingTitle(npcZone)
    branchId = ZoneUtil.getCanonicalBranchZone(npcZone)
    toStreet = ToontownGlobals.StreetNames[branchId][0]
    streetName = ToontownGlobals.StreetNames[branchId][-1]
    isInPlayground = ZoneUtil.isPlayground(branchId)
    return (npcName,
     hoodName,
     buildingArticle,
     buildingName,
     toStreet,
     streetName,
     isInPlayground)


def getNpcLocationDialog(fromNpcId, toNpcId):
    if not toNpcId:
        return (None, None, None)
    fromNpcZone = None
    fromBranchId = None
    if fromNpcId:
        fromNpcZone = NPCToons.getNPCZone(fromNpcId)
        fromBranchId = ZoneUtil.getCanonicalBranchZone(fromNpcZone)
    toNpcZone = NPCToons.getNPCZone(toNpcId)
    toBranchId = ZoneUtil.getCanonicalBranchZone(toNpcZone)
    toNpcName, toHoodName, toBuildingArticle, toBuildingName, toStreetTo, toStreetName, isInPlayground = getNpcInfo(toNpcId)
    if fromBranchId == toBranchId:
        if isInPlayground:
            streetDesc = TTLocalizer.QuestsStreetLocationThisPlayground
        else:
            streetDesc = TTLocalizer.QuestsStreetLocationThisStreet
    elif isInPlayground:
        streetDesc = TTLocalizer.QuestsStreetLocationNamedPlayground % toHoodName
    else:
        streetDesc = TTLocalizer.QuestsStreetLocationNamedStreet % {'toStreetName': toStreetName,
         'toHoodName': toHoodName}
    paragraph = TTLocalizer.QuestsLocationParagraph % {'building': TTLocalizer.QuestsLocationBuilding % toNpcName,
     'buildingName': toBuildingName,
     'buildingVerb': TTLocalizer.QuestsLocationBuildingVerb,
     'street': streetDesc}
    return (paragraph, toBuildingName, streetDesc)


def fillInQuestNames(text, avName = None, fromNpcId = None, toNpcId = None):
    text = copy.deepcopy(text)
    if avName != None:
        text = text.replace('_avName_', avName)
    if toNpcId:
        if toNpcId == ToonHQ:
            toNpcName = TTLocalizer.QuestsHQOfficerFillin
            where = TTLocalizer.QuestsHQWhereFillin
            buildingName = TTLocalizer.QuestsHQBuildingNameFillin
            streetDesc = TTLocalizer.QuestsHQLocationNameFillin
        elif toNpcId == ToonTailor:
            toNpcName = TTLocalizer.QuestsTailorFillin
            where = TTLocalizer.QuestsTailorWhereFillin
            buildingName = TTLocalizer.QuestsTailorBuildingNameFillin
            streetDesc = TTLocalizer.QuestsTailorLocationNameFillin
        else:
            toNpcName = str(NPCToons.getNPCName(toNpcId))
            where, buildingName, streetDesc = getNpcLocationDialog(fromNpcId, toNpcId)
        text = text.replace('_toNpcName_', toNpcName)
        text = text.replace('_where_', where)
        text = text.replace('_buildingName_', buildingName)
        text = text.replace('_streetDesc_', streetDesc)
    return text


def getVisitingQuest():
    return VisitQuest(VISIT_QUEST_ID)


class Reward:
    def __init__(self, id, reward):
        self.id = id
        self.reward = reward

    def getId(self):
        return self.id

    def getType(self):
        return self.__class__

    def getAmount(self):
        return None

    def sendRewardAI(self, av):
        raise 'not implemented'

    def countReward(self, qrc):
        raise 'not implemented'

    def getString(self):
        return 'undefined'

    def getPosterString(self):
        return 'base class'


class MaxHpReward(Reward):
    def __init__(self, id, reward):
        Reward.__init__(self, id, reward)

    def getAmount(self):
        return self.reward[0]

    def sendRewardAI(self, av):
        maxHp = av.getMaxHp()
        maxHp = min(ToontownGlobals.MaxHpLimit, maxHp + self.getAmount())
        av.b_setMaxHp(maxHp)
        av.toonUp(maxHp)

    def countReward(self, qrc):
        qrc.maxHp += self.getAmount()

    def getString(self):
        return TTLocalizer.QuestsMaxHpReward % self.getAmount()

    def getPosterString(self):
        return TTLocalizer.QuestsMaxHpRewardPoster % self.getAmount()


class MoneyReward(Reward):
    def __init__(self, id, reward):
        Reward.__init__(self, id, reward)

    def getAmount(self):
        return self.reward[0]

    def sendRewardAI(self, av):
        money = av.getMoney()
        maxMoney = av.getMaxMoney()
        av.addMoney(self.getAmount())

    def countReward(self, qrc):
        qrc.money += self.getAmount()

    def getString(self):
        amt = self.getAmount()
        if amt == 1:
            return TTLocalizer.QuestsMoneyRewardSingular
        else:
            return TTLocalizer.QuestsMoneyRewardPlural % amt

    def getPosterString(self):
        amt = self.getAmount()
        if amt == 1:
            return TTLocalizer.QuestsMoneyRewardPosterSingular
        else:
            return TTLocalizer.QuestsMoneyRewardPosterPlural % amt


class MaxMoneyReward(Reward):
    def __init__(self, id, reward):
        Reward.__init__(self, id, reward)

    def getAmount(self):
        return self.reward[0]

    def sendRewardAI(self, av):
        av.b_setMaxMoney(self.getAmount())

    def countReward(self, qrc):
        qrc.maxMoney = self.getAmount()

    def getString(self):
        amt = self.getAmount()
        if amt == 1:
            return TTLocalizer.QuestsMaxMoneyRewardSingular
        else:
            return TTLocalizer.QuestsMaxMoneyRewardPlural % amt

    def getPosterString(self):
        amt = self.getAmount()
        if amt == 1:
            return TTLocalizer.QuestsMaxMoneyRewardPosterSingular
        else:
            return TTLocalizer.QuestsMaxMoneyRewardPosterPlural % amt


class MaxGagCarryReward(Reward):
    def __init__(self, id, reward):
        Reward.__init__(self, id, reward)

    def getAmount(self):
        return self.reward[0]

    def getName(self):
        return self.reward[1]

    def sendRewardAI(self, av):
        av.b_setMaxCarry(self.getAmount())

    def countReward(self, qrc):
        qrc.maxCarry = self.getAmount()

    def getString(self):
        name = self.getName()
        amt = self.getAmount()
        return TTLocalizer.QuestsMaxGagCarryReward % {'name': name,
         'num': amt}

    def getPosterString(self):
        name = self.getName()
        amt = self.getAmount()
        return TTLocalizer.QuestsMaxGagCarryRewardPoster % {'name': name,
         'num': amt}


class MaxQuestCarryReward(Reward):
    def __init__(self, id, reward):
        Reward.__init__(self, id, reward)

    def getAmount(self):
        return self.reward[0]

    def sendRewardAI(self, av):
        av.b_setQuestCarryLimit(self.getAmount())

    def countReward(self, qrc):
        qrc.questCarryLimit = self.getAmount()

    def getString(self):
        amt = self.getAmount()
        return TTLocalizer.QuestsMaxQuestCarryReward % amt

    def getPosterString(self):
        amt = self.getAmount()
        return TTLocalizer.QuestsMaxQuestCarryRewardPoster % amt


class TeleportReward(Reward):
    def __init__(self, id, reward):
        Reward.__init__(self, id, reward)

    def getZone(self):
        return self.reward[0]

    def sendRewardAI(self, av):
        av.addTeleportAccess(self.getZone())

    def countReward(self, qrc):
        qrc.addTeleportAccess(self.getZone())

    def getString(self):
        hoodName = ToontownGlobals.hoodNameMap[self.getZone()][-1]
        return TTLocalizer.QuestsTeleportReward % hoodName

    def getPosterString(self):
        hoodName = ToontownGlobals.hoodNameMap[self.getZone()][-1]
        return TTLocalizer.QuestsTeleportRewardPoster % hoodName


TrackTrainingQuotas = {ToontownBattleGlobals.HEAL_TRACK: 15,
 ToontownBattleGlobals.TRAP_TRACK: 15,
 ToontownBattleGlobals.LURE_TRACK: 15,
 ToontownBattleGlobals.SOUND_TRACK: 15,
 ToontownBattleGlobals.THROW_TRACK: 15,
 ToontownBattleGlobals.SQUIRT_TRACK: 15,
 ToontownBattleGlobals.DROP_TRACK: 15}

class TrackTrainingReward(Reward):
    def __init__(self, id, reward):
        Reward.__init__(self, id, reward)

    def getTrack(self):
        track = self.reward[0]
        if track == None:
            track = 0
        return track

    def sendRewardAI(self, av):
        av.b_setTrackProgress(self.getTrack(), 0)

    def countReward(self, qrc):
        qrc.trackProgressId = self.getTrack()
        qrc.trackProgress = 0

    def getString(self):
        trackName = ToontownBattleGlobals.Tracks[self.getTrack()].capitalize()
        return TTLocalizer.QuestsTrackTrainingReward % trackName

    def getPosterString(self):
        return TTLocalizer.QuestsTrackTrainingRewardPoster


class TrackProgressReward(Reward):
    def __init__(self, id, reward):
        Reward.__init__(self, id, reward)

    def getTrack(self):
        track = self.reward[0]
        if track == None:
            track = 0
        return track

    def getProgressIndex(self):
        return self.reward[1]

    def sendRewardAI(self, av):
        av.addTrackProgress(self.getTrack(), self.getProgressIndex())

    def countReward(self, qrc):
        qrc.addTrackProgress(self.getTrack(), self.getProgressIndex())

    def getString(self):
        trackName = ToontownBattleGlobals.Tracks[self.getTrack()].capitalize()
        return TTLocalizer.QuestsTrackProgressReward % {'frameNum': self.getProgressIndex(),
         'trackName': trackName}

    def getPosterString(self):
        trackName = ToontownBattleGlobals.Tracks[self.getTrack()].capitalize()
        return TTLocalizer.QuestsTrackProgressRewardPoster % {'trackName': trackName,
         'frameNum': self.getProgressIndex()}


class TrackCompleteReward(Reward):
    def __init__(self, id, reward):
        Reward.__init__(self, id, reward)

    def getTrack(self):
        track = self.reward[0]
        if track == None:
            track = 0
        return track

    def sendRewardAI(self, av):
        av.addTrackAccess(self.getTrack())
        av.clearTrackProgress()

    def countReward(self, qrc):
        qrc.addTrackAccess(self.getTrack())
        qrc.clearTrackProgress()

    def getString(self):
        trackName = ToontownBattleGlobals.Tracks[self.getTrack()].capitalize()
        return TTLocalizer.QuestsTrackCompleteReward % trackName

    def getPosterString(self):
        trackName = ToontownBattleGlobals.Tracks[self.getTrack()].capitalize()
        return TTLocalizer.QuestsTrackCompleteRewardPoster % trackName


class ClothingTicketReward(Reward):
    def __init__(self, id, reward):
        Reward.__init__(self, id, reward)

    def sendRewardAI(self, av):
        pass

    def countReward(self, qrc):
        pass

    def getString(self):
        return TTLocalizer.QuestsClothingTicketReward

    def getPosterString(self):
        return TTLocalizer.QuestsClothingTicketRewardPoster


class TIPClothingTicketReward(ClothingTicketReward):
    def __init__(self, id, reward):
        ClothingTicketReward.__init__(self, id, reward)

    def getString(self):
        return TTLocalizer.TIPQuestsClothingTicketReward

    def getPosterString(self):
        return TTLocalizer.TIPQuestsClothingTicketRewardPoster


class CheesyEffectReward(Reward):
    def __init__(self, id, reward):
        Reward.__init__(self, id, reward)

    def getEffect(self):
        return self.reward[0]

    def getHoodId(self):
        return self.reward[1]

    def getDurationMinutes(self):
        return self.reward[2]

    def sendRewardAI(self, av):
        expireTime = int(time.time() / 60 + 0.5) + self.getDurationMinutes()
        av.b_setCheesyEffect(self.getEffect(), self.getHoodId(), expireTime)

    def countReward(self, qrc):
        pass

    def getString(self):
        effect = self.getEffect()
        hoodId = self.getHoodId()
        duration = self.getDurationMinutes()
        string = TTLocalizer.CheesyEffectMinutes
        if duration > 90:
            duration = int((duration + 30) / 60)
            string = TTLocalizer.CheesyEffectHours
            if duration > 36:
                duration = int((duration + 12) / 24)
                string = TTLocalizer.CheesyEffectDays
        desc = TTLocalizer.CheesyEffectDescriptions[effect][1]
        if hoodId == 0:
            whileStr = ''
        elif hoodId == 1:
            whileStr = TTLocalizer.CheesyEffectExceptIn % TTLocalizer.ToontownCentral[-1]
        else:
            hoodName = base.cr.hoodMgr.getFullnameFromId(hoodId)
            whileStr = TTLocalizer.CheesyEffectWhileYouAreIn % hoodName
        if duration:
            return string % {'time': duration,
             'effectName': desc,
             'whileIn': whileStr}
        else:
            return TTLocalizer.CheesyEffectIndefinite % {'effectName': desc,
             'whileIn': whileStr}

    def getPosterString(self):
        effect = self.getEffect()
        desc = TTLocalizer.CheesyEffectDescriptions[effect][0]
        return TTLocalizer.QuestsCheesyEffectRewardPoster % desc


class CogSuitPartReward(Reward):
    trackNames = [TTLocalizer.Bossbot,
     TTLocalizer.Lawbot,
     TTLocalizer.Cashbot,
     TTLocalizer.Sellbot,
     TTLocalizer.Governbot,
     TTLocalizer.Eurekabot,
     TTLocalizer.Buildbot,
     TTLocalizer.Viralbot]

    def __init__(self, id, reward):
        Reward.__init__(self, id, reward)

    def getCogTrack(self):
        return self.reward[0]

    def getCogPart(self):
        return self.reward[1]

    def sendRewardAI(self, av):
        dept = self.getCogTrack()
        part = self.getCogPart()
        av.giveCogPart(part, dept)

    def countReward(self, qrc):
        pass

    def getCogTrackName(self):
        index = ToontownGlobals.cogDept2index[self.getCogTrack()]
        return CogSuitPartReward.trackNames[index]

    def getCogPartName(self):
        index = ToontownGlobals.cogDept2index[self.getCogTrack()]
        return CogDisguiseGlobals.PartsQueryNames[index][self.getCogPart()]

    def getString(self):
        return TTLocalizer.QuestsCogSuitPartReward % {'cogTrack': self.getCogTrackName(),
         'part': self.getCogPartName()}

    def getPosterString(self):
        return TTLocalizer.QuestsCogSuitPartRewardPoster % {'cogTrack': self.getCogTrackName(),
         'part': self.getCogPartName()}


class BuffReward(Reward):
    def sendRewardAI(self, av):
        av.addBuff(self.getBuffId(), self.getBuffTime())

    def getBuffId(self):
        return self.reward[0]

    def getBuffTime(self):
        return self.reward[1]

    def getString(self):
        return TTLocalizer.getBuffString(self.getBuffId(), self.getBuffTime())

    def getPosterString(self):
        return TTLocalizer.getBuffPosterString(self.getBuffId())

class EPPReward(Reward):
    trackNames = [TTLocalizer.Bossbot,
                  TTLocalizer.Lawbot,
                  TTLocalizer.Cashbot,
                  TTLocalizer.Sellbot,
                  TTLocalizer.Governbot,
                  TTLocalizer.Eurekabot,
                  TTLocalizer.Buildbot,
                  TTLocalizer.Viralbot]
     
    def sendRewardAI(self, av):
        av.addEPP(self.reward[0])
    
    def countReward(self, qrc):
        pass
    
    def getCogTrackName(self):
        return EPPReward.trackNames[self.reward[0]]
    
    def getString(self):
        return TTLocalizer.QuestsEPPReward % self.getCogTrackName()
    
    def getPosterString(self):
        return TTLocalizer.QuestsEPPRewardPoster % self.getCogTrackName()       


def getRewardClass(id):
    reward = RewardDict.get(id)
    if reward:
        return reward[0]
    else:
        return None
    return None


def getReward(id):
    reward = RewardDict.get(id)
    if reward:
        rewardClass = reward[0]
        return rewardClass(id, reward[1:])
    else:
        notify.warning('getReward(): id %s not found.' % id)
        return None
    return None


def getNextRewards(numChoices, tier, av):
    rewardTier = list(getRewardsInTier(tier))
    optRewards = list(getOptionalRewardsInTier(tier))
    if tier == TT_TIER + 3:
        optRewards = []
    if isLoopingFinalTier(tier):
        rewardHistory = map(lambda questDesc: questDesc[3], av.quests)
        if notify.getDebug():
            notify.debug('getNextRewards: current rewards (history): %s' % rewardHistory)
    else:
        rewardHistory = av.getRewardHistory()[1]
        if notify.getDebug():
            notify.debug('getNextRewards: rewardHistory: %s' % rewardHistory)
    if notify.getDebug():
        notify.debug('getNextRewards: rewardTier: %s' % rewardTier)
        notify.debug('getNextRewards: numChoices: %s' % numChoices)
    for rewardId in getRewardsInTier(tier):
        if getRewardClass(rewardId) == CogSuitPartReward:
            deptStr = RewardDict.get(rewardId)[1]
            cogPart = RewardDict.get(rewardId)[2]
            dept = ToontownGlobals.cogDept2index[deptStr]
            if av.hasCogPart(cogPart, dept):
                notify.debug('getNextRewards: already has cog part: %s dept: %s' % (cogPart, dept))
                rewardTier.remove(rewardId)
            else:
                notify.debug('getNextRewards: keeping quest for cog part: %s dept: %s' % (cogPart, dept))

    for rewardId in rewardHistory:
        if rewardId in rewardTier:
            rewardTier.remove(rewardId)
        elif rewardId in optRewards:
            optRewards.remove(rewardId)
        elif rewardId in (901, 902, 903, 904, 905, 906, 907):
            genericRewardId = 900
            if genericRewardId in rewardTier:
                rewardTier.remove(genericRewardId)
        elif rewardId > 1000 and rewardId < 1699:
            index = rewardId % 100
            genericRewardId = 800 + index
            if genericRewardId in rewardTier:
                rewardTier.remove(genericRewardId)

    if numChoices == 0:
        if len(rewardTier) == 0:
            return []
        else:
            return [rewardTier[0]]
    rewardPool = rewardTier[:numChoices]
    for i in xrange(len(rewardPool), numChoices * 2):
        if optRewards:
            optionalReward = seededRandomChoice(optRewards)
            optRewards.remove(optionalReward)
            rewardPool.append(optionalReward)
        else:
            break

    if notify.getDebug():
        notify.debug('getNextRewards: starting reward pool: %s' % rewardPool)
    if len(rewardPool) == 0:
        if notify.getDebug():
            notify.debug('getNextRewards: no rewards left at all')
        return []
    finalRewardPool = [rewardPool.pop(0)]
    for i in xrange(numChoices - 1):
        if len(rewardPool) == 0:
            break
        selectedReward = seededRandomChoice(rewardPool)
        rewardPool.remove(selectedReward)
        finalRewardPool.append(selectedReward)

    if notify.getDebug():
        notify.debug('getNextRewards: final reward pool: %s' % finalRewardPool)
    return finalRewardPool


RewardDict = {
    100: (MaxHpReward, 1),
    101: (MaxHpReward, 2),
    102: (MaxHpReward, 3),
    103: (MaxHpReward, 4),
    104: (MaxHpReward, 5),
    105: (MaxHpReward, 6),
    106: (MaxHpReward, 7),
    107: (MaxHpReward, 8),
    108: (MaxHpReward, 9),
    109: (MaxHpReward, 10),
    200: (MaxGagCarryReward, 40, TTLocalizer.QuestsMediumPouch),
    201: (MaxGagCarryReward, 50, TTLocalizer.QuestsLargePouch),
    202: (MaxGagCarryReward, 60, TTLocalizer.QuestsSmallBag),
    203: (MaxGagCarryReward, 80, TTLocalizer.QuestsMediumBag),
    204: (MaxGagCarryReward, 100, TTLocalizer.QuestsLargeBag),
    205: (MaxGagCarryReward, 120, TTLocalizer.QuestsSmallBackpack),
    206: (MaxGagCarryReward, 140, TTLocalizer.QuestsMediumBackpack),
    207: (MaxGagCarryReward, 170, TTLocalizer.QuestsLargeBackpack),
    300: (TeleportReward, ToontownGlobals.ToontownCentral),
    301: (TeleportReward, ToontownGlobals.DonaldsDock),
    302: (TeleportReward, ToontownGlobals.DaisyGardens),
    303: (TeleportReward, ToontownGlobals.MinniesMelodyland),
    304: (TeleportReward, ToontownGlobals.TheBrrrgh),
    305: (TeleportReward, ToontownGlobals.DonaldsDreamland),
    400: (TrackTrainingReward, None),
    401: (TrackTrainingReward, ToontownBattleGlobals.HEAL_TRACK),
    402: (TrackTrainingReward, ToontownBattleGlobals.TRAP_TRACK),
    403: (TrackTrainingReward, ToontownBattleGlobals.LURE_TRACK),
    404: (TrackTrainingReward, ToontownBattleGlobals.SOUND_TRACK),
    405: (TrackTrainingReward, ToontownBattleGlobals.THROW_TRACK),
    406: (TrackTrainingReward, ToontownBattleGlobals.SQUIRT_TRACK),
    407: (TrackTrainingReward, ToontownBattleGlobals.DROP_TRACK),
    500: (MaxQuestCarryReward, 2),
    501: (MaxQuestCarryReward, 3),
    502: (MaxQuestCarryReward, 4),
    600: (MoneyReward, 30),
    601: (MoneyReward, 40),
    602: (MoneyReward, 50),
    603: (MoneyReward, 60),
    604: (MoneyReward, 100),
    605: (MoneyReward, 150),
    606: (MoneyReward, 200),
    607: (MoneyReward, 250),
    608: (MoneyReward, 300),
    609: (MoneyReward, 400),
    610: (MoneyReward, 500),
    611: (MoneyReward, 600),
    612: (MoneyReward, 700),
    613: (MoneyReward, 800),
    614: (MoneyReward, 900),
    615: (MoneyReward, 1000),
    616: (MoneyReward, 1100),
    617: (MoneyReward, 1200),
    618: (MoneyReward, 1300),
    619: (MoneyReward, 1400),
    620: (MoneyReward, 1500),
    621: (MoneyReward, 1750),
    622: (MoneyReward, 2000),
    623: (MoneyReward, 2500),
    700: (MaxMoneyReward, 250),
    701: (MaxMoneyReward, 500),
    702: (MaxMoneyReward, 1000),
    703: (MaxMoneyReward, 2500),
    704: (MaxMoneyReward, 5000),
    705: (MaxMoneyReward, 10000),
    706: (MaxMoneyReward, 20000),
    707: (MaxMoneyReward, 50000),
    801: (TrackProgressReward, None, 1),
    802: (TrackProgressReward, None, 2),
    803: (TrackProgressReward, None, 3),
    804: (TrackProgressReward, None, 4),
    805: (TrackProgressReward, None, 5),
    806: (TrackProgressReward, None, 6),
    807: (TrackProgressReward, None, 7),
    808: (TrackProgressReward, None, 8),
    809: (TrackProgressReward, None, 9),
    810: (TrackProgressReward, None, 10),
    811: (TrackProgressReward, None, 11),
    812: (TrackProgressReward, None, 12),
    813: (TrackProgressReward, None, 13),
    814: (TrackProgressReward, None, 14),
    815: (TrackProgressReward, None, 15),
    110: (TIPClothingTicketReward,),
    1000: (ClothingTicketReward,),
    1001: (TrackProgressReward, ToontownBattleGlobals.HEAL_TRACK, 1),
    1002: (TrackProgressReward, ToontownBattleGlobals.HEAL_TRACK, 2),
    1003: (TrackProgressReward, ToontownBattleGlobals.HEAL_TRACK, 3),
    1004: (TrackProgressReward, ToontownBattleGlobals.HEAL_TRACK, 4),
    1005: (TrackProgressReward, ToontownBattleGlobals.HEAL_TRACK, 5),
    1006: (TrackProgressReward, ToontownBattleGlobals.HEAL_TRACK, 6),
    1007: (TrackProgressReward, ToontownBattleGlobals.HEAL_TRACK, 7),
    1008: (TrackProgressReward, ToontownBattleGlobals.HEAL_TRACK, 8),
    1009: (TrackProgressReward, ToontownBattleGlobals.HEAL_TRACK, 9),
    1010: (TrackProgressReward, ToontownBattleGlobals.HEAL_TRACK, 10),
    1011: (TrackProgressReward, ToontownBattleGlobals.HEAL_TRACK, 11),
    1012: (TrackProgressReward, ToontownBattleGlobals.HEAL_TRACK, 12),
    1013: (TrackProgressReward, ToontownBattleGlobals.HEAL_TRACK, 13),
    1014: (TrackProgressReward, ToontownBattleGlobals.HEAL_TRACK, 14),
    1015: (TrackProgressReward, ToontownBattleGlobals.HEAL_TRACK, 15),
    1101: (TrackProgressReward, ToontownBattleGlobals.TRAP_TRACK, 1),
    1102: (TrackProgressReward, ToontownBattleGlobals.TRAP_TRACK, 2),
    1103: (TrackProgressReward, ToontownBattleGlobals.TRAP_TRACK, 3),
    1104: (TrackProgressReward, ToontownBattleGlobals.TRAP_TRACK, 4),
    1105: (TrackProgressReward, ToontownBattleGlobals.TRAP_TRACK, 5),
    1106: (TrackProgressReward, ToontownBattleGlobals.TRAP_TRACK, 6),
    1107: (TrackProgressReward, ToontownBattleGlobals.TRAP_TRACK, 7),
    1108: (TrackProgressReward, ToontownBattleGlobals.TRAP_TRACK, 8),
    1109: (TrackProgressReward, ToontownBattleGlobals.TRAP_TRACK, 9),
    1110: (TrackProgressReward, ToontownBattleGlobals.TRAP_TRACK, 10),
    1111: (TrackProgressReward, ToontownBattleGlobals.TRAP_TRACK, 11),
    1112: (TrackProgressReward, ToontownBattleGlobals.TRAP_TRACK, 12),
    1113: (TrackProgressReward, ToontownBattleGlobals.TRAP_TRACK, 13),
    1114: (TrackProgressReward, ToontownBattleGlobals.TRAP_TRACK, 14),
    1115: (TrackProgressReward, ToontownBattleGlobals.TRAP_TRACK, 15),
    1201: (TrackProgressReward, ToontownBattleGlobals.LURE_TRACK, 1),
    1202: (TrackProgressReward, ToontownBattleGlobals.LURE_TRACK, 2),
    1203: (TrackProgressReward, ToontownBattleGlobals.LURE_TRACK, 3),
    1204: (TrackProgressReward, ToontownBattleGlobals.LURE_TRACK, 4),
    1205: (TrackProgressReward, ToontownBattleGlobals.LURE_TRACK, 5),
    1206: (TrackProgressReward, ToontownBattleGlobals.LURE_TRACK, 6),
    1207: (TrackProgressReward, ToontownBattleGlobals.LURE_TRACK, 7),
    1208: (TrackProgressReward, ToontownBattleGlobals.LURE_TRACK, 8),
    1209: (TrackProgressReward, ToontownBattleGlobals.LURE_TRACK, 9),
    1210: (TrackProgressReward, ToontownBattleGlobals.LURE_TRACK, 10),
    1211: (TrackProgressReward, ToontownBattleGlobals.LURE_TRACK, 11),
    1212: (TrackProgressReward, ToontownBattleGlobals.LURE_TRACK, 12),
    1213: (TrackProgressReward, ToontownBattleGlobals.LURE_TRACK, 13),
    1214: (TrackProgressReward, ToontownBattleGlobals.LURE_TRACK, 14),
    1215: (TrackProgressReward, ToontownBattleGlobals.LURE_TRACK, 15),
    1301: (TrackProgressReward, ToontownBattleGlobals.SOUND_TRACK, 1),
    1302: (TrackProgressReward, ToontownBattleGlobals.SOUND_TRACK, 2),
    1303: (TrackProgressReward, ToontownBattleGlobals.SOUND_TRACK, 3),
    1304: (TrackProgressReward, ToontownBattleGlobals.SOUND_TRACK, 4),
    1305: (TrackProgressReward, ToontownBattleGlobals.SOUND_TRACK, 5),
    1306: (TrackProgressReward, ToontownBattleGlobals.SOUND_TRACK, 6),
    1307: (TrackProgressReward, ToontownBattleGlobals.SOUND_TRACK, 7),
    1308: (TrackProgressReward, ToontownBattleGlobals.SOUND_TRACK, 8),
    1309: (TrackProgressReward, ToontownBattleGlobals.SOUND_TRACK, 9),
    1310: (TrackProgressReward, ToontownBattleGlobals.SOUND_TRACK, 10),
    1311: (TrackProgressReward, ToontownBattleGlobals.SOUND_TRACK, 11),
    1312: (TrackProgressReward, ToontownBattleGlobals.SOUND_TRACK, 12),
    1313: (TrackProgressReward, ToontownBattleGlobals.SOUND_TRACK, 13),
    1314: (TrackProgressReward, ToontownBattleGlobals.SOUND_TRACK, 14),
    1315: (TrackProgressReward, ToontownBattleGlobals.SOUND_TRACK, 15),
    900: (TrackCompleteReward, None),
    901: (TrackCompleteReward, ToontownBattleGlobals.HEAL_TRACK),
    902: (TrackCompleteReward, ToontownBattleGlobals.TRAP_TRACK),
    903: (TrackCompleteReward, ToontownBattleGlobals.LURE_TRACK),
    904: (TrackCompleteReward, ToontownBattleGlobals.SOUND_TRACK),
    905: (TrackCompleteReward, ToontownBattleGlobals.THROW_TRACK),
    906: (TrackCompleteReward, ToontownBattleGlobals.SQUIRT_TRACK),
    907: (TrackCompleteReward, ToontownBattleGlobals.DROP_TRACK),
    2205: (CheesyEffectReward, ToontownGlobals.CEBigToon, 2000, 10),
    2206: (CheesyEffectReward, ToontownGlobals.CESmallToon, 2000, 10),
    2101: (CheesyEffectReward, ToontownGlobals.CEBigHead, 1000, 10),
    2102: (CheesyEffectReward, ToontownGlobals.CESmallHead, 1000, 10),
    2105: (CheesyEffectReward, ToontownGlobals.CEBigToon, 0, 20),
    2106: (CheesyEffectReward, ToontownGlobals.CESmallToon, 0, 20),
    2501: (CheesyEffectReward, ToontownGlobals.CEBigHead, 5000, 60),
    2502: (CheesyEffectReward, ToontownGlobals.CESmallHead, 5000, 60),
    2503: (CheesyEffectReward, ToontownGlobals.CEBigLegs, 5000, 20),
    2504: (CheesyEffectReward, ToontownGlobals.CESmallLegs, 5000, 20),
    2505: (CheesyEffectReward, ToontownGlobals.CEBigToon, 0, 60),
    2506: (CheesyEffectReward, ToontownGlobals.CESmallToon, 0, 60),
    2401: (CheesyEffectReward, ToontownGlobals.CEBigHead, 1, 120),
    2402: (CheesyEffectReward, ToontownGlobals.CESmallHead, 1, 120),
    2403: (CheesyEffectReward, ToontownGlobals.CEBigLegs, 4000, 60),
    2404: (CheesyEffectReward, ToontownGlobals.CESmallLegs, 4000, 60),
    2405: (CheesyEffectReward, ToontownGlobals.CEBigToon, 0, 120),
    2406: (CheesyEffectReward, ToontownGlobals.CESmallToon, 0, 120),
    2407: (CheesyEffectReward, ToontownGlobals.CEFlatPortrait, 4000, 30),
    2408: (CheesyEffectReward, ToontownGlobals.CEFlatProfile, 4000, 30),
    2409: (CheesyEffectReward, ToontownGlobals.CETransparent, 4000, 30),
    2410: (CheesyEffectReward, ToontownGlobals.CENoColor, 4000, 30),
    2301: (CheesyEffectReward, ToontownGlobals.CEBigHead, 1, 360),
    2302: (CheesyEffectReward, ToontownGlobals.CESmallHead, 1, 360),
    2303: (CheesyEffectReward, ToontownGlobals.CEBigLegs, 1, 360),
    2304: (CheesyEffectReward, ToontownGlobals.CESmallLegs, 1, 360),
    2305: (CheesyEffectReward, ToontownGlobals.CEBigToon, 0, 1440),
    2306: (CheesyEffectReward, ToontownGlobals.CESmallToon, 0, 1440),
    2307: (CheesyEffectReward, ToontownGlobals.CEFlatPortrait, 3000, 240),
    2308: (CheesyEffectReward, ToontownGlobals.CEFlatProfile, 3000, 240),
    2309: (CheesyEffectReward, ToontownGlobals.CETransparent, 1, 120),
    2310: (CheesyEffectReward, ToontownGlobals.CENoColor, 1, 120),
    2311: (CheesyEffectReward, ToontownGlobals.CEInvisible, 3000, 120),
    2900: (CheesyEffectReward, ToontownGlobals.CENormal, 0, 0),
    2901: (CheesyEffectReward, ToontownGlobals.CEBigHead, 1, 1440),
    2902: (CheesyEffectReward, ToontownGlobals.CESmallHead, 1, 1440),
    2903: (CheesyEffectReward, ToontownGlobals.CEBigLegs, 1, 1440),
    2904: (CheesyEffectReward, ToontownGlobals.CESmallLegs, 1, 1440),
    2905: (CheesyEffectReward, ToontownGlobals.CEBigToon, 0, 1440),
    2906: (CheesyEffectReward, ToontownGlobals.CESmallToon, 0, 1440),
    2907: (CheesyEffectReward, ToontownGlobals.CEFlatPortrait, 1, 1440),
    2908: (CheesyEffectReward, ToontownGlobals.CEFlatProfile, 1, 1440),
    2909: (CheesyEffectReward, ToontownGlobals.CETransparent, 1, 1440),
    2910: (CheesyEffectReward, ToontownGlobals.CENoColor, 1, 1440),
    2911: (CheesyEffectReward, ToontownGlobals.CEInvisible, 1, 1440),
    2920: (CheesyEffectReward, ToontownGlobals.CENormal, 0, 0),
    2921: (CheesyEffectReward, ToontownGlobals.CEBigHead, 1, 2880),
    2922: (CheesyEffectReward, ToontownGlobals.CESmallHead, 1, 2880),
    2923: (CheesyEffectReward, ToontownGlobals.CEBigLegs, 1, 2880),
    2924: (CheesyEffectReward, ToontownGlobals.CESmallLegs, 1, 2880),
    2925: (CheesyEffectReward, ToontownGlobals.CEBigToon, 0, 2880),
    2926: (CheesyEffectReward, ToontownGlobals.CESmallToon, 0, 2880),
    2927: (CheesyEffectReward, ToontownGlobals.CEFlatPortrait, 1, 2880),
    2928: (CheesyEffectReward, ToontownGlobals.CEFlatProfile, 1, 2880),
    2929: (CheesyEffectReward, ToontownGlobals.CETransparent, 1, 2880),
    2930: (CheesyEffectReward, ToontownGlobals.CENoColor, 1, 2880),
    2931: (CheesyEffectReward, ToontownGlobals.CEInvisible, 1, 2880),
    2940: (CheesyEffectReward, ToontownGlobals.CENormal, 0, 0),
    2941: (CheesyEffectReward, ToontownGlobals.CEBigHead, 1, 10080),
    2942: (CheesyEffectReward, ToontownGlobals.CESmallHead, 1, 10080),
    2943: (CheesyEffectReward, ToontownGlobals.CEBigLegs, 1, 10080),
    2944: (CheesyEffectReward, ToontownGlobals.CESmallLegs, 1, 10080),
    2945: (CheesyEffectReward, ToontownGlobals.CEBigToon, 0, 10080),
    2946: (CheesyEffectReward, ToontownGlobals.CESmallToon, 0, 10080),
    2947: (CheesyEffectReward, ToontownGlobals.CEFlatPortrait, 1, 10080),
    2948: (CheesyEffectReward, ToontownGlobals.CEFlatProfile, 1, 10080),
    2949: (CheesyEffectReward, ToontownGlobals.CETransparent, 1, 10080),
    2950: (CheesyEffectReward, ToontownGlobals.CENoColor, 1, 10080),
    2951: (CheesyEffectReward, ToontownGlobals.CEInvisible, 1, 10080),
    2960: (CheesyEffectReward, ToontownGlobals.CENormal, 0, 0),
    2961: (CheesyEffectReward, ToontownGlobals.CEBigHead, 1, 43200),
    2962: (CheesyEffectReward, ToontownGlobals.CESmallHead, 1, 43200),
    2963: (CheesyEffectReward, ToontownGlobals.CEBigLegs, 1, 43200),
    2964: (CheesyEffectReward, ToontownGlobals.CESmallLegs, 1, 43200),
    2965: (CheesyEffectReward, ToontownGlobals.CEBigToon, 0, 43200),
    2966: (CheesyEffectReward, ToontownGlobals.CESmallToon, 0, 43200),
    2967: (CheesyEffectReward, ToontownGlobals.CEFlatPortrait, 1, 43200),
    2968: (CheesyEffectReward, ToontownGlobals.CEFlatProfile, 1, 43200),
    2969: (CheesyEffectReward, ToontownGlobals.CETransparent, 1, 43200),
    2970: (CheesyEffectReward, ToontownGlobals.CENoColor, 1, 43200),
    2971: (CheesyEffectReward, ToontownGlobals.CEInvisible, 1, 43200),
    4000: (CogSuitPartReward, 'm', CogDisguiseGlobals.leftLegUpper),
    4001: (CogSuitPartReward, 'm', CogDisguiseGlobals.leftLegLower),
    4002: (CogSuitPartReward, 'm', CogDisguiseGlobals.leftLegFoot),
    4003: (CogSuitPartReward, 'm', CogDisguiseGlobals.rightLegUpper),
    4004: (CogSuitPartReward, 'm', CogDisguiseGlobals.rightLegLower),
    4005: (CogSuitPartReward, 'm', CogDisguiseGlobals.rightLegFoot),
    4006: (CogSuitPartReward, 'm', CogDisguiseGlobals.upperTorso),
    4007: (CogSuitPartReward, 'm', CogDisguiseGlobals.torsoPelvis),
    4008: (CogSuitPartReward, 'm', CogDisguiseGlobals.leftArmUpper),
    4009: (CogSuitPartReward, 'm', CogDisguiseGlobals.leftArmLower),
    4010: (CogSuitPartReward, 'm', CogDisguiseGlobals.rightArmUpper),
    4011: (CogSuitPartReward, 'm', CogDisguiseGlobals.rightArmLower),
    4100: (CogSuitPartReward, 'l', CogDisguiseGlobals.leftLegUpper),
    4101: (CogSuitPartReward, 'l', CogDisguiseGlobals.leftLegLower),
    4102: (CogSuitPartReward, 'l', CogDisguiseGlobals.leftLegFoot),
    4103: (CogSuitPartReward, 'l', CogDisguiseGlobals.rightLegUpper),
    4104: (CogSuitPartReward, 'l', CogDisguiseGlobals.rightLegLower),
    4105: (CogSuitPartReward, 'l', CogDisguiseGlobals.rightLegFoot),
    4106: (CogSuitPartReward, 'l', CogDisguiseGlobals.upperTorso),
    4107: (CogSuitPartReward, 'l', CogDisguiseGlobals.torsoPelvis),
    4108: (CogSuitPartReward, 'l', CogDisguiseGlobals.leftArmUpper),
    4109: (CogSuitPartReward, 'l', CogDisguiseGlobals.leftArmLower),
    4110: (CogSuitPartReward, 'l', CogDisguiseGlobals.leftArmHand),
    4111: (CogSuitPartReward, 'l', CogDisguiseGlobals.rightArmUpper),
    4112: (CogSuitPartReward, 'l', CogDisguiseGlobals.rightArmLower),
    4113: (CogSuitPartReward, 'l', CogDisguiseGlobals.rightArmHand),
    4200: (CogSuitPartReward, 'c', CogDisguiseGlobals.leftLegUpper),
    4201: (CogSuitPartReward, 'c', CogDisguiseGlobals.leftLegLower),
    4202: (CogSuitPartReward, 'c', CogDisguiseGlobals.leftLegFoot),
    4203: (CogSuitPartReward, 'c', CogDisguiseGlobals.rightLegUpper),
    4204: (CogSuitPartReward, 'c', CogDisguiseGlobals.rightLegLower),
    4205: (CogSuitPartReward, 'c', CogDisguiseGlobals.rightLegFoot),
    4206: (CogSuitPartReward, 'c', CogDisguiseGlobals.torsoLeftShoulder),
    4207: (CogSuitPartReward, 'c', CogDisguiseGlobals.torsoRightShoulder),
    4208: (CogSuitPartReward, 'c', CogDisguiseGlobals.torsoChest),
    4209: (CogSuitPartReward, 'c', CogDisguiseGlobals.torsoHealthMeter),
    4210: (CogSuitPartReward, 'c', CogDisguiseGlobals.torsoPelvis),
    4211: (CogSuitPartReward, 'c', CogDisguiseGlobals.leftArmUpper),
    4212: (CogSuitPartReward, 'c', CogDisguiseGlobals.leftArmLower),
    4213: (CogSuitPartReward, 'c', CogDisguiseGlobals.leftArmHand),
    4214: (CogSuitPartReward, 'c', CogDisguiseGlobals.rightArmUpper),
    4215: (CogSuitPartReward, 'c', CogDisguiseGlobals.rightArmLower),
    4216: (CogSuitPartReward, 'c', CogDisguiseGlobals.rightArmHand),
    4300: (CogSuitPartReward, 'v', CogDisguiseGlobals.leftLegUpper),
    4301: (CogSuitPartReward, 'v', CogDisguiseGlobals.leftLegLower),
    4302: (CogSuitPartReward, 'v', CogDisguiseGlobals.leftLegFoot),
    4303: (CogSuitPartReward, 'v', CogDisguiseGlobals.rightLegUpper),
    4304: (CogSuitPartReward, 'v', CogDisguiseGlobals.rightLegLower),
    4305: (CogSuitPartReward, 'v', CogDisguiseGlobals.rightLegFoot),
    4306: (CogSuitPartReward, 'v', CogDisguiseGlobals.torsoLeftShoulder),
    4307: (CogSuitPartReward, 'v', CogDisguiseGlobals.torsoRightShoulder),
    4308: (CogSuitPartReward, 'v', CogDisguiseGlobals.torsoChest),
    4309: (CogSuitPartReward, 'v', CogDisguiseGlobals.torsoHealthMeter),
    4310: (CogSuitPartReward, 'v', CogDisguiseGlobals.torsoPelvis),
    4311: (CogSuitPartReward, 'v', CogDisguiseGlobals.leftArmUpper),
    4312: (CogSuitPartReward, 'v', CogDisguiseGlobals.leftArmLower),
    4313: (CogSuitPartReward, 'v', CogDisguiseGlobals.leftArmHand),
    4314: (CogSuitPartReward, 'v', CogDisguiseGlobals.rightArmUpper),
    4315: (CogSuitPartReward, 'v', CogDisguiseGlobals.rightArmLower),
    4316: (CogSuitPartReward, 'v', CogDisguiseGlobals.rightArmHand),
    4400: (CogSuitPartReward, 'e', CogDisguiseGlobals.leftLegUpper),
    4401: (CogSuitPartReward, 'e', CogDisguiseGlobals.leftLegLower),
    4402: (CogSuitPartReward, 'e', CogDisguiseGlobals.leftLegFoot),
    4403: (CogSuitPartReward, 'e', CogDisguiseGlobals.rightLegUpper),
    4404: (CogSuitPartReward, 'e', CogDisguiseGlobals.rightLegLower),
    4405: (CogSuitPartReward, 'e', CogDisguiseGlobals.rightLegFoot),
    4406: (CogSuitPartReward, 'e', CogDisguiseGlobals.torsoLeftShoulder),
    4407: (CogSuitPartReward, 'e', CogDisguiseGlobals.torsoRightShoulder),
    4408: (CogSuitPartReward, 'e', CogDisguiseGlobals.torsoChest),
    4409: (CogSuitPartReward, 'e', CogDisguiseGlobals.torsoHealthMeter),
    4410: (CogSuitPartReward, 'e', CogDisguiseGlobals.torsoPelvis),
    4411: (CogSuitPartReward, 'e', CogDisguiseGlobals.leftArmUpper),
    4412: (CogSuitPartReward, 'e', CogDisguiseGlobals.leftArmLower),
    4413: (CogSuitPartReward, 'e', CogDisguiseGlobals.leftArmHand),
    4414: (CogSuitPartReward, 'e', CogDisguiseGlobals.rightArmUpper),
    4415: (CogSuitPartReward, 'e', CogDisguiseGlobals.rightArmLower),
    4416: (CogSuitPartReward, 'e', CogDisguiseGlobals.rightArmHand),
    4500: (CogSuitPartReward, 'b', CogDisguiseGlobals.leftLegUpper),
    4501: (CogSuitPartReward, 'b', CogDisguiseGlobals.leftLegLower),
    4502: (CogSuitPartReward, 'b', CogDisguiseGlobals.leftLegFoot),
    4503: (CogSuitPartReward, 'b', CogDisguiseGlobals.rightLegUpper),
    4504: (CogSuitPartReward, 'b', CogDisguiseGlobals.rightLegLower),
    4505: (CogSuitPartReward, 'b', CogDisguiseGlobals.rightLegFoot),
    4506: (CogSuitPartReward, 'b', CogDisguiseGlobals.torsoLeftShoulder),
    4507: (CogSuitPartReward, 'b', CogDisguiseGlobals.torsoRightShoulder),
    4508: (CogSuitPartReward, 'b', CogDisguiseGlobals.torsoChest),
    4509: (CogSuitPartReward, 'b', CogDisguiseGlobals.torsoHealthMeter),
    4510: (CogSuitPartReward, 'b', CogDisguiseGlobals.torsoPelvis),
    4511: (CogSuitPartReward, 'b', CogDisguiseGlobals.leftArmUpper),
    4512: (CogSuitPartReward, 'b', CogDisguiseGlobals.leftArmLower),
    4513: (CogSuitPartReward, 'b', CogDisguiseGlobals.leftArmHand),
    4514: (CogSuitPartReward, 'b', CogDisguiseGlobals.rightArmUpper),
    4515: (CogSuitPartReward, 'b', CogDisguiseGlobals.rightArmLower),
    4516: (CogSuitPartReward, 'b', CogDisguiseGlobals.rightArmHand),
    4600: (CogSuitPartReward, 'z', CogDisguiseGlobals.leftLegUpper),
    4601: (CogSuitPartReward, 'z', CogDisguiseGlobals.leftLegLower),
    4602: (CogSuitPartReward, 'z', CogDisguiseGlobals.leftLegFoot),
    4603: (CogSuitPartReward, 'z', CogDisguiseGlobals.rightLegUpper),
    4604: (CogSuitPartReward, 'z', CogDisguiseGlobals.rightLegLower),
    4605: (CogSuitPartReward, 'z', CogDisguiseGlobals.rightLegFoot),
    4606: (CogSuitPartReward, 'z', CogDisguiseGlobals.torsoLeftShoulder),
    4607: (CogSuitPartReward, 'z', CogDisguiseGlobals.torsoRightShoulder),
    4608: (CogSuitPartReward, 'z', CogDisguiseGlobals.torsoChest),
    4609: (CogSuitPartReward, 'z', CogDisguiseGlobals.torsoHealthMeter),
    4610: (CogSuitPartReward, 'z', CogDisguiseGlobals.torsoPelvis),
    4611: (CogSuitPartReward, 'z', CogDisguiseGlobals.leftArmUpper),
    4612: (CogSuitPartReward, 'z', CogDisguiseGlobals.leftArmLower),
    4613: (CogSuitPartReward, 'z', CogDisguiseGlobals.leftArmHand),
    4614: (CogSuitPartReward, 'z', CogDisguiseGlobals.rightArmUpper),
    4615: (CogSuitPartReward, 'z', CogDisguiseGlobals.rightArmLower),
    4616: (CogSuitPartReward, 'z', CogDisguiseGlobals.rightArmHand),


    # Buff rewards (BuffID, Time):
    # Movement Speed Increase
    3001: (BuffReward, ToontownGlobals.BMovementSpeed, 30),
    3002: (BuffReward, ToontownGlobals.BMovementSpeed, 60),
    3003: (BuffReward, ToontownGlobals.BMovementSpeed, 180),
    3004: (BuffReward, ToontownGlobals.BMovementSpeed, 360),
    10000: (EPPReward, 0), # Bossbot
    10001: (EPPReward, 1), # Lawbot
    10002: (EPPReward, 2), # Cashbot
    10003: (EPPReward, 3), # Sellbot
    10004: (EPPReward, 4),  # Governbot
    10005: (EPPReward, 5), # Eurekabot
    10006: (EPPReward, 6), # Buildbot
    10007: (EPPReward, 7)  # Viralbot
}

BuffRewardIds = [3001, 3002, 3003, 3004]

def getNumTiers():
    return len(RequiredRewardTrackDict) - 1


def isLoopingFinalTier(tier):
    return tier == LOOPING_FINAL_TIER


def getRewardsInTier(tier):
    return RequiredRewardTrackDict.get(tier, [])


def getNumRewardsInTier(tier):
    return len(RequiredRewardTrackDict.get(tier, []))


def rewardTierExists(tier):
    return tier in RequiredRewardTrackDict


def getOptionalRewardsInTier(tier):
    return OptionalRewardTrackDict.get(tier, [])


def getRewardIdFromTrackId(trackId):
    return 401 + trackId


RequiredRewardTrackDict = {
    TT_TIER: (602,),
    TT_TIER + 1: (400,),
    TT_TIER + 2: (101, 801, 500, 802, 803, 100, 804, 805, 102, 806, 807, 100, 808, 200, 809, 101, 810, 811, 812, 813, 700, 814, 815, 300),
    TT_TIER + 3: (900,),
    DD_TIER: (400,),
    DD_TIER + 1: (100, 801, 802, 201, 803, 804, 101, 805, 806, 102, 807, 808, 100, 809, 810, 101, 811, 812, 701, 813, 814, 815, 301),
    DD_TIER + 2: (900,),
    DG_TIER: (100, 202, 101, 102, 100, 101, 501, 702, 302),
    MM_TIER: (400,),
    MM_TIER + 1: (100, 801, 802, 203, 803, 804, 101, 805, 806, 102, 807, 808, 100, 809, 810, 101, 811, 812, 703, 813, 814, 815, 303),
    MM_TIER + 2: (900,),
    BR_TIER: (400,),
    BR_TIER + 1: (100, 801, 802, 704, 803, 804, 101, 805, 806, 502, 807, 808, 102, 809, 810, 204, 811, 812, 100, 813, 814, 101, 815, 304, 10003),
    BR_TIER + 2: (900,),
    DL_TIER: (4000, 100, 205, 101, 102, 705, 103, 305, 4001, 4002),
    DL_TIER + 1: (100, 206, 101, 4003, 4004, 4005, 102, 4006, 4007, 4008, 706, 103, 4009, 4010, 4011, 4000, 4001, 4002),
    DL_TIER + 2: (4006, 4007, 4008, 100, 4000, 4001, 4002, 4003, 101, 4004, 4005, 4009, 102, 103, 4010, 4011),
    DL_TIER + 3: (4009, 4010, 4011, 100, 4000, 4001, 101, 4002, 4003, 102, 4004, 4005, 102, 4006, 4007, 707, 207, 4008, 10002, 10004, 10005, 10006, 10007),
    LAWBOT_HQ_TIER: (4100,),
    LAWBOT_HQ_TIER + 1: (4101,),
    LAWBOT_HQ_TIER + 2: (4102,),
    LAWBOT_HQ_TIER + 3: (4103,),
    LAWBOT_HQ_TIER + 4: (4104,),
    LAWBOT_HQ_TIER + 5: (4105,),
    LAWBOT_HQ_TIER + 6: (4106,),
    LAWBOT_HQ_TIER + 7: (4107,),
    LAWBOT_HQ_TIER + 8: (4108,),
    LAWBOT_HQ_TIER + 9: (4109,),
    LAWBOT_HQ_TIER + 10: (4110,),
    LAWBOT_HQ_TIER + 11: (4111,),
    LAWBOT_HQ_TIER + 12: (4112,),
    LAWBOT_HQ_TIER + 13: (4113,),
    BOSSBOT_HQ_TIER: (4200,),
    BOSSBOT_HQ_TIER + 1: (4201,),
    BOSSBOT_HQ_TIER + 2: (4202,),
    BOSSBOT_HQ_TIER + 3: (4203,),
    BOSSBOT_HQ_TIER + 4: (4204,),
    BOSSBOT_HQ_TIER + 5: (4205,),
    BOSSBOT_HQ_TIER + 6: (4206,),
    BOSSBOT_HQ_TIER + 7: (4207,),
    BOSSBOT_HQ_TIER + 8: (4208,),
    BOSSBOT_HQ_TIER + 9: (4209, 4210, 4211, 4212, 4213, 4214,),
    BOSSBOT_HQ_TIER + 15: (4215,),
    BOSSBOT_HQ_TIER + 16: (4216,),
    BOSSBOT_HQ_TIER: (4300,),
    GOVERNBOT_HQ_TIER + 1: (4301,),
    GOVERNBOT_HQ_TIER + 2: (4302,),
    GOVERNBOT_HQ_TIER + 3: (4303,),
    GOVERNBOT_HQ_TIER + 4: (4304,),
    GOVERNBOT_HQ_TIER + 5: (4305,),
    GOVERNBOT_HQ_TIER + 6: (4306,),
    GOVERNBOT_HQ_TIER + 7: (4307,),
    GOVERNBOT_HQ_TIER + 8: (4308,),
    GOVERNBOT_HQ_TIER + 9: (4309, 4310, 4311, 4312, 4313, 4314,),
    GOVERNBOT_HQ_TIER + 15: (4315,),
    GOVERNBOT_HQ_TIER + 16: (4316,),
    EUREKABOT_HQ_TIER + 1: (4401,),
    EUREKABOT_HQ_TIER + 2: (4402,),
    EUREKABOT_HQ_TIER + 3: (4403,),
    EUREKABOT_HQ_TIER + 4: (4404,),
    EUREKABOT_HQ_TIER + 5: (4405,),
    EUREKABOT_HQ_TIER + 6: (4406,),
    EUREKABOT_HQ_TIER + 7: (4407,),
    EUREKABOT_HQ_TIER + 8: (4408,),
    EUREKABOT_HQ_TIER + 9: (4409, 4410, 4411, 4412, 4413, 4414,),
    EUREKABOT_HQ_TIER + 15: (4415,),
    EUREKABOT_HQ_TIER + 16: (4416,),
    BUILDBOT_HQ_TIER + 1: (4501,),
    BUILDBOT_HQ_TIER + 2: (4502,),
    BUILDBOT_HQ_TIER + 3: (4503,),
    BUILDBOT_HQ_TIER + 4: (4504,),
    BUILDBOT_HQ_TIER + 5: (4505,),
    BUILDBOT_HQ_TIER + 6: (4506,),
    BUILDBOT_HQ_TIER + 7: (4507,),
    BUILDBOT_HQ_TIER + 8: (4508,),
    BUILDBOT_HQ_TIER + 9: (4509, 4510, 4511, 4512, 4513, 4514,),
    BUILDBOT_HQ_TIER + 15: (4515),
    BUILDBOT_HQ_TIER + 16: (4516,),
    VIRALBOT_HQ_TIER + 1: (4601,),
    VIRALBOT_HQ_TIER + 2: (4602,),
    VIRALBOT_HQ_TIER + 3: (4603,),
    VIRALBOT_HQ_TIER + 4: (4604,),
    VIRALBOT_HQ_TIER + 5: (4605,),
    VIRALBOT_HQ_TIER + 6: (4606,),
    VIRALBOT_HQ_TIER + 7: (4607,),
    VIRALBOT_HQ_TIER + 8: (4608,),
    VIRALBOT_HQ_TIER + 9: (4609, 4610, 4611, 4612, 4613, 4614,),
    VIRALBOT_HQ_TIER + 15: (4615,),
    VIRALBOT_HQ_TIER + 16: (4616,),
    PRE_ELDER_TIER: (10001, 10000),
    ELDER_TIER: (4000, 4001, 4002, 4003, 4004, 4005, 4006, 4007, 4008, 4009, 4010, 4011)}

OptionalRewardTrackDict = {
    TT_TIER: (),
    TT_TIER + 1: (),
    TT_TIER + 2: (1000, 603, 603, 604, 604, 2205, 2206, 2205, 2206, 3001, 3001, 3001, 3001),
    TT_TIER + 3: (604, 605, 605, 606, 2205, 2206, 2205, 2206, 3002, 3001, 3001, 3001),
    DD_TIER: (1000, 605, 605, 606, 606, 2101, 2102, 2105, 2106, 3002, 3002, 3002, 3001),
    DD_TIER + 1: (1000, 605, 606, 605, 605, 2101, 2102, 2105, 2106, 3002, 3002, 3002, 3001),
    DD_TIER + 2: (1000, 605, 604, 605, 606, 2101, 2102, 2105, 2106, 3002, 3002, 3002, 3002),
    DG_TIER: (1000, 607, 608, 609, 610, 2501, 2502, 2503, 2504, 2505, 2506, 3002, 3002, 3002, 3002),
    MM_TIER: (1000, 609, 610, 611, 609, 2403, 2404, 2405, 2406, 2407, 2408, 2409, 3002, 3002, 3002, 3002),
    MM_TIER + 1: (1000, 611, 612, 612, 612, 2403, 2404, 2405, 2406, 2407, 2408, 2409, 3003, 3003, 3002, 3002),
    MM_TIER + 2: (1000, 612, 612, 613, 613, 2403, 2404, 2405, 2406, 2407, 2408, 2409, 3003, 3003, 3002, 3002),
    BR_TIER: (1000, 2305, 2306, 2307, 2308, 2309, 2310, 2311, 3003, 3003, 3003, 3003),
    BR_TIER + 1: (1000, 2305, 2306, 2307, 2308, 2309, 2310, 2311, 3003, 3003, 3003, 3003),
    BR_TIER + 2: (1000, 2305, 2306, 2307, 2308, 2309, 2310, 2311, 3003, 3003, 3003, 3003),
    DL_TIER: (2901, 2902, 2907, 2908, 2909, 2910, 2911, 3003, 3003, 3004, 3004),
    DL_TIER + 1: (1000, 2923, 2924, 2927, 2928, 2929, 2930, 2931, 3003, 3003, 3004, 3004),
    DL_TIER + 2: (2941, 2942, 2943, 2944, 2947, 2948, 2949, 2950, 2951, 3004, 3004, 3004, 3004),
    DL_TIER + 3: (1000, 2961, 2962, 2963, 2964, 2965, 2966, 2967, 2968, 2969, 2970, 2971, 3004, 3004, 3004, 3004),
    ELDER_TIER: (1000, 1000, 615, 616, 617, 618, 619, 620, 2961, 2962, 2963, 2964, 2965, 2966, 2967, 2968, 2969, 2970, 2971, 3004, 3004, 3004)
}

def isRewardOptional(tier, rewardId):
    return tier in OptionalRewardTrackDict and rewardId in OptionalRewardTrackDict[tier]


def getItemName(itemId):
    return ItemDict[itemId][0]


def getPluralItemName(itemId):
    return ItemDict[itemId][1]


def avatarHasTrolleyQuest(av):
    return len(av.quests) == 1 and av.quests[0][0] == TROLLEY_QUEST_ID


def avatarHasCompletedTrolleyQuest(av):
    return av.quests[0][4] > 0


def avatarHasFirstCogQuest(av):
    return len(av.quests) == 1 and av.quests[0][0] == FIRST_COG_QUEST_ID


def avatarHasCompletedFirstCogQuest(av):
    return av.quests[0][4] > 0


def avatarHasFriendQuest(av):
    return len(av.quests) == 1 and av.quests[0][0] == FRIEND_QUEST_ID


def avatarHasCompletedFriendQuest(av):
    return av.quests[0][4] > 0


def avatarHasPhoneQuest(av):
    return len(av.quests) == 1 and av.quests[0][0] == PHONE_QUEST_ID


def avatarHasCompletedPhoneQuest(av):
    return av.quests[0][4] > 0


def avatarWorkingOnRequiredRewards(av):
    tier = av.getRewardTier()
    rewardList = list(getRewardsInTier(tier))
    for i in xrange(len(rewardList)):
        actualRewardId = transformReward(rewardList[i], av)
        rewardList[i] = actualRewardId

    for questDesc in av.quests:
        questId = questDesc[0]
        rewardId = questDesc[3]
        if rewardId in rewardList:
            return 1
        elif rewardId == NA:
            rewardId = transformReward(getFinalRewardId(questId, fAll=1), av)
            if rewardId in rewardList:
                return 1

    return 0


def avatarHasAllRequiredRewards(av, tier):
    # Get the reward history.
    rewardHistory = list(av.getRewardHistory()[1])

    # Delete quests we're working on from the reward History.
    avQuests = av.getQuests()

    # Iterate through the current quests.
    for i in xrange(0, len(avQuests), 5):
        questDesc = avQuests[i:i + 5]
        questId, fromNpcId, toNpcId, rewardId, toonProgress = questDesc
        transformedRewardId = transformReward(rewardId, av)

        if rewardId in rewardHistory:
            rewardHistory.remove(rewardId)

        if transformedRewardId in rewardHistory:
            rewardHistory.remove(transformedRewardId)

    rewardList = getRewardsInTier(tier)
    notify.debug('checking avatarHasAllRequiredRewards: history: %s, tier: %s' % (rewardHistory, rewardList))
    for rewardId in rewardList:
        if rewardId == 900:
            found = 0
            for actualRewardId in (901, 902, 903, 904, 905, 906, 907):
                if actualRewardId in rewardHistory:
                    found = 1
                    rewardHistory.remove(actualRewardId)
                    if notify.getDebug():
                        notify.debug('avatarHasAllRequiredRewards: rewardId 900 found as: %s' % actualRewardId)
                    break

            if not found:
                if notify.getDebug():
                    notify.debug('avatarHasAllRequiredRewards: rewardId 900 not found')
                return 0
        else:
            actualRewardId = transformReward(rewardId, av)
            if actualRewardId in rewardHistory:
                rewardHistory.remove(actualRewardId)
            elif getRewardClass(rewardId) == CogSuitPartReward:
                deptStr = RewardDict.get(rewardId)[1]
                cogPart = RewardDict.get(rewardId)[2]
                dept = ToontownGlobals.cogDept2index[deptStr]
                if av.hasCogPart(cogPart, dept):
                    if notify.getDebug():
                        notify.debug('avatarHasAllRequiredRewards: rewardId: %s counts, avatar has cog part: %s dept: %s' % (actualRewardId, cogPart, dept))
                else:
                    if notify.getDebug():
                        notify.debug('avatarHasAllRequiredRewards: CogSuitPartReward: %s not found' % actualRewardId)
                    return 0
            else:
                if notify.getDebug():
                    notify.debug('avatarHasAllRequiredRewards: rewardId %s not found' % actualRewardId)
                return 0

    if notify.getDebug():
        notify.debug('avatarHasAllRequiredRewards: remaining rewards: %s' % rewardHistory)
        for rewardId in rewardHistory:
            if not isRewardOptional(tier, rewardId):
                notify.warning('required reward found, expected only optional: %s' % rewardId)

    return 1


def nextQuestList(nextQuest):
    if nextQuest == NA:
        return None
    seqTypes = (types.ListType, types.TupleType)
    if type(nextQuest) in seqTypes:
        return nextQuest
    else:
        return (nextQuest,)
    return None


def checkReward(questId, forked = 0):
    quest = QuestDict[questId]
    reward = quest[5]
    nextQuests = nextQuestList(quest[6])
    if nextQuests is None:
        validRewards = RewardDict.keys() + [Any,
         AnyCashbotSuitPart,
         AnyLawbotSuitPart,
         AnyGovernbotSuitPart,
         AnyEurekabotSuitPart,
         AnyBuildbotSuitPart,
         AnyViralbotSuitPart,
         OBSOLETE]
        if reward is OBSOLETE:
            print 'warning: quest %s is obsolete' % questId
        return reward
    else:
        forked = forked or len(nextQuests) > 1
        firstReward = checkReward(nextQuests[0], forked)
        for qId in nextQuests[1:]:
            thisReward = checkReward(qId, forked)

        return firstReward
    return


def assertAllQuestsValid():
    print 'checking quests...'
    for questId in QuestDict.keys():
        try:
            quest = getQuest(questId)
        except AssertionError, e:
            err = 'invalid quest: %s' % questId
            print err
            raise

    for questId in QuestDict.keys():
        quest = QuestDict[questId]
        tier, start, questDesc, fromNpc, toNpc, reward, nextQuest, dialog = quest
        if start:
            checkReward(questId)
