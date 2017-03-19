import random
from panda3d.core import *
from direct.directnotify.DirectNotifyGlobal import *
from toontown.toonbase import TTLocalizer, ToontownGlobals
import random
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
notify = directNotify.newCategory('SuitDNA')
suitHeadTypes = ['f',
 'p',
 'ym',
 'mm',
 'ds',
 'hh',
 'cr',
 'tbc',
 'bf',
 'b',
 'dt',
 'ac',
 'bs',
 'sd',
 'le',
 'bw',
 'sc',
 'pp',
 'tw',
 'bc',
 'nc',
 'mb',
 'ls',
 'rb',
 'cc',
 'tm',
 'nd',
 'gh',
 'ms',
 'tf',
 'm',
 'mh',
 'v1',
 'v2',
 'v3',
 'v4',
 'v5',
 'rr',
 'v7',
 'v8',
 'ttb',
 'lr',
 'e3',
 'e4',
 'e5',
 'tbh',
 'e7',
 'fns',
 'b1',
 'b2',
 'b3',
 'b4',
 'b5',
 'b6',
 'b7',
 'b8',
 'ant',
 'z2',
 'z3',
 'z4',
 'z5',
 'z6',
 'z7',
 'z8']
newSuitHeadTypes = ['v1',
 'v2',
 'v3',
 'v4',
 'v5',
 'rr',
 'v7',
 'v8',
 'ttb',
 'lr',
 'e3',
 'e4',
 'e5',
 'tbh',
 'e7',
 'fns',
 'b1',
 'b2',
 'b3',
 'b4',
 'b5',
 'b6',
 'b7',
 'b8',
 'ant',
 'z2',
 'z3',
 'z4',
 'z5',
 'z6',
 'z7',
 'z8']
suitATypes = ['ym',
 'hh',
 'tbc',
 'dt',
 'bs',
 'le',
 'bw',
 'pp',
 'nc',
 'rb',
 'nd',
 'tf',
 'm',
 'mh',
 'v1',
 'v2',
 'v3',
 'v4',
 'v5',
 'v7',
 'v8',
 'e3',
 'e4',
 'e5',
 'e7',
 'b1',
 'b2',
 'b3',
 'b4',
 'b5',
 'b6',
 'b7',
 'b8',
 'z2',
 'z3',
 'z4',
 'z5',
 'z6',
 'z7',
 'z8']
suitBTypes = ['p',
 'ds',
 'b',
 'ac',
 'sd',
 'bc',
 'ls',
 'tm',
 'ms',
 'rr',
 'lr',
 'tbh',
 'fns']
suitCTypes = ['f',
 'mm',
 'cr',
 'bf',
 'sc',
 'tw',
 'mb',
 'cc',
 'gh',
 'ttb',
 'ant']
suitDepts = ['c',
 'l',
 'm',
 's',
 'v',
 'e',
 'b',
 'z']
newSuitDepts = {'v',
                'e',
                'b',
                'z'}
suitDeptZones = [ToontownGlobals.BossbotHQ,
 ToontownGlobals.LawbotHQ,
 ToontownGlobals.CashbotHQ,
 ToontownGlobals.SellbotHQ,
 ToontownGlobals.GovernbotHQ,
 ToontownGlobals.EurekabotHQ,
 ToontownGlobals.BuildbotHQ,
 ToontownGlobals.ViralbotHQ]
suitDeptFullnames = {'c': TTLocalizer.Bossbot,
 'l': TTLocalizer.Lawbot,
 'm': TTLocalizer.Cashbot,
 's': TTLocalizer.Sellbot,
 'v': TTLocalizer.Governbot,
 'e': TTLocalizer.Eurekabot,
 'b': TTLocalizer.Buildbot,
 'z': TTLocalizer.Viralbot}
suitDeptFullnamesP = {'c': TTLocalizer.BossbotP,
 'l': TTLocalizer.LawbotP,
 'm': TTLocalizer.CashbotP,
 's': TTLocalizer.SellbotP,
 'v': TTLocalizer.GovernbotP,
 'e': TTLocalizer.EurekabotP,
 'b': TTLocalizer.BuildbotP,
 'z': TTLocalizer.ViralbotP}
suitDeptFilenames = {'c': 'boss',
 'l': 'law',
 'm': 'cash',
 's': 'sell',
 'v': 'govern',
 'e': 'eureka',
 'b': 'build',
 'z': 'viral'}
suitDeptModelPaths = {'c': '**/CorpIcon',
 0: '**/CorpIcon',
 'l': '**/LegalIcon',
 1: '**/LegalIcon',
 'm': '**/MoneyIcon',
 2: '**/MoneyIcon',
 's': '**/SalesIcon',
 3: '**/SalesIcon',
 'v': '**/GovernIcon',
 4: '**/GovernIcon',
 'e': '**/EurekaIcon',
 5: '**/EurekaIcon',
 'b': '**/BuildIcon',
 6: '**/BuildIcon',
 'z': '**/ViralIcon',
 7: '**/ViralIcon'}
corpPolyColor = VBase4(0.95, 0.75, 0.75, 1.0)
legalPolyColor = VBase4(0.75, 0.75, 0.95, 1.0)
moneyPolyColor = VBase4(0.65, 0.95, 0.85, 1.0)
salesPolyColor = VBase4(0.95, 0.75, 0.95, 1.0)
governPolyColor = VBase4(0.3, 0.3, 0.3, 1.0)
eurekaPolyColor = VBase4(1.0, 0.85, 0.95, 1.0)
buildPolyColor = VBase4(0.427, 0.85, 0.95, 1.0)
viralPolyColor = VBase4(0.182, 0.85, 0.139, 1.0)
suitsPerLevel = [1,
 1,
 1,
 1,
 1,
 1,
 1,
 1]
