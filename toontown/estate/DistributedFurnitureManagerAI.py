from direct.distributed.DistributedObjectAI import DistributedObjectAI
from toontown.catalog.CatalogItemList import CatalogItemList
from toontown.catalog import CatalogItem
from toontown.catalog.CatalogFurnitureItem import CatalogFurnitureItem, FLTrunk, FLCloset, FLBank, FLPhone, FLCrate, FLChair, FLTV
from toontown.catalog.CatalogWallpaperItem import CatalogWallpaperItem
from toontown.catalog.CatalogMouldingItem import CatalogMouldingItem
from toontown.catalog.CatalogFlooringItem import CatalogFlooringItem
from toontown.catalog.CatalogWainscotingItem import CatalogWainscotingItem
from toontown.toonbase import ToontownGlobals
from DistributedFurnitureItemAI import DistributedFurnitureItemAI
from DistributedPhoneAI import DistributedPhoneAI
from DistributedClosetAI import DistributedClosetAI
from DistributedTrunkAI import DistributedTrunkAI
from DistributedBankAI import DistributedBankAI
from DistributedRewardCrateAI import DistributedRewardCrateAI
from DistributedChairAI import DistributedChairAI
from DistributedTVAI import DistributedTVAI
from otp.ai.MagicWordGlobal import *

class FurnitureError(Exception):
    def __init__(self, code):
        Exception.__init__(self)
        self.code = code


