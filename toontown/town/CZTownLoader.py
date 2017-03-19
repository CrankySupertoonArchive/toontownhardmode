from toontown.suit import Suit
from toontown.town import TTStreet
from toontown.town import TownLoader


class CZTownLoader(TownLoader.TownLoader):
    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = TTStreet.TTStreet
        self.musicFile = 'phase_14/audio/bgm/CZ_SZ.ogg'
        self.activityMusicFile = 'phase_14/audio/bgm/CZ_SZ_activity.ogg'
        self.townStorageDNAFile = 'phase_14/dna/storage_CZ_town.pdna'

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        Suit.loadSuits(1)
        dnaFile = 'phase_14/dna/construction_zone_' + str(self.canonicalBranchZone) + '.pdna'
        self.createHood(dnaFile)

    def unload(self):
        TownLoader.TownLoader.unload(self)
        Suit.unloadSuits(1)
