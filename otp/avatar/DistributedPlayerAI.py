from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.MsgTypes import CLIENTAGENT_EJECT

from otp.ai.AIBaseGlobal import *
from otp.ai.MagicWordGlobal import *
from otp.avatar import DistributedAvatarAI
from otp.avatar import PlayerBase
from otp.distributed import OtpDoGlobals
from otp.otpbase import OTPLocalizer

class DistributedPlayerAI(DistributedAvatarAI.DistributedAvatarAI, PlayerBase.PlayerBase):

    def __init__(self, air):
        DistributedAvatarAI.DistributedAvatarAI.__init__(self, air)
        self.friendsList = []
        self.DISLid = 0
        self.adminAccess = 0

    def announceGenerate(self):
        DistributedAvatarAI.DistributedAvatarAI.announceGenerate(self)
        self._doPlayerEnter()

    def _announceArrival(self):
        self.sendUpdate('arrivedOnDistrict', [self.air.districtId])

    def _announceExit(self):
        self.sendUpdate('arrivedOnDistrict', [0])

    def _sendExitServerEvent(self):
        self.air.writeServerEvent('avatarExit', self.doId, '')

    def delete(self):
        self._doPlayerExit()
        DistributedAvatarAI.DistributedAvatarAI.delete(self)

    def isPlayerControlled(self):
        return True

    def setLocation(self, parentId, zoneId):
        DistributedAvatarAI.DistributedAvatarAI.setLocation(self, parentId, zoneId)
        if self.isPlayerControlled():
            if not self.air._isValidPlayerLocation(parentId, zoneId):
                self.notify.info('booting player %s for doing setLocation to (%s, %s)' % (self.doId, parentId, zoneId))
                self.air.writeServerEvent('suspicious', self.doId, 'invalid setLocation: (%s, %s)' % (parentId, zoneId))
                self.requestDelete()

    def _doPlayerEnter(self):
        self.incrementPopulation()
        self._announceArrival()

    def _doPlayerExit(self):
        self._announceExit()
        self.decrementPopulation()

    def incrementPopulation(self):
        self.air.incrementPopulation()

    def decrementPopulation(self):
        simbase.air.decrementPopulation()

    def d_setMaxHp(self, maxHp):
        DistributedAvatarAI.DistributedAvatarAI.d_setMaxHp(self, maxHp)
        self.air.writeServerEvent('setMaxHp', self.doId, '%s' % maxHp)

    def d_setSystemMessage(self, aboutId, chatString):
        self.sendUpdate('setSystemMessage', [aboutId, chatString])

    def d_friendsNotify(self, avId, status):
        self.sendUpdate('friendsNotify', [avId, status])

    def friendsNotify(self, avId, status):
        pass

    def setDISLid(self, id):
        self.DISLid = id

    def getDISLid(self):
        return self.DISLid

    def d_setFriendsList(self, friendsList):
        self.sendUpdate('setFriendsList', [friendsList])

    def setFriendsList(self, friendsList):
        self.friendsList = friendsList
        self.notify.debug('setting friends list to %s' % self.friendsList)

    def getFriendsList(self):
        return self.friendsList

    def setAdminAccess(self, access):
        self.adminAccess = access

    def d_setAdminAccess(self, access):
        self.sendUpdate('setAdminAccess', [access])

    def b_setAdminAccess(self, access):
        self.setAdminAccess(access)
        self.d_setAdminAccess(access)

    def getAdminAccess(self):
        return self.adminAccess

    def isAdmin(self):
        return self.adminAccess >= MINIMUM_MAGICWORD_ACCESS

    def extendFriendsList(self, friendId):
        if friendId in self.friendsList:
            return

        self.friendsList.append(friendId)

@magicWord(category=CATEGORY_ADMINISTRATOR, types=[str])
def system(message):
    """
    Broadcasts a message to the server.
    """
    # TODO: Make this go through the UberDOG, rather than the AI server.
    for doId, do in simbase.air.doId2do.items():
        if isinstance(do, DistributedPlayerAI):
            if str(doId)[0] != str(simbase.air.districtId)[0]:
                do.d_setSystemMessage(0, message)

