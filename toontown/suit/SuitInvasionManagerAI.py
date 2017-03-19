import time, random

from toontown.battle import SuitBattleGlobals
from toontown.suit import SuitDNA
from toontown.suit.SuitInvasionGlobals import *
from toontown.toonbase import ToontownGlobals


class SuitInvasionManagerAI:
    def __init__(self, air):
        self.air = air

        self.invading = False
        self.start = 0
        self.remaining = 0
        self.total = 0
        self.suitDeptIndex = None
        self.suitTypeIndex = None
        self.flags = 0

        self.air.accept(
            'startInvasion', self.handleStartInvasion)
        self.air.accept(
            'stopInvasion', self.handleStopInvasion)

        # We want to handle shard status queries so that a ShardStatusReceiver
        # being created after we're created will know where we're at:
        self.air.accept('queryShardStatus', self.sendInvasionStatus)

        self.sendInvasionStatus()

    def getInvading(self):
        return self.invading

    def getInvadingCog(self):
        return (self.suitDeptIndex, self.suitTypeIndex, self.flags)

    def startInvasion(self, suitDeptIndex=None, suitTypeIndex=None, flags=0,
                      type=INVASION_TYPE_NORMAL):
        if self.invading:
            # An invasion is currently in progress; ignore this request.
            return False

        if (suitDeptIndex is None) and (suitTypeIndex is None) and (not flags):
            # This invasion is no-op.
            return False

        if (suitDeptIndex is None) and (suitTypeIndex is not None):
            # It's impossible to determine the invading Cog.
            return False

        if flags not in (0, IFV2, IFSkelecog, IFWaiter, IFGold):
            # The provided flag combination is not possible.
            return False

        if (suitDeptIndex is not None) and (suitDeptIndex >= len(SuitDNA.suitDepts)):
            # Invalid suit department.
            return False

        if (suitTypeIndex is not None) and (suitTypeIndex >= SuitDNA.suitsPerDept):
            # Invalid suit type.
            return False

        if type not in (INVASION_TYPE_NORMAL, INVASION_TYPE_MEGA, INVASION_TYPE_BRUTAL):
            # Invalid invasion type.
            return False

        # Looks like we're all good. Begin the invasion:
        self.invading = True
        self.start = int(time.time())
        self.suitDeptIndex = suitDeptIndex
        self.suitTypeIndex = suitTypeIndex
        self.flags = flags

        # How many suits do we want?
        if type == INVASION_TYPE_NORMAL:
            self.total = random.randint(3000, 6000)
        elif type == INVASION_TYPE_MEGA:
            self.total = 8000
        elif type == INVASION_TYPE_BRUTAL:
            self.total = 10000
        self.remaining = self.total

        self.flySuits()
        self.notifyInvasionStarted()

        # Update the invasion tracker on the districts page in the Shticker Book:
        if self.suitDeptIndex is not None:
            self.air.districtStats.b_setInvasionStatus(self.suitDeptIndex + 1)
        else:
            self.air.districtStats.b_setInvasionStatus(5)

        # If this is a normal invasion, and the players take too long to defeat
        # all of the Cogs, we'll want the invasion to timeout:
        if type == INVASION_TYPE_NORMAL:
            timeout = config.GetInt('invasion-timeout', 1800)
            taskMgr.doMethodLater(timeout, self.stopInvasion, 'invasionTimeout')

        # If this is a mega invasion, and the players take to long to defeat
        # all of the cogs, we want the invasion to take a bit longer to timeout:
        if type == INVASION_TYPE_MEGA:
            timeout = config.GetInt('invasion-timeout', 3200)

        # If this is a brutal invasion, the players will have a very long time to
        # Defeat the cogs before the invasion times out:
        if type == INVASION_TYPE_BRUTAL:
            timeout = config.GetInt('invasion-timeout', 10000)

        self.sendInvasionStatus()
        return True

    def stopInvasion(self, task=None):
        if not self.invading:
            # We are not currently invading.
            return False

        # Stop the invasion timeout task:
        taskMgr.remove('invasionTimeout')

        # Update the invasion tracker on the districts page in the Shticker Book:
        self.air.districtStats.b_setInvasionStatus(0)

        # Revert what was done when the invasion started:
        self.notifyInvasionEnded()
        self.invading = False
        self.start = 0
        self.suitDeptIndex = None
        self.suitTypeIndex = None
        self.flags = 0
        self.total = 0
        self.remaining = 0
        self.flySuits()

        self.sendInvasionStatus()
        return True

    def getSuitName(self):
        if self.suitDeptIndex is not None:
            if self.suitTypeIndex is not None:
                return SuitDNA.getSuitName(self.suitDeptIndex, self.suitTypeIndex)
            else:
                return SuitDNA.suitDepts[self.suitDeptIndex]
        else:
            return SuitDNA.suitHeadTypes[0]

    def notifyInvasionStarted(self):
        msgType = ToontownGlobals.SuitInvasionBegin
        if self.flags & IFSkelecog:
            msgType = ToontownGlobals.SkelecogInvasionBegin
        elif self.flags & IFWaiter:
            msgType = ToontownGlobals.WaiterInvasionBegin
        elif self.flags & IFGold:
            msgType = ToontownGlobals.GoldInvasionBegin
        elif self.flags & IFV2:
            msgType = ToontownGlobals.V2InvasionBegin
        self.air.newsManager.sendUpdate(
            'setInvasionStatus',
            [msgType, self.getSuitName(), self.total, self.flags])

    def notifyInvasionEnded(self):
        msgType = ToontownGlobals.SuitInvasionEnd
        if self.flags & IFSkelecog:
            msgType = ToontownGlobals.SkelecogInvasionEnd
        elif self.flags & IFWaiter:
            msgType = ToontownGlobals.WaiterInvasionEnd
        elif self.flags & IFGold:
            msgType = ToontownGlobals.GoldInvasionEnd
        elif self.flags & IFV2:
            msgType = ToontownGlobals.V2InvasionEnd
        self.air.newsManager.sendUpdate(
            'setInvasionStatus', [msgType, self.getSuitName(), 0, self.flags])

    def notifyInvasionUpdate(self):
        self.air.newsManager.sendUpdate(
            'setInvasionStatus',
            [ToontownGlobals.SuitInvasionUpdate, self.getSuitName(),
             self.remaining, self.flags])

    def notifyInvasionBulletin(self, avId):
        msgType = ToontownGlobals.SuitInvasionBulletin
        if self.flags & IFSkelecog:
            msgType = ToontownGlobals.SkelecogInvasionBulletin
        elif self.flags & IFWaiter:
            msgType = ToontownGlobals.WaiterInvasionBulletin
        elif self.flags & IFGold:
            msgType = ToontownGlobals.GoldInvasionBulletin
        elif self.flags & IFV2:
            msgType = ToontownGlobals.V2InvasionBulletin
        self.air.newsManager.sendUpdateToAvatarId(
            avId, 'setInvasionStatus',
            [msgType, self.getSuitName(), self.remaining, self.flags])

    def flySuits(self):
        for suitPlanner in self.air.suitPlanners.values():
            suitPlanner.flySuits()

    def handleSuitDefeated(self):
        self.remaining -= 1
        if self.remaining == 0:
            self.stopInvasion()
        elif self.remaining == (self.total/2):
            self.notifyInvasionUpdate()
        self.sendInvasionStatus()

    def handleStartInvasion(self, shardId, *args):
        if shardId == self.air.ourChannel:
            self.startInvasion(*args)

    def handleStopInvasion(self, shardId):
        if shardId == self.air.ourChannel:
            self.stopInvasion()

    def sendInvasionStatus(self):
        if self.invading:
            if self.suitDeptIndex is not None:
                if self.suitTypeIndex is not None:
                    type = SuitBattleGlobals.SuitAttributes[self.getSuitName()]['name']
                else:
                    type = SuitDNA.getDeptFullname(self.getSuitName())
            else:
                type = None
            status = {
                'invasion': {
                    'type': type,
                    'flags': self.flags,
                    'remaining': self.remaining,
                    'total': self.total,
                    'start': self.start
                }
            }
        else:
            status = {'invasion': None}
        self.air.sendNetEvent('shardStatus', [self.air.ourChannel, status])

    def cleanupInvasion(self, task=None):
        self.stopInvasion()
        self.suitDeptIndex = None
        self.suitTypeIndex = None
        self.isSkelecog = 0
        self.isWaiter = 0
        self.isV2 = 0
        self.isGold = 0
        self.cleanupCurrentSuits()

        if task:
            return task.done

    def cleanupCurrentSuits(self):
        for suitPlanner in self.air.suitPlanners:
            self.air.suitPlanners.get(suitPlanner).flySuits()

    def cleanupTasks(self):
        taskMgr.remove('suitInvasionManager-cleanup')



