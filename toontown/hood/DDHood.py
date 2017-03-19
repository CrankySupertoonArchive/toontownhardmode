from pandac.PandaModules import Vec4
from toontown.safezone.DDSafeZoneLoader import DDSafeZoneLoader
from toontown.town.DDTownLoader import DDTownLoader
from toontown.toonbase import ToontownGlobals
from toontown.hood.ToonHood import ToonHood

class DDHood(ToonHood):
    notify = directNotify.newCategory('DDHood')

    ID = ToontownGlobals.DonaldsDock
    TOWNLOADER_CLASS = DDTownLoader
    SAFEZONELOADER_CLASS = DDSafeZoneLoader
    STORAGE_DNA = 'phase_6/dna/storage_DD.pdna'
    SKY_FILE = 'phase_3.5/models/props/BR_sky'
    SPOOKY_SKY_FILE = 'phase_3.5/models/props/BR_sky'
    TITLE_COLOR = (0.8, 0.6, 0.5, 1.0)

    HOLIDAY_DNA = {
      ToontownGlobals.CHRISTMAS: ['phase_6/dna/winter_storage_DD.pdna'],
      ToontownGlobals.HALLOWEEN: ['phase_6/dna/halloween_props_storage_DD.pdna']}

    def load(self):
        ToonHood.load(self)

        self.fog = Fog('DDFog')
