from otp.chat.ChatInputWhiteListFrame import ChatInputWhiteListFrame
from direct.showbase import DirectObject
from otp.otpbase import OTPGlobals
import sys
from direct.gui.DirectGui import *
from panda3d.core import *
from otp.chat import ChatUtil
from otp.otpbase import OTPLocalizer
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import ToontownGlobals

class TTChatInputWhiteList(ChatInputWhiteListFrame):
    notify = DirectNotifyGlobal.directNotify.newCategory('TTChatInputWhiteList')
    TFToggleKey = base.config.GetString('true-friend-toggle-key', 'alt')
    TFToggleKeyUp = TFToggleKey + '-up'

    def __init__(self, parent = None, **kw):
        entryOptions = {'parent': self,
         'relief': DGG.SUNKEN,
         'scale': 0.05,
         'frameColor': (0.9, 0.9, 0.85, 0.0),
         'pos': (-0.2, 0, 0.11),
         'entryFont': OTPGlobals.getInterfaceFont(),
         'width': 8.6,
         'numLines': 3,
         'cursorKeys': 0,
         'backgroundFocus': 0,
         'suppressKeys': 0,
         'suppressMouse': 1,
         'command': self.sendChat,
         'focus': 0,
         'text': '',
         'sortOrder': DGG.FOREGROUND_SORT_INDEX}
        ChatInputWhiteListFrame.__init__(self, entryOptions, parent, **kw)
        base.ttwl = self
        self.autoOff = 1
        self.sendBy = 'Data'
        self.prefilter = 0
        self.promoteWhiteList = 1
        self.typeGrabbed = 0
        self.deactivate()
        gui = loader.loadModel('phase_3.5/models/gui/chat_input_gui')
        self.chatFrame = DirectFrame(parent=self, image=gui.find('**/Chat_Bx_FNL'), relief=None, pos=(0.0, 0, 0.0), state=DGG.NORMAL)
        self.chatButton = DirectButton(parent=self.chatFrame, image=(gui.find('**/ChtBx_ChtBtn_UP'), gui.find('**/ChtBx_ChtBtn_DN'), gui.find('**/ChtBx_ChtBtn_RLVR')), pos=(0.182, 0, -0.088), relief=None, text=('', OTPLocalizer.ChatInputNormalSayIt, OTPLocalizer.ChatInputNormalSayIt), text_scale=0.06, text_fg=Vec4(1, 1, 1, 1), text_shadow=Vec4(0, 0, 0, 1), text_pos=(0, -0.09), textMayChange=0, command=self.chatButtonPressed)
        self.cancelButton = DirectButton(parent=self.chatFrame, image=(gui.find('**/CloseBtn_UP'), gui.find('**/CloseBtn_DN'), gui.find('**/CloseBtn_Rllvr')), pos=(-0.151, 0, -0.088), relief=None, text=('', OTPLocalizer.ChatInputNormalCancel, OTPLocalizer.ChatInputNormalCancel), text_scale=0.06, text_fg=Vec4(1, 1, 1, 1), text_shadow=Vec4(0, 0, 0, 1), text_pos=(0, -0.09), textMayChange=0, command=self.cancelButtonPressed)
        self.whisperLabel = DirectLabel(parent=self.chatFrame, pos=(0.02, 0, 0.23), relief=DGG.FLAT, frameColor=(1, 1, 0.5, 1), frameSize=(-0.23,
         0.23,
         -0.07,
         0.05), text=OTPLocalizer.ChatInputNormalWhisper, text_scale=0.04, text_fg=Vec4(0, 0, 0, 1), text_wordwrap=9.5, textMayChange=1)
        self.chatEntry.bind(DGG.OVERFLOW, self.chatOverflow)
        self.chatEntry.bind(DGG.TYPE, self.typeCallback)
        self.trueFriendChat = 0
        if base.config.GetBool('whisper-to-nearby-true-friends', 1):
            self.accept(self.TFToggleKey, self.shiftPressed)
        return

    def shiftPressed(self):
        self.ignore(self.TFToggleKey)
        self.trueFriendChat = 1
        self.accept(self.TFToggleKeyUp, self.shiftReleased)

    def shiftReleased(self):
        self.ignore(self.TFToggleKeyUp)
        self.trueFriendChat = 0
        self.accept(self.TFToggleKey, self.shiftPressed)

    def handleTypeGrab(self):
        self.ignore('typeEntryGrab')
        self.accept('typeEntryRelease', self.handleTypeRelease)
        self.typeGrabbed = 1

    def handleTypeRelease(self):
        self.ignore('typeEntryRelease')
        self.accept('typeEntryGrab', self.handleTypeGrab)
        self.typeGrabbed = 0

    def typeCallback(self, extraArgs):
        if self.typeGrabbed:
            return
        self.applyFilter(extraArgs)
        if localAvatar.chatMgr.chatInputWhiteList.isActive():
            return
        messenger.send('wakeup')
        messenger.send('enterNormalChat')

    def destroy(self):
        self.chatEntry.destroy()
        self.chatFrame.destroy()
        self.ignoreAll()
        ChatInputWhiteListFrame.destroy(self)

    def delete(self):
        ChatInputWhiteListFrame.delete(self)
        return

    def sendChat(self, text, overflow = False):
        if self.typeGrabbed:
            return
        else:
            ChatInputWhiteListFrame.sendChat(self, self.chatEntry.get())

    def sendChatByData(self, text):
        if self.trueFriendChat:
            for friendId in base.localAvatar.friendsList:
                if base.localAvatar.isTrueFriends(friendId):
                    self.sendWhisperByFriend(friendId, text)
        elif self.receiverId:
            base.talkAssistant.sendWhisperTalk(text, self.receiverId)
        else:
            base.talkAssistant.sendOpenTalk(text)

    def sendWhisperByFriend(self, avatarId, text):
        online = 0
        if avatarId in base.cr.doId2do:
            online = 1
        avatarUnderstandable = 0
        av = None
        if avatarId:
            av = base.cr.identifyAvatar(avatarId)
        if av != None:
            avatarUnderstandable = av.isUnderstandable()
        if avatarUnderstandable and online:
            base.talkAssistant.sendWhisperTalk(text, avatarId)
        return

    def chatButtonPressed(self):
        self.sendChat(self.chatEntry.get())

    def cancelButtonPressed(self):
        self.requestMode('Off')
        localAvatar.chatMgr.fsm.request('mainMenu')

    def enterAllChat(self):
        ChatInputWhiteListFrame.enterAllChat(self)
        self.whisperLabel.hide()

    def exitAllChat(self):
        ChatInputWhiteListFrame.exitAllChat(self)

    def enterAvatarWhisper(self):
        ChatInputWhiteListFrame.enterAvatarWhisper(self)
        self.labelWhisper()

    def exitAvatarWhisper(self):
        ChatInputWhiteListFrame.exitAvatarWhisper(self)
        self.whisperLabel.hide()

    def labelWhisper(self):
        if self.receiverId:
            self.whisperName = ChatUtil.findAvatarName(self.receiverId)
            self.whisperLabel['text'] = OTPLocalizer.ChatInputWhisperLabel % self.whisperName
            self.whisperLabel.show()
        else:
            self.whisperLabel.hide()
