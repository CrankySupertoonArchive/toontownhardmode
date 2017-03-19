from otp.ai.MagicWordGlobal import *
from toontown.safezone.CZSafeZoneLoader import CZSafeZoneLoader
from toontown.town.CZTownLoader import CZTownLoader
from toontown.toonbase import ToontownGlobals
from toontown.hood.ToonHood import ToonHood

class CZHood(ToonHood):
    notify = directNotify.newCategory('CZHood')

    ID = ToontownGlobals.ConstructionZone
    TOWNLOADER_CLASS = CZTownLoader
    SAFEZONELOADER_CLASS = CZSafeZoneLoader
    STORAGE_DNA = 'phase_14/dna/storage_CZ.pdna'
    SKY_FILE = 'phase_3.5/models/props/TT_sky'
    SPOOKY_SKY_FILE = 'phase_3.5/models/props/BR_sky'
    TITLE_COLOR = (1.0, 0.5, 0.4, 1.0)

    def load(self):
        ToonHood.load(self)

        self.fog = Fog('DDFog')
    
@magicWord(category=CATEGORY_CREATIVE)
def spooky():
    """
    Activates the 'spooky' effect on the current area.
    """
    hood = base.cr.playGame.hood
    if not hasattr(hood, 'startSpookySky'):
        return "Couldn't find spooky sky."
    if hasattr(hood, 'magicWordSpookyEffect'):
        return 'The spooky effect is already active!'
    hood.magicWordSpookyEffect = True
    hood.startSpookySky()
    fadeOut = base.cr.playGame.getPlace().loader.geom.colorScaleInterval(
        1.5, Vec4(0.55, 0.55, 0.65, 1), startColorScale=Vec4(1, 1, 1, 1),
        blendType='easeInOut')
    fadeOut.start()
    spookySfx = base.loadSfx('phase_4/audio/sfx/spooky.ogg')
    spookySfx.play()
    return 'Activating the spooky effect...'