class DistributedFurnitureManagerAI(DistributedObjectAI):
    notify = directNotify.newCategory("DistributedFurnitureManagerAI")

    def __init__(self, air, house, interior):
        DistributedObjectAI.__init__(self, air)

        self.house = house
        self.interior = interior

        self.director = None

        self.ownerId = house.avatarId
        self.ownerName = house.name

        self.atticItems = None
        self.atticWallpaper = None
        self.wallpaper = None
        self.atticWindows = None
        self.windows = None
        self.deletedItems = None

        self.items = []

        # Initialize the above variables:
        self.loadFromHouse()

    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)

        for item in self.items:
            item.generateWithRequired(self.zoneId)

    def delete(self):
        for item in self.items:
            item.destroy()

        DistributedObjectAI.delete(self)

    def loadFromHouse(self):
        self.b_setAtticItems(self.house.getAtticItems())
        self.b_setAtticWallpaper(self.house.getAtticWallpaper())
        self.b_setAtticWindows(self.house.getAtticWindows())
        self.b_setDeletedItems(self.house.getDeletedItems())

        self.wallpaper = CatalogItemList(self.house.getInteriorWallpaper(),
                                         store=CatalogItem.Customization)
        self.applyWallpaper()
        self.windows = CatalogItemList(self.house.getInteriorWindows(),
                                       store=CatalogItem.Customization |
                                             CatalogItem.WindowPlacement)
        self.applyWindows()

        self.setItems(self.house.getInteriorItems())

    def saveToHouse(self):
        self.house.b_setAtticItems(self.getAtticItems())
        self.house.b_setAtticWallpaper(self.getAtticWallpaper())
        self.house.b_setAtticWindows(self.getAtticWindows())
        self.house.b_setDeletedItems(self.getDeletedItems())

        self.house.b_setInteriorWallpaper(self.wallpaper.getBlob())
        self.house.b_setInteriorWindows(self.windows.getBlob())

        self.house.b_setInteriorItems(self.getItems())

    def applyWallpaper(self):
        self.interior.b_setWallpaper(self.wallpaper.getBlob())

    def applyWindows(self):
        self.interior.b_setWindows(self.windows.getBlob())

    def setItems(self, items):
        items = CatalogItemList(items, store=CatalogItem.Customization|CatalogItem.Location)

        for item in self.items:
            item.destroy()

        self.items = []

        for item in items:
            self.generateItem(item)

    def getItems(self):
        items = CatalogItemList(store=CatalogItem.Customization|CatalogItem.Location)

        for item in self.items:
            items.append(item.catalogItem)

        return items.getBlob()

    def setOwnerId(self, ownerId):
        self.ownerId = ownerId

    def d_setOwnerId(self, ownerId):
        self.sendUpdate('setOwnerId', [ownerId])

    def b_setOwnerId(self, ownerId):
        self.setOwnerId(ownerId)
        self.d_setOwnerId(ownerId)

    def getOwnerId(self):
        return self.ownerId

    def setOwnerName(self, ownerName):
        self.ownerName = ownerName

    def d_setOwnerName(self, ownerName):
        self.sendUpdate('setOwnerName', [ownerName])

    def b_setOwnerName(self, ownerName):
        self.setOwnerName(ownerName)
        self.d_setOwnerName(ownerName)

    def getOwnerName(self):
        return self.ownerName

    def getInteriorId(self):
        return self.interior.doId

    def setAtticItems(self, items):
        self.atticItems = CatalogItemList(items, store=CatalogItem.Customization)

    def d_setAtticItems(self, items):
        self.sendUpdate('setAtticItems', [items])

    def b_setAtticItems(self, items):
        self.setAtticItems(items)
        if self.isGenerated():
            self.d_setAtticItems(items)

    def getAtticItems(self):
        return self.atticItems.getBlob()

    def setAtticWallpaper(self, items):
        self.atticWallpaper = CatalogItemList(items, store=CatalogItem.Customization)

    def d_setAtticWallpaper(self, items):
        self.sendUpdate('setAtticWallpaper', [items])

    def b_setAtticWallpaper(self, items):
        self.setAtticWallpaper(items)
        if self.isGenerated():
            self.d_setAtticWallpaper(items)

    def getAtticWallpaper(self):
        return self.atticWallpaper.getBlob()

    def setAtticWindows(self, items):
        self.atticWindows = CatalogItemList(items, store=CatalogItem.Customization)

    def d_setAtticWindows(self, items):
        self.sendUpdate('setAtticWindows', [items])

    def b_setAtticWindows(self, items):
        self.setAtticWindows(items)
        if self.isGenerated():
            self.d_setAtticWindows(items)

    def getAtticWindows(self):
        return self.atticWindows.getBlob()

    def setDeletedItems(self, items):
        self.deletedItems = CatalogItemList(items, store=CatalogItem.Customization)

    def d_setDeletedItems(self, items):
        self.sendUpdate('setDeletedItems', [items])

    def b_setDeletedItems(self, items):
        self.setDeletedItems(items)
        if self.isGenerated():
            self.d_setDeletedItems(items)

    def getDeletedItems(self):
        return self.deletedItems.getBlob()

    def suggestDirector(self, directorId):
        senderId = self.air.getAvatarIdFromSender()

        if self.ownerId != senderId:
            self.air.writeServerEvent('suspicious', avId=senderId, issue='Tried to move furniture, but not the house owner!')
            return

        if senderId != directorId and directorId != 0:
            self.air.writeServerEvent('suspicious', avId=senderId, issue='Tried to make someone else (%d) move their furniture!' % directorId)
            return

        director = self.air.doId2do.get(directorId)
        if directorId and not director:
            self.air.writeServerEvent('suspicious', avId=directorId, issue='Tried to move furniture without being on the shard!')
            return

        if self.director:
            self.director.b_setGhostMode(0)
        if director:
            if director.zoneId != self.zoneId:
                self.air.writeServerEvent('suspicious', avId=directorId, issue='Tried to become director from another zone!')
                return
            director.b_setGhostMode(1)

        self.director = director
        self.sendUpdate('setDirector', [directorId])

        # Let's also save the furniture to the house (and thus to the DB) while
        # we're at it...
        self.saveToHouse()

    def avatarEnter(self):
        pass

    def avatarExit(self):
        pass

    # Furniture-manipulation:

    def generateItem(self, item):
        if item.getFlags() & FLTrunk:
            do = DistributedTrunkAI(self.air, self, item)
        elif item.getFlags() & FLCloset:
            do = DistributedClosetAI(self.air, self, item)
        elif item.getFlags() & FLBank:
            do = DistributedBankAI(self.air, self, item)
        elif item.getFlags() & FLPhone:
            do = DistributedPhoneAI(self.air, self, item)
        elif item.getFlags() & FLCrate:
            do = DistributedRewardCrateAI(self.air, self, item)
        elif item.getFlags() & FLChair:
            do = DistributedChairAI(self.air, self, item)
        elif item.getFlags() & FLTV:
            do = DistributedTVAI(self.air, self, item)
        else:
            do = DistributedFurnitureItemAI(self.air, self, item)
        
        if self.isGenerated():
            do.generateWithRequired(self.zoneId)

        self.items.append(do)
        return do

    def moveItemToAttic(self, doId):
        item = self.getItemObject(doId)

        self.atticItems.append(item.catalogItem)
        self.d_setAtticItems(self.getAtticItems())

        item.destroy()
        self.items.remove(item)

        return ToontownGlobals.FM_MovedItem

    def moveItemFromAttic(self, index, x, y, z, h, p, r):
        item = self.getAtticFurniture(self.atticItems, index)

        self.atticItems.remove(item)
        self.d_setAtticItems(self.getAtticItems())

        item.posHpr = (x, y, z, h, p, r)
        object = self.generateItem(item)

        return (ToontownGlobals.FM_MovedItem, object.doId)

    def deleteItemFromAttic(self, blob, index):
        item = self.getAtticFurniture(self.atticItems, index)
        if item is None:
            self.air.writeServerEvent('suspicious', avId=self.air.getAvatarIdFromSender(), issue='Tried to delete an invalid item at index %s' % index)
            return ToontownGlobals.FM_InvalidIndex

        self.atticItems.remove(item)
        self.d_setAtticItems(self.getAtticItems())

        return ToontownGlobals.FM_DeletedItem

    def deleteItemFromRoom(self, doId, addToTrash=True):
        item = self.getItemObject(doId)

        if not item:
            self.air.writeServerEvent('suspicious', avId=self.air.getAvatarIdFromSender(), issue='Tried to delete an invalid item with doId %s' % doId)
            return ToontownGlobals.FM_InvalidIndex

        if addToTrash:
            self.deletedItems.append(item.catalogItem)
            self.d_setDeletedItems(self.getDeletedItems())

        item.destroy()
        self.items.remove(item)
        
        return ToontownGlobals.FM_DeletedItem

    def moveWallpaperFromAttic(self, index, room):
        retcode = ToontownGlobals.FM_SwappedItem
        wallpaper = self.getAtticFurniture(self.atticWallpaper, index)
        if wallpaper is None:
            self.air.writeServerEvent('suspicious', avId=self.air.getAvatarIdFromSender(), issue='Invalid wallpaper at index %s' % index)
            return ToontownGlobals.FM_InvalidIndex

        if room > 3:
            self.air.writeServerEvent('suspicious', avId=self.air.getAvatarIdFromSender(), issue='Tried to apply a wallpaper in an invalid room %d!' % room)
            return ToontownGlobals.FM_InvalidItem
        interiorIndex = room*4
        if isinstance(wallpaper, CatalogMouldingItem):
            interiorIndex += 1
        elif isinstance(wallpaper, CatalogFlooringItem):
            interiorIndex += 2
        elif isinstance(wallpaper, CatalogWainscotingItem):
            interiorIndex += 3
        atticIndex = self.atticWallpaper.index(wallpaper)
        self.atticWallpaper[atticIndex] = self.wallpaper[interiorIndex]
        self.d_setAtticWallpaper(self.getAtticWallpaper())
        self.wallpaper[interiorIndex] = wallpaper
        self.applyWallpaper()

        return retcode

    def deleteWallpaperFromAttic(self, blob, index):
        wallpaper = self.getAtticFurniture(blob, index)
        if wallpaper in self.atticWallpaper:
            self.atticWallpaper.remove(wallpaper)
        self.b_setAtticWallpaper(self.getAtticWallpaper())

    def moveWindowToAttic(self, slot):
        window = self.getWindow(slot)
        if window is None:
            return ToontownGlobals.FM_InvalidIndex
        self.windows.remove(window)
        self.applyWindows()
        self.atticWindows.append(window)
        self.d_setAtticWindows(self.getAtticWindows())
        return ToontownGlobals.FM_MovedItem

    def moveWindowFromAttic(self, index, slot):
        retcode = ToontownGlobals.FM_MovedItem
        window = self.getAtticFurniture(self.atticWindows, index)
        if slot > 7:
            self.air.writeServerEvent('suspicious', avId=self.air.getAvatarIdFromSender(),
                                      issue='Tried to move window to invalid slot %d!' % slot)
            return ToontownGlobals.FM_HouseFull
        if self.getWindow(slot):
            self.moveWindowToAttic(slot)
            retcode = ToontownGlobals.FM_SwappedItem
        self.atticWindows.remove(window)
        self.d_setAtticWindows(self.getAtticWindows())
        window.placement = slot
        self.windows.append(window)
        self.applyWindows()
        return retcode

    def moveWindow(self, fromSlot, toSlot):
        retcode = ToontownGlobals.FM_MovedItem
        window = self.getWindow(fromSlot)
        if window is None:
            return ToontownGlobals.FM_InvalidIndex
        if toSlot > 7:
            self.air.writeServerEvent('suspicious', avId=self.air.getAvatarIdFromSender(),
                                      issue='DistributedfTried to move window to invalid slot %d!' % toSlot)
            return ToontownGlobals.FM_HouseFull
        if self.getWindow(toSlot):
            self.moveWindowToAttic(toSlot)
            retcode = ToontownGlobals.FM_SwappedItem
        window.placement = toSlot
        self.applyWindows()
        return retcode

    def deleteWindowFromAttic(self, blob, index):
        window = self.getAtticFurniture(self.atticWindows, index)
        if window is None:
            self.air.writeServerEvent('suspicious', avId=self.air.getAvatarIdFromSender(), issue='Tried to delete an invalid window at index %s' % index)
            return ToontownGlobals.FM_InvalidIndex
        self.atticWindows.remove(window)
        self.d_setAtticWindows(self.getAtticWindows())
        return ToontownGlobals.FM_DeletedItem

    def recoverDeletedItem(self, blob, index):
        if len(self.deletedItems) <= index:
            return
        
        item = self.deletedItems[index]
        self.deletedItems.remove(item)
        self.atticItems.append(item)
        self.d_setDeletedItems(self.deletedItems)
        self.d_setAtticItems(self.getAtticItems())
        
        return ToontownGlobals.FM_MovedItem

    def handleMessage(self, func, response, *args):
        context = args[-1]
        args = args[:-1]
        senderId = self.air.getAvatarIdFromSender()
        if not self.director or senderId != self.director.doId:
            self.air.writeServerEvent('suspicious', avId=senderId,
                                      issue='Sent furniture management request without'
                                      ' being the director.')
            retval = ToontownGlobals.FM_NotDirector
        else:
            try:
                retval = func(*args) or 0
            except FurnitureError as e:
                retval = e.code
        if response == 'moveItemFromAtticResponse':
            if type(retval) == tuple:
                retval, doId = retval
            else:
                doId = 0
            taskMgr.doMethodLater(1, self.sendUpdateToAvatarId,
                                  self.uniqueName('send-attic-response'),
                                  extraArgs=[senderId, response, [retval, doId, context]])
        else:
            self.sendUpdateToAvatarId(senderId, response, [retval, context])

    def moveItemToAtticMessage(self, doId, context):
        self.handleMessage(self.moveItemToAttic, 'moveItemToAtticResponse', doId, context)

    def moveItemFromAtticMessage(self, index, x, y, z, h, p, r, context):
        self.handleMessage(self.moveItemFromAttic, 'moveItemFromAtticResponse', index, x, y, z, h, p, r, context)

    def deleteItemFromAtticMessage(self, blob, index, context):
        self.handleMessage(self.deleteItemFromAttic, 'deleteItemFromAtticResponse', blob, index, context)

    def deleteItemFromRoomMessage(self, blob, doId, context):
        self.handleMessage(self.deleteItemFromRoom, 'deleteItemFromRoomResponse', doId, context)

    def moveWallpaperFromAtticMessage(self, index, room, context):
        self.handleMessage(self.moveWallpaperFromAttic, 'moveWallpaperFromAtticResponse', index, room, context)

    def deleteWallpaperFromAtticMessage(self, blob, index, context):
        self.handleMessage(self.deleteWallpaperFromAttic, 'deleteWallpaperFromAtticResponse', blob, index, context)

    def moveWindowToAtticMessage(self, slot, context):
        self.handleMessage(self.moveWindowToAttic, 'moveWindowToAtticResponse', slot, context)

    def moveWindowFromAtticMessage(self, index, slot, context):
        self.handleMessage(self.moveWindowFromAttic, 'moveWindowFromAtticResponse', index, slot, context)

    def moveWindowMessage(self, fromSlot, toSlot, context):
        self.handleMessage(self.moveWindow, 'moveWindowResponse', fromSlot, toSlot, context)

    def deleteWindowFromAtticMessage(self, blob, index, context):
        self.handleMessage(self.deleteWindowFromAttic, 'deleteWindowFromAtticResponse', blob, index, context)

    def recoverDeletedItemMessage(self, blob, index, context):
        self.handleMessage(self.recoverDeletedItem, 'recoverDeletedItemResponse', blob, index, context)

    def getItemObject(self, doId):
        item = self.air.doId2do.get(doId)
        if item is None:
            raise FurnitureError(ToontownGlobals.FM_InvalidItem)
        if item not in self.items:
            raise FurnitureError(ToontownGlobals.FM_InvalidItem)
        return item

    def getAtticFurniture(self, attic, index):
        if index >= len(attic):
            raise FurnitureError(ToontownGlobals.FM_InvalidIndex)
        return attic[index]

    def getWindow(self, slot):
        for window in self.windows:
            if window.placement == slot:
                return window
        return None

@magicWord(category=CATEGORY_PROGRAMMER)
def fillAttic():
    """
    Move everything to the attic.
    """
    target = spellbook.getTarget()

    if not hasattr(target, "estate") or not hasattr(target.estate, "houses"):
        return "The target is not in an estate!"

    for house in target.estate.houses:
        if house.doId == target.houseId:
            manager = house.interior.furnitureManager

            for item in reversed(manager.items):
                manager.moveItemToAttic(item.doId)

            manager.saveToHouse()
            return "Everything has been moved to the attic!"
    
    return "The target is not in his estate!"

@magicWord(category=CATEGORY_PROGRAMMER)
def emptyHouse():
    """
    Delete everything in the house.
    """
    target = spellbook.getTarget()

    if not hasattr(target, "estate") or not hasattr(target.estate, "houses"):
        return "The target is not in an estate!"

    for house in target.estate.houses:
        if house.doId == target.houseId:
            manager = house.interior.furnitureManager

            for item in reversed(manager.items):
                item.destroy()

            manager.items = []
            manager.saveToHouse()
            return "Everything has been deleted!"
    
    return "The target is not in his estate!"