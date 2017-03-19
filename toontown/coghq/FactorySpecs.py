from toontown.toonbase import ToontownGlobals
import SellbotLegFactorySpec
import SellbotLegFactoryCogs
import LawbotLegFactorySpec
import LawbotLegFactoryCogs

def getFactorySpecModule(factoryId):
    return FactorySpecModules[factoryId]


def getCogSpecModule(factoryId):
    return CogSpecModules[factoryId]


FactorySpecModules = {ToontownGlobals.SellbotFactoryInt: SellbotLegFactorySpec,
 ToontownGlobals.LawbotOfficeInt: LawbotLegFactorySpec}
CogSpecModules = {ToontownGlobals.SellbotFactoryInt: SellbotLegFactoryCogs,
 ToontownGlobals.LawbotOfficeInt: LawbotLegFactoryCogs}

if config.GetBool('want-brutal-factory', True):
    import SellbotMegaCorpLegCogs
    import SellbotMegaCorpLegSpec
    FactorySpecModules[ToontownGlobals.SellbotMegaCorpInt] = SellbotMegaCorpLegSpec
    CogSpecModules[ToontownGlobals.SellbotMegaCorpInt] = SellbotMegaCorpLegCogs

if config.GetBool('want-hard-factory', True):
    import HardSellbotLegFactoryCogs
    import HardSellbotLegFactorySpec
    FactorySpecModules[ToontownGlobals.HardSellbotFactoryInt] = HardSellbotLegFactorySpec
    CogSpecModules[ToontownGlobals.HardSellbotFactoryInt] = HardSellbotLegFactoryCogs

if config.GetBool('want-unfair-factory', True):
    import UnfairSellbotLegFactoryCogs
    import UnfairSellbotLegFactorySpec
    FactorySpecModules[ToontownGlobals.UnfairSellbotFactoryInt] = UnfairSellbotLegFactorySpec
    CogSpecModules[ToontownGlobals.UnfairSellbotFactoryInt] = UnfairSellbotLegFactoryCogs