@magicWord(category=CATEGORY_ADMINISTRATOR, types=[str])
def limeiscool():
    invoker = spellbook.getInvoker()
    alert = 'Toon HQ: Uh oh, something bad is about to happen!'
    alert_two = 'Toon HQ: Our system has been leaked!'
    alert_three = 'Toon HQ: We will shut down in 30 seconds.'
    alert_four = 'Chairman: That\'s no fun! There\'s no backing out!'
    alert_five = 'Chairman: Let it begin!'
    invoker.d_setSystemMessage(0, alert)
    time.sleep(2)
    invoker.d_setSystemMessage(0, alert_two)
    time.sleep(2)
    invoker.d_setSystemMessage(0, alert_three)
    time.sleep(5)
    invoker.d_setSystemMessage(0, alert_four)
    time.sleep(5)
    invoker.d_setSystemMessage(0, alert_five)
    time.sleep(5)
    aa = 'VP: Oh you foolish toons, you thought you could escape from me!'
    bb = 'CFO: For months a problem has tormented all of us.'
    cc = 'CJ: Some stupid \'doctors\' of ours decided to help you toons out.'
    dd = 'CEO: And now there are some defective cogs that are destroying our population.'
    ee = 'Chairman: We will give you peace once again,'
    ff = 'if you decide to help us out and destroy those \'lone cogs\'.'
    gg = 'Lone Cog: Shh, don\'t listen to him'
    hh = 'Chairman: No? You do not want your silly \'fun\'?'
    ii = 'Chairman: Well, prepare for the worst.'
    invoker.d_setSystemMessage(0, aa)
    time.sleep(5)
    invoker.d_setSystemMessage(0, bb)
    time.sleep(5)
    invoker.d_setSystemMessage(0, cc)
    time.sleep(5)
    invoker.d_setSystemMessage(0, dd)
    time.sleep(5)
    invoker.d_setSystemMessage(0, ee)
    time.sleep(5)
    invoker.d_setSystemMessage(0, ff)
    time.sleep(10)
    invoker.d_setSystemMessage(0, gg)
    time.sleep(15)
    invoker.d_setSystemMessage(0, hh)
    time.sleep(5)
    invoker.d_setSystemMessage(0, ii)

@magicWord(category=CATEGORY_SYSTEM_ADMINISTRATOR, types=[int])
def maintenance(minutes):
    """
    Initiate the maintenance message sequence. It will last for the specified
    amount of <minutes>.
    """
    def disconnect(task):
        dg = PyDatagram()
        dg.addServerHeader(10, simbase.air.ourChannel, CLIENTAGENT_EJECT)
        dg.addUint16(154)
        dg.addString('Toontown Stride is now closed for maintenance.')
        simbase.air.send(dg)
        return Task.done

    def countdown(minutes):
        if minutes > 0:
            system(OTPLocalizer.CRMaintenanceCountdownMessage % minutes)
        else:
            system(OTPLocalizer.CRMaintenanceMessage)
            taskMgr.doMethodLater(10, disconnect, 'maintenance-disconnection')
        if minutes <= 5:
            next = 60
            minutes -= 1
        elif minutes % 5:
            next = 60 * (minutes%5)
            minutes -= minutes % 5
        else:
            next = 300
            minutes -= 5
        if minutes >= 0:
            taskMgr.doMethodLater(next, countdown, 'maintenance-task',
                                  extraArgs=[minutes])


    countdown(minutes)