suitsPerDept = 8
levelsPerSuit = 8
goonTypes = ['pg', 'sg']

def getSuitBodyType(name):
    if name in suitATypes:
        return 'a'
    elif name in suitBTypes:
        return 'b'
    elif name in suitCTypes:
        return 'c'
    else:
        print 'Unknown body type for suit name: ', name


def getSuitDept(name):
    index = suitHeadTypes.index(name)
    if index < suitsPerDept:
        return suitDepts[0]
    elif index < suitsPerDept * 2:
        return suitDepts[1]
    elif index < suitsPerDept * 3:
        return suitDepts[2]
    elif index < suitsPerDept * 4:
        return suitDepts[3]
    elif index < suitsPerDept * 5:
        return suitDepts[4]
    elif index < suitsPerDept * 6:
        return suitDepts[5]
    elif index < suitsPerDept * 7:
        return suitDepts[6]
    elif index < suitsPerDept * 8:
        return suitDepts[7]
    else:
        print 'Unknown dept for suit name: ', name
        return None
    return None


def getDeptFullname(dept):
    return suitDeptFullnames[dept]


def getDeptFullnameP(dept):
    return suitDeptFullnamesP[dept]


def getSuitDeptFullname(name):
    return suitDeptFullnames[getSuitDept(name)]


def getSuitType(name):
    index = suitHeadTypes.index(name)
    return index % suitsPerDept + 1


def getSuitName(deptIndex, typeIndex):
    return suitHeadTypes[(suitsPerDept*deptIndex) + typeIndex]


def getRandomSuitType(level, rng = random):
    return random.randint(max(level - 7, 1), min(level, 8))


def getRandomSuitByDept(dept):
    deptNumber = suitDepts.index(dept)
    return suitHeadTypes[suitsPerDept * deptNumber + random.randint(0, 7)]

def getSuitsInDept(dept):
    start = dept * suitsPerDept
    end = start + suitsPerDept
    return suitHeadTypes[start:end]

class SuitDNA:

    def __init__(self, str = None, type = None, dna = None, r = None, b = None, g = None):
        if str != None:
            self.makeFromNetString(str)
        elif type != None:
            if type == 's':
                self.newSuit()
        else:
            self.type = 'u'
        return

    def __str__(self):
        if self.type == 's':
            return 'type = %s\nbody = %s, dept = %s, name = %s' % ('suit',
             self.body,
             self.dept,
             self.name)
        elif self.type == 'b':
            return 'type = boss cog\ndept = %s' % self.dept
        else:
            return 'type undefined'

    def makeNetString(self):
        dg = PyDatagram()
        dg.addFixedString(self.type, 1)
        if self.type == 's':
            dg.addFixedString(self.name, 3)
            dg.addFixedString(self.dept, 1)
        elif self.type == 'b':
            dg.addFixedString(self.dept, 1)
        elif self.type == 'u':
            notify.error('undefined avatar')
        else:
            notify.error('unknown avatar type: ', self.type)
        return dg.getMessage()

    def makeFromNetString(self, string):
        dg = PyDatagram(string)
        dgi = PyDatagramIterator(dg)
        self.type = dgi.getFixedString(1)
        if self.type == 's':
            self.name = dgi.getFixedString(3)
            self.dept = dgi.getFixedString(1)
            self.body = getSuitBodyType(self.name)
        elif self.type == 'b':
            self.dept = dgi.getFixedString(1)
        else:
            notify.error('unknown avatar type: ', self.type)
        return None

    def __defaultGoon(self):
        self.type = 'g'
        self.name = goonTypes[0]

    def __defaultSuit(self):
        self.type = 's'
        self.name = 'ds'
        self.dept = getSuitDept(self.name)
        self.body = getSuitBodyType(self.name)

    def newSuit(self, name = None):
        if name == None:
            self.__defaultSuit()
        else:
            self.type = 's'
            self.name = name
            self.dept = getSuitDept(self.name)
            self.body = getSuitBodyType(self.name)
        return

    def newBossCog(self, dept):
        self.type = 'b'
        self.dept = dept

    def newSuitRandom(self, level = None, dept = None):
        self.type = 's'
        if level == None:
            level = random.choice(range(1, len(suitsPerLevel)))
        elif level < 0 or level > len(suitsPerLevel):
            notify.error('Invalid suit level: %d' % level)
        if dept == None:
            dept = random.choice(suitDepts)
        self.dept = dept
        index = suitDepts.index(dept)
        base = index * suitsPerDept
        offset = 0
        if level > 1:
            for i in xrange(1, level):
                offset = offset + suitsPerLevel[i - 1]

        bottom = base + offset
        top = bottom + suitsPerLevel[level - 1]
        self.name = suitHeadTypes[random.choice(range(bottom, top))]
        self.body = getSuitBodyType(self.name)
        return

    def newGoon(self, name = None):
        if type == None:
            self.__defaultGoon()
        else:
            self.type = 'g'
            if name in goonTypes:
                self.name = name
            else:
                notify.error('unknown goon type: ', name)
        return

    def getType(self):
        if self.type == 's':
            type = 'suit'
        elif self.type == 'b':
            type = 'boss'
        else:
            notify.error('Invalid DNA type: ', self.type)
        return type
