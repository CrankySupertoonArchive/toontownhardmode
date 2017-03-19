from panda3d.core import *
from toontown.toon import ToonDNA
from direct.fsm import StateData
from direct.gui.DirectGui import *
from MakeAToonGlobals import *
from toontown.toonbase import TTLocalizer, ToontownGlobals
import ShuffleButton
import random, colorsys
from direct.directnotify import DirectNotifyGlobal
from direct.task import Task

class ColorShop(StateData.StateData):
    notify = DirectNotifyGlobal.directNotify.newCategory('ColorShop')

    def __init__(self, doneEvent):
        StateData.StateData.__init__(self, doneEvent)
        self.toon = None
        self.colorAll = 1

    def getColorList(self):
        return ToonDNA.matColorsList

    def enter(self, toon, shopsVisited = []):
        base.disableMouse()
        self.toon = toon
        self.dna = toon.getStyle()
        colorList = self.getColorList()
        self.allParts = (TTLocalizer.ColorAll, TTLocalizer.ColorShopHead, TTLocalizer.ColorShopBody, TTLocalizer.ColorShopLegs)
        if not hasattr(self, 'headChoice'):
            self.headChoice = colorList.index(self.dna.headColor)
            self.allChoice = self.headChoice
            self.armChoice = colorList.index(self.dna.armColor)
            self.legChoice = colorList.index(self.dna.legColor)
            self.partChoice = 0

        self.startColor = 0
        self.acceptOnce('last', self.__handleBackward)
        self.acceptOnce('next', self.__handleForward)
        choicePool = [self.getColorList(), self.getColorList(), self.getColorList(), self.getColorList()]
        self.shuffleButton.setChoicePool(choicePool)
        self.accept(self.shuffleFetchMsg, self.changeColor)
        self.acceptOnce('MAT-newToonCreated', self.shuffleButton.cleanHistory)

    def showButtons(self):
        self.parentFrame.show()

    def hideButtons(self):
        self.parentFrame.hide()
        self.advancedFrame.hide()

    def exit(self):
        self.ignore('last')
        self.ignore('next')
        self.ignore('enter')
        self.ignore(self.shuffleFetchMsg)
        try:
            del self.toon
        except:
            print 'ColorShop: toon not found'

        self.hideButtons()
        taskMgr.remove('colorDragTask')

    def load(self):
        self.gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui')
        guiRArrowUp = self.gui.find('**/tt_t_gui_mat_arrowUp')
        guiRArrowRollover = self.gui.find('**/tt_t_gui_mat_arrowUp')
        guiRArrowDown = self.gui.find('**/tt_t_gui_mat_arrowDown')
        guiRArrowDisabled = self.gui.find('**/tt_t_gui_mat_arrowDisabled')
        shuffleFrame = self.gui.find('**/tt_t_gui_mat_shuffleFrame')
        shuffleUp = self.gui.find('**/tt_t_gui_mat_shuffleUp')
        shuffleDown = self.gui.find('**/tt_t_gui_mat_shuffleDown')
        shuffleImage = (self.gui.find('**/tt_t_gui_mat_shuffleArrowUp'), self.gui.find('**/tt_t_gui_mat_shuffleArrowDown'), self.gui.find('**/tt_t_gui_mat_shuffleArrowUp'), self.gui.find('**/tt_t_gui_mat_shuffleArrowDisabled'))
        self.parentFrame = self.getNewFrame()
        self.advancedFrame = self.getNewFrame()
        self.toonFrame = DirectFrame(parent=self.parentFrame, image=shuffleFrame, image_scale=halfButtonInvertScale, relief=None, pos=(0, 0, -0.073), hpr=(0, 0, 0), scale=1.3, frameColor=(1, 1, 1, 1), text=TTLocalizer.ColorShopToon, text_scale=TTLocalizer.CStoonFrame, text_pos=(-0.001, -0.015), text_fg=(1, 1, 1, 1))
        self.allLButton = DirectButton(parent=self.toonFrame, relief=None, image=shuffleImage, image_scale=halfButtonScale, image1_scale=halfButtonHoverScale, image2_scale=halfButtonHoverScale, pos=(-0.2, 0, 0), command=self.__swapAllColor, extraArgs=[-1])
        self.allRButton = DirectButton(parent=self.toonFrame, relief=None, image=shuffleImage, image_scale=halfButtonInvertScale, image1_scale=halfButtonInvertHoverScale, image2_scale=halfButtonInvertHoverScale, pos=(0.2, 0, 0), command=self.__swapAllColor, extraArgs=[1])
        self.headFrame = DirectFrame(parent=self.parentFrame, image=shuffleFrame, image_scale=halfButtonInvertScale, relief=None, pos=(0, 0, -0.3), hpr=(0, 0, 2), scale=0.9, frameColor=(1, 1, 1, 1), text=TTLocalizer.ColorShopHead, text_scale=0.0625, text_pos=(-0.001, -0.015), text_fg=(1, 1, 1, 1))
        self.headLButton = DirectButton(parent=self.headFrame, relief=None, image=shuffleImage, image_scale=halfButtonScale, image1_scale=halfButtonHoverScale, image2_scale=halfButtonHoverScale, pos=(-0.2, 0, 0), command=self.__swapHeadColor, extraArgs=[-1])
        self.headRButton = DirectButton(parent=self.headFrame, relief=None, image=shuffleImage, image_scale=halfButtonInvertScale, image1_scale=halfButtonInvertHoverScale, image2_scale=halfButtonInvertHoverScale, pos=(0.2, 0, 0), command=self.__swapHeadColor, extraArgs=[1])
        self.bodyFrame = DirectFrame(parent=self.parentFrame, image=shuffleFrame, image_scale=halfButtonScale, relief=None, pos=(0, 0, -0.5), hpr=(0, 0, -2), scale=0.9, frameColor=(1, 1, 1, 1), text=TTLocalizer.ColorShopBody, text_scale=0.0625, text_pos=(-0.001, -0.015), text_fg=(1, 1, 1, 1))
        self.armLButton = DirectButton(parent=self.bodyFrame, relief=None, image=shuffleImage, image_scale=halfButtonScale, image1_scale=halfButtonHoverScale, image2_scale=halfButtonHoverScale, pos=(-0.2, 0, 0), command=self.__swapArmColor, extraArgs=[-1])
        self.armRButton = DirectButton(parent=self.bodyFrame, relief=None, image=shuffleImage, image_scale=halfButtonInvertScale, image1_scale=halfButtonInvertHoverScale, image2_scale=halfButtonInvertHoverScale, pos=(0.2, 0, 0), command=self.__swapArmColor, extraArgs=[1])
        self.legsFrame = DirectFrame(parent=self.parentFrame, image=shuffleFrame, image_scale=halfButtonInvertScale, relief=None, pos=(0, 0, -0.7), hpr=(0, 0, 3), scale=0.9, frameColor=(1, 1, 1, 1), text=TTLocalizer.ColorShopLegs, text_scale=0.0625, text_pos=(-0.001, -0.015), text_fg=(1, 1, 1, 1))
        self.legLButton = DirectButton(parent=self.legsFrame, relief=None, image=shuffleImage, image_scale=halfButtonScale, image1_scale=halfButtonHoverScale, image2_scale=halfButtonHoverScale, pos=(-0.2, 0, 0), command=self.__swapLegColor, extraArgs=[-1])
        self.legRButton = DirectButton(parent=self.legsFrame, relief=None, image=shuffleImage, image_scale=halfButtonInvertScale, image1_scale=halfButtonInvertHoverScale, image2_scale=halfButtonInvertHoverScale, pos=(0.2, 0, 0), command=self.__swapLegColor, extraArgs=[1])
        self.advancedButton = DirectButton(parent=self.parentFrame, relief=None, image=(shuffleUp, shuffleDown, shuffleUp), image_scale=(-0.8, 0.6, 0.6), image1_scale=(-0.83, 0.6, 0.6), image2_scale=(-0.83, 0.6, 0.6), text=TTLocalizer.ColorAdvanced, text_font=ToontownGlobals.getInterfaceFont(), text_scale=TTLocalizer.SBshuffleBtn, text_pos=(0, -0.02), text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1), pos=(0, 0, -1.15), command=self.popupAdvancedMenu)
        self.basicButton = DirectButton(parent=self.advancedFrame, relief=None, image=(shuffleUp, shuffleDown, shuffleUp), image_scale=(-0.8, 0.6, 0.6), image1_scale=(-0.83, 0.6, 0.6), image2_scale=(-0.83, 0.6, 0.6), text=TTLocalizer.ColorBasic, text_font=ToontownGlobals.getInterfaceFont(), text_scale=TTLocalizer.SBshuffleBtn, text_pos=(0, -0.02), text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1), pos=(0, 0, -1.15), command=self.popupBasicMenu)
        self.pickContainer = DirectFrame(parent=self.advancedFrame, relief=None, pos=(-0.4, 0, -0.5), image='phase_3/maps/color_picker_container.png', scale=(0.7, 0.5, 0.55))
        self.pickContainer.setTransparency(True)
        self.pickImage = PNMImage(int((ToontownGlobals.COLOR_SATURATION_MAX - ToontownGlobals.COLOR_SATURATION_MIN) * 100), int((ToontownGlobals.COLOR_VALUE_MAX - ToontownGlobals.COLOR_VALUE_MIN) * 100))
        self.hueSlider = DirectSlider(parent=self.advancedFrame, relief=None, image='phase_3/maps/color_picker_hue.jpg', scale=0.3, pos=(-0.05, 0, -0.43), image_scale=(0.1, 1.0, 1.0), pageSize=5, orientation=DGG.VERTICAL, command=self.__chooseHue)
        self.pickButton = DirectButton(parent=self.advancedFrame, relief=None, image='phase_3/maps/invisible.png', scale=0.3, pos=(-0.45, 0, -0.43), frameColor=(1, 1, 1, 0.1), pressEffect=0)
        self.pickButton.bind(DGG.B1PRESS, self.__startPickColor)
        self.pickButton.bind(DGG.B1RELEASE, self.__stopPickColor)
        self.partsFrame = DirectFrame(parent=self.advancedFrame, image=shuffleFrame, image_scale=halfButtonInvertScale, relief=None, pos=(-0.395, 0, -0.85), hpr=(0, 0, -2), scale=0.9, frameColor=(1, 1, 1, 1), text=TTLocalizer.ColorAll, text_scale=0.0625, text_pos=(-0.001, -0.015), text_fg=(1, 1, 1, 1))
        self.partLButton = DirectButton(parent=self.partsFrame, relief=None, image=shuffleImage, image_scale=halfButtonScale, image1_scale=halfButtonHoverScale, image2_scale=halfButtonHoverScale, pos=(-0.2, 0, 0), state=DGG.DISABLED, command=self.__swapPart, extraArgs=[-1])
        self.partRButton = DirectButton(parent=self.partsFrame, relief=None, image=shuffleImage, image_scale=halfButtonInvertScale, image1_scale=halfButtonInvertHoverScale, image2_scale=halfButtonInvertHoverScale, pos=(0.2, 0, 0), command=self.__swapPart, extraArgs=[1])
        self.parentFrame.hide()
        self.advancedFrame.hide()
        self.shuffleFetchMsg = 'ColorShopShuffle'
        self.shuffleButton = ShuffleButton.ShuffleButton(self, self.shuffleFetchMsg)

    def unload(self):
        self.gui.removeNode()
        del self.gui
        self.parentFrame.destroy()
        self.advancedFrame.destroy()
        self.toonFrame.destroy()
        self.headFrame.destroy()
        self.bodyFrame.destroy()
        self.legsFrame.destroy()
        self.headLButton.destroy()
        self.headRButton.destroy()
        self.armLButton.destroy()
        self.armRButton.destroy()
        self.legLButton.destroy()
        self.legRButton.destroy()
        self.allLButton.destroy()
        self.allRButton.destroy()
        self.advancedButton.destroy()
        self.basicButton.destroy()
        self.pickContainer.destroy()
        self.hueSlider.destroy()
        self.pickButton.destroy()
        self.partsFrame.destroy()
        self.partLButton.destroy()
        self.partRButton.destroy()
        del self.parentFrame
        del self.advancedFrame
        del self.toonFrame
        del self.headFrame
        del self.bodyFrame
        del self.legsFrame
        del self.headLButton
        del self.headRButton
        del self.armLButton
        del self.armRButton
        del self.legLButton
        del self.legRButton
        del self.allLButton
        del self.allRButton
        del self.advancedButton
        del self.basicButton
        del self.pickContainer
        del self.hueSlider
        del self.pickButton
        del self.partsFrame
        del self.partLButton
        del self.partRButton
        self.shuffleButton.unload()
        self.ignore('MAT-newToonCreated')
    
    def getNewFrame(self):
        frame = DirectFrame(relief=DGG.RAISED, pos=(0.98, 0, 0.416), frameColor=(1, 0, 0, 0))
        frame.setPos(-0.36, 0, -0.5)
        frame.reparentTo(base.a2dTopRight)
        return frame

    def popupAdvancedMenu(self):
        self.parentFrame.hide()
        self.advancedFrame.show()
    
    def popupBasicMenu(self):
        self.parentFrame.show()
        self.advancedFrame.hide()
    
    def calcRelative(self, value, baseMin, baseMax, limitMin, limitMax):
        return ((limitMax - limitMin) * (value - baseMin) / (baseMax - baseMin)) + limitMin
    
    def __chooseHue(self):
        for x in xrange(self.pickImage.getXSize()):
            for y in xrange(self.pickImage.getYSize()):
                self.pickImage.setXel(x, y, colorsys.hsv_to_rgb(self.hueSlider['value'], (x / 100.0) + ToontownGlobals.COLOR_SATURATION_MIN, (y / 100.0) + ToontownGlobals.COLOR_VALUE_MIN))
        
        texture = Texture()
        texture.load(self.pickImage)
        self.pickButton['image'] = texture
    
    def __pickColor(self, task=None):
        x = base.mouseWatcherNode.getMouseX()
        y = base.mouseWatcherNode.getMouseY()
        win_w, win_h = base.win.getSize()

        if win_w < win_h:
            y *= 1. * win_h / win_w
        else:
            x *= 1. * win_w / win_h

        x -= self.pickButton.getX(aspect2d)
        y -= self.pickButton.getZ(aspect2d)
        image_scale = self.pickButton['image_scale']
        x = (.5 + x / (2. * self.pickButton.getSx(aspect2d) * image_scale[0]))
        y = (.5 + y / -(2. * self.pickButton.getSz(aspect2d) * image_scale[2]))

        if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
            return Task.cont

        x = self.calcRelative(x, 0.0, 1.0, ToontownGlobals.COLOR_SATURATION_MIN, ToontownGlobals.COLOR_SATURATION_MAX)
        y = self.calcRelative(y, 0.0, 1.0, ToontownGlobals.COLOR_VALUE_MIN, ToontownGlobals.COLOR_VALUE_MAX)
        rgb = colorsys.hsv_to_rgb(self.hueSlider['value'], x, y) + (1,)
        rgb = tuple([float('%.2f' % x) for x in rgb])

        if self.partChoice in (0, 1):
            self.dna.headColor = rgb
        if self.partChoice in (0, 2):
            self.dna.armColor = rgb
        if self.partChoice in (0, 3):
            self.dna.legColor = rgb

        self.toon.swapToonColor(self.dna)
        return Task.cont
    
    def __startPickColor(self, extra):
        self.__stopPickColor(extra)
        taskMgr.add(self.__pickColor, 'colorDragTask')
    
    def __stopPickColor(self, extra):
        taskMgr.remove('colorDragTask')

    def __swapPart(self, offset):
        self.partChoice += offset
        self.partLButton['state'] = DGG.DISABLED if self.partChoice <= 0 else DGG.NORMAL
        self.partRButton['state'] = DGG.DISABLED if self.partChoice >= len(self.allParts) - 1 else DGG.NORMAL
        self.partsFrame['text'] = self.allParts[self.partChoice]
    
    def __swapAllColor(self, offset):
        colorList = self.getColorList()
        length = len(colorList)
        self.allChoice = (self.allChoice + offset) % length
        self.__updateScrollButtons(self.allChoice, length, self.allLButton, self.allRButton)
        self.__updateScrollButtons(self.allChoice, length, self.headLButton, self.headRButton)
        self.__updateScrollButtons(self.allChoice, length, self.armLButton, self.armRButton)
        self.__updateScrollButtons(self.allChoice, length, self.legLButton, self.legRButton)
        newColor = colorList[self.allChoice]
        self.dna.headColor = newColor
        self.dna.armColor = newColor
        self.dna.legColor = newColor
        self.toon.swapToonColor(self.dna)

    def __swapHeadColor(self, offset):
        colorList = self.getColorList()
        length = len(colorList)
        self.headChoice = (self.headChoice + offset) % length
        self.__updateScrollButtons(self.headChoice, length, self.headLButton, self.headRButton)
        newColor = colorList[self.headChoice]
        self.dna.headColor = newColor
        self.toon.swapToonColor(self.dna)

    def __swapArmColor(self, offset):
        colorList = self.getColorList()
        length = len(colorList)
        self.armChoice = (self.armChoice + offset) % length
        self.__updateScrollButtons(self.armChoice, length, self.armLButton, self.armRButton)
        newColor = colorList[self.armChoice]
        self.dna.armColor = newColor
        self.toon.swapToonColor(self.dna)

    def __swapLegColor(self, offset):
        colorList = self.getColorList()
        length = len(colorList)
        self.legChoice = (self.legChoice + offset) % length
        self.__updateScrollButtons(self.legChoice, length, self.legLButton, self.legRButton)
        newColor = colorList[self.legChoice]
        self.dna.legColor = newColor
        self.toon.swapToonColor(self.dna)

    def __updateScrollButtons(self, choice, length, lButton, rButton):
        if choice == (self.startColor - 1) % length:
            rButton['state'] = DGG.DISABLED
        else:
            rButton['state'] = DGG.NORMAL
        if choice == self.startColor % length:
            lButton['state'] = DGG.DISABLED
        else:
            lButton['state'] = DGG.NORMAL

    def __handleForward(self):
        self.doneStatus = 'next'
        messenger.send(self.doneEvent)

    def __handleBackward(self):
        self.doneStatus = 'last'
        messenger.send(self.doneEvent)

    def changeColor(self):
        self.notify.debug('Entering changeColor')
        colorList = self.getColorList()
        newChoice = self.shuffleButton.getCurrChoice()
        newHeadColorIndex = self.indexOf(colorList, newChoice[0], 25)
        newArmColorIndex = self.indexOf(colorList, newChoice[1], 25)
        newLegColorIndex = self.indexOf(colorList, newChoice[2], 25)
        self.__swapHeadColor(newHeadColorIndex - self.headChoice)
        if self.colorAll:
            self.__swapArmColor(newHeadColorIndex - self.armChoice)
            self.__swapLegColor(newHeadColorIndex - self.legChoice)
        else:
            self.__swapArmColor(newArmColorIndex - self.armChoice)
            self.__swapLegColor(newLegColorIndex - self.legChoice)
    
    def indexOf(self, list, item, default):
        try:
            return list.index(item)
        except:
            return default

    def getCurrToonSetting(self):
        return [self.dna.headColor, self.dna.armColor, self.dna.legColor]