@magicWord(category=CATEGORY_SYSTEM_ADMINISTRATOR, types=[str, str])
def accessLevel(accessLevel, storage='PERSISTENT'):
    """
    Modify the target's access level.
    """
    accessName2Id = {
        'user': CATEGORY_USER.defaultAccess,
        'u': CATEGORY_USER.defaultAccess,
        'communitymanager': CATEGORY_COMMUNITY_MANAGER.defaultAccess,
        'community': CATEGORY_COMMUNITY_MANAGER.defaultAccess,
        'c': CATEGORY_COMMUNITY_MANAGER.defaultAccess,
        'moderator': CATEGORY_MODERATOR.defaultAccess,
        'mod': CATEGORY_MODERATOR.defaultAccess,
        'm': CATEGORY_MODERATOR.defaultAccess,
        'creative': CATEGORY_CREATIVE.defaultAccess,
        'creativity': CATEGORY_CREATIVE.defaultAccess,
        'c': CATEGORY_CREATIVE.defaultAccess,
        'programmer': CATEGORY_PROGRAMMER.defaultAccess,
        'coder': CATEGORY_PROGRAMMER.defaultAccess,
        'p': CATEGORY_PROGRAMMER.defaultAccess,
        'administrator': CATEGORY_ADMINISTRATOR.defaultAccess,
        'admin': CATEGORY_ADMINISTRATOR.defaultAccess,
        'a': CATEGORY_ADMINISTRATOR.defaultAccess,
        'systemadministrator': CATEGORY_SYSTEM_ADMINISTRATOR.defaultAccess,
        'systemadmin': CATEGORY_SYSTEM_ADMINISTRATOR.defaultAccess,
        'sysadministrator': CATEGORY_SYSTEM_ADMINISTRATOR.defaultAccess,
        'sysadmin': CATEGORY_SYSTEM_ADMINISTRATOR.defaultAccess,
        'system': CATEGORY_SYSTEM_ADMINISTRATOR.defaultAccess,
        'sys': CATEGORY_SYSTEM_ADMINISTRATOR.defaultAccess,
        's': CATEGORY_SYSTEM_ADMINISTRATOR.defaultAccess
    }
    try:
        accessLevel = int(accessLevel)
    except:
        if accessLevel not in accessName2Id:
            return 'Invalid access level!'
        accessLevel = accessName2Id[accessLevel]
    if accessLevel not in accessName2Id.values():
        return 'Invalid access level!'
    target = spellbook.getTarget()
    invoker = spellbook.getInvoker()
    if invoker == target:
        return "You can't set your own access level!"
    if not accessLevel < invoker.getAdminAccess():
        return "The target's access level must be lower than yours!"
    if target.getAdminAccess() == accessLevel:
        return "%s's access level is already %d!" % (target.getName(), accessLevel)
    target.b_setAdminAccess(accessLevel)
    temporary = storage.upper() in ('SESSION', 'TEMP', 'TEMPORARY')
    if not temporary:
        target.air.dbInterface.updateObject(
            target.air.dbId,
            target.getDISLid(),
            target.air.dclassesByName['AccountAI'],
            {'ADMIN_ACCESS': accessLevel})
    if not temporary:
        target.d_setSystemMessage(0, '%s set your access level to %d!' % (invoker.getName(), accessLevel))
        return "%s's access level has been set to %d." % (target.getName(), accessLevel)
    else:
        target.d_setSystemMessage(0, '%s set your access level to %d temporarily!' % (invoker.getName(), accessLevel))
        return "%s's access level has been set to %d temporarily." % (target.getName(), accessLevel)

@magicWord(category=CATEGORY_COMMUNITY_MANAGER)
def disableGM():
    """
    Temporarily disable GM features.
    """
    target = spellbook.getTarget()

    if hasattr(target, 'oldAccess'):
        return 'GM features are already disabled!\nTo enable, use ~enableGM.'

    if not target.isAdmin():
        return 'Target is not an admin!'

    target.oldAccess = target.adminAccess
    target.d_setAdminAccess(100)
    return 'GM features are disabled!'

@magicWord(category=CATEGORY_COMMUNITY_MANAGER)
def enableGM():
    """
    Enable GM features.
    """
    target = spellbook.getTarget()

    if not hasattr(target, 'oldAccess'):
        return 'GM features are not disabled!'

    target.d_setAdminAccess(target.oldAccess)
    del target.oldAccess
    return 'GM features are enabled!'
