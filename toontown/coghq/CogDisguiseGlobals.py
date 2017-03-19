from toontown.suit import SuitDNA
import types
from toontown.toonbase import TTLocalizer
from direct.showbase import PythonUtil
from otp.otpbase import OTPGlobals
from toontown.battle import SuitBattleGlobals
PartsPerSuit = (17,
 14,
 12,
 10,
 17,
 17,
 17,
 17)
PartsPerSuitBitmasks = (131071,
 130175,
 56447,
 56411,
 131071,
 131071,
 131071,
 131071)
AllBits = 131071
MinPartLoss = 1
MaxPartLoss = 2
MeritsPerLevel = ((200,
  130,
  160,   #flunky
  190,
  800,
  0,
  0,
  0),
 (160,
  210,
  260,   #pencil pusher
  310,
  1300,
  0,
  0,
  0),
 (260,
  340,
  420,
  500,   #yesman
  2100,
  0,
  0,
  0),
 (420,
  550,
  680,   #micromanager
  810,
  3400,
  0,
  0,
  0),
 (680,
  890,
  1100,
  1310,
  5500,   #downsizer
  0,
  0,
  0),
 (1100,
  1440,
  1780,
  2120,   #headhunter
  8900,
  0,
  0,
  0),
 (1780,
  2330,
  2880,
  3430,
  14400,  #corporate raider
  0,
  0,
  0),
 (3770,
  4660,
  5500,
  23300,   #big cheese
  2880,
  23300,
  23300,
  0),
 (150,
  80,
  100,
  120,    #bottom feeder
  500,
  0,
  0,
  0),
 (100,
  130,
  160,
  190,   #bloodsucker
  800,
  0,
  0,
  0),
 (160,
  210,
  260,
  310,
  1300,  #double talker
  0,
  0,
  0),
 (260,
  340,
  420,   #ambulance chaser
  500,
  2100,
  0,
  0,
  0),
 (420,
  550,
  680,
  810,
  3400,   #back stabber
  0,
  0,
  0),
 (680,
  890,
  1100,
  1310,
  5500,   #spin doctor
  0,
  0,
  0),
 (1100,
  1440,
  1780,
  2120,
  8900,   #legal eagle
  0,
  0,
  0),
 (2330,
  2880,
  3430,    #big wig
  14400,
  1780,
  14400,
  14400,
  0),
 (100,
  50,
  60,
  70,
  300,   #short change
  0,
  0,
  0),
 (60,
  80,
  100,
  120,    #penny pincher
  500,
  0,
  0,
  0),
 (100,
  130,
  160,
  190,
  800,   #tightwad
  0,
  0,
  0),
 (160,
  210,
  260,
  310,   #bean counter
  1300,
  0,
  0,
  0),
 (260,
  340,
  420,
  500,
  2100,  #number cruncher
  0,
  0,
  0),
 (420,
  550,
  680,
  810,
  3400,   #money bags
  0,
  0,
  0),
 (680,
  890,
  1100,
  1310,
  5500,   #loan shark
  0,
  0,
  0),
 (1440,
  1780,
  2120,
  8900,   #robber baron
  1100,
  8900,
  8900,
  0),
 (50,
  65,
  85,
  110,   #cold caller
  140,
  280,
  0,
  0),
 (70,
  100,
  135,
  175,   #telemarketer
  215,
  265,
  530,
  0),
 (100,
  145,
  195,
  250,    #name dropper
  310,
  375,
  445,
  890),
 (140,
  200,
  265,
  335,  #glad hander
  410,
  490,
  575,
  665),
 (190,
  265,
  345,
  430,   #mover and shaker
  520,
  615,
  715,
  820),
 (250,
  340,
  435,
  535,
  640,  #two face
  750,
  865,
  985),
 (320,
  425,
  535,
  650,
  770,   #mingler
  895,
  1025,
  1160),
 (520,
  645,
  775,
  1550,   #mr hollywood
  1440,
  1590,
  4480,
  0),
 (200,
  130,
  160,
  190,
  800,  #v1 governbots
  0,
  0,
  0),
 (160,
  210,
  260,
  310,
  1300,  #v2
  0,
  0,
  0),
 (260,
  340,
  420,
  500,
  2100,  #account-ant
  0,
  0,
  0),
 (420,
  550,
  680,
  810,
  3400,   #v4
  0, 
  0,
  0),
 (680,
  890,
  1100,
  1310,
  5500,   #v5
  0,
  0,
  0),
 (1100,
  1440,
  1780,
  2120,
  8900,    #rat racer
  0,
  0,
  0),
 (1780,
  2330,
  2880,
  3430,    #v7
  14400,
  0,
  0,
  0),
 (3770,
  4660,
  5500,    #v8
  23300,
  2880,
  23300,
  23300,
  0),
 (100,
  50,
  60,
  70,
  300,   #e1
  0,
  0,
  0),
 (60,
  80,
  100,
  120,    #e2
  500,
  0,
  0,
  0),
 (100,
  130,
  160,
  190,
  800,   #labrat
  0,
  0,
  0),
 (160,
  210,
  260,
  310,   #e4
  1300,
  0,
  0,
  0),
 (260,
  340,
  420,
  500,
  2100,  #e5
  0,
  0,
  0),
 (420,
  550,
  680,
  810,
  3400,   #the biohazard
  0,
  0,
  0),
 (680,
  890,
  1100,
  1310,
  5500,   #e7
  0,
  0,
  0),
 (1440,
  1780,
  2120,
  8900,   #frank nstine
  1100,
  8900,
  8900,
  0),
 (150,
  80,
  100,
  120,    #b1
  500,
  0,
  0,
  0),
 (100,
  130,
  160,
  190,   #b2
  800,
  0,
  0,
  0),
 (160,
  210,
  260,
  310,
  1300,  #b3
  0,
  0,
  0),
 (260,
  340,
  420,   #b4
  500,
  2100,
  0,
  0,
  0),
 (420,
  550,
  680,
  810,
  3400,   #b5
  0,
  0,
  0),
 (680,
  890,
  1100,
  1310,
  5500,   #b6
  0,
  0,
  0),
 (1100,
  1440,
  1780,
  2120,
  8900,   #b7
  0,
  0,
  0),
 (2330,
  2880,
  3430,    #b8
  14400,
  1780,
  14400,
  14400,
  0),
 (50,
  65,
  85,
  110,   #account-ant
  140,
  280,
  0,
  0),
 (70,
  100,
  135,
  175,   #z2
  215,
  265,
  530,
  0),
 (100,
  145,
  195,
  250,    #z3
  310,
  375,
  445,
  890),
 (140,
  200,
  265,
  335,  #z4
  410,
  490,
  575,
  665),
 (190,
  265,
  345,
  430,   #z5
  520,
  615,
  715,
  820),
 (250,
  340,
  435,
  535,
  640,  #z6
  750,
  865,
  985),
 (320,
  425,
  535,
  650,
  770,   #z7
  895,
  1025,
  1160),
 (520,
  645,
  775,
  1550,   #z8
  1440,
  1590,
  4480,
  0))
leftLegUpper = 1
leftLegLower = 2
leftLegFoot = 4
rightLegUpper = 8
rightLegLower = 16
rightLegFoot = 32
torsoLeftShoulder = 64
torsoRightShoulder = 128
torsoChest = 256
torsoHealthMeter = 512
torsoPelvis = 1024
leftArmUpper = 2048
leftArmLower = 4096
leftArmHand = 8192
rightArmUpper = 16384
rightArmLower = 32768
rightArmHand = 65536
upperTorso = torsoLeftShoulder
leftLegIndex = 0
rightLegIndex = 1
torsoIndex = 2
leftArmIndex = 3
rightArmIndex = 4
PartsQueryShifts = (leftLegUpper,
 rightLegUpper,
 torsoLeftShoulder,
 leftArmUpper,
 rightArmUpper)
PartsQueryMasks = (leftLegFoot + leftLegLower + leftLegUpper,
 rightLegFoot + rightLegLower + rightLegUpper,
 torsoPelvis + torsoHealthMeter + torsoChest + torsoRightShoulder + torsoLeftShoulder,
 leftArmHand + leftArmLower + leftArmUpper,
 rightArmHand + rightArmLower + rightArmUpper)
PartNameStrings = TTLocalizer.CogPartNames
SimplePartNameStrings = TTLocalizer.CogPartNamesSimple
PartsQueryNames = ({1: PartNameStrings[0],
  2: PartNameStrings[1],
  4: PartNameStrings[2],
  8: PartNameStrings[3],
  16: PartNameStrings[4],
  32: PartNameStrings[5],
  64: PartNameStrings[6],
  128: PartNameStrings[7],
  256: PartNameStrings[8],
  512: PartNameStrings[9],
  1024: PartNameStrings[10],
  2048: PartNameStrings[11],
  4096: PartNameStrings[12],
  8192: PartNameStrings[13],
  16384: PartNameStrings[14],
  32768: PartNameStrings[15],
  65536: PartNameStrings[16]},
 {1: PartNameStrings[0],
  2: PartNameStrings[1],
  4: PartNameStrings[2],
  8: PartNameStrings[3],
  16: PartNameStrings[4],
  32: PartNameStrings[5],
  64: SimplePartNameStrings[0],
  128: SimplePartNameStrings[0],
  256: SimplePartNameStrings[0],
  512: SimplePartNameStrings[0],
  1024: PartNameStrings[10],
  2048: PartNameStrings[11],
  4096: PartNameStrings[12],
  8192: PartNameStrings[13],
  16384: PartNameStrings[14],
  32768: PartNameStrings[15],
  65536: PartNameStrings[16]},
 {1: PartNameStrings[0],
  2: PartNameStrings[1],
  4: PartNameStrings[2],
  8: PartNameStrings[3],
  16: PartNameStrings[4],
  32: PartNameStrings[5],
  64: SimplePartNameStrings[0],
  128: SimplePartNameStrings[0],
  256: SimplePartNameStrings[0],
  512: SimplePartNameStrings[0],
  1024: PartNameStrings[10],
  2048: PartNameStrings[11],
  4096: PartNameStrings[12],
  8192: PartNameStrings[12],
  16384: PartNameStrings[14],
  32768: PartNameStrings[15],
  65536: PartNameStrings[15]},
 {1: PartNameStrings[0],
  2: PartNameStrings[1],
  4: PartNameStrings[1],
  8: PartNameStrings[3],
  16: PartNameStrings[4],
  32: PartNameStrings[4],
  64: SimplePartNameStrings[0],
  128: SimplePartNameStrings[0],
  256: SimplePartNameStrings[0],
  512: SimplePartNameStrings[0],
  1024: PartNameStrings[10],
  2048: PartNameStrings[11],
  4096: PartNameStrings[12],
  8192: PartNameStrings[12],
  16384: PartNameStrings[14],
  32768: PartNameStrings[15],
  65536: PartNameStrings[15]},
 {1: PartNameStrings[0],
  2: PartNameStrings[1],
  4: PartNameStrings[2],
  8: PartNameStrings[3],
  16: PartNameStrings[4],
  32: PartNameStrings[5],
  64: PartNameStrings[6],
  128: PartNameStrings[7],
  256: PartNameStrings[8],
  512: PartNameStrings[9],
  1024: PartNameStrings[10],
  2048: PartNameStrings[11],
  4096: PartNameStrings[12],
  8192: PartNameStrings[13],
  16384: PartNameStrings[14],
  32768: PartNameStrings[15],
  65536: PartNameStrings[16]},
 {1: PartNameStrings[0],
  2: PartNameStrings[1],
  4: PartNameStrings[2],
  8: PartNameStrings[3],
  16: PartNameStrings[4],
  32: PartNameStrings[5],
  64: PartNameStrings[6],
  128: PartNameStrings[7],
  256: PartNameStrings[8],
  512: PartNameStrings[9],
  1024: PartNameStrings[10],
  2048: PartNameStrings[11],
  4096: PartNameStrings[12],
  8192: PartNameStrings[13],
  16384: PartNameStrings[14],
  32768: PartNameStrings[15],
  65536: PartNameStrings[16]},
 {1: PartNameStrings[0],
  2: PartNameStrings[1],
  4: PartNameStrings[2],
  8: PartNameStrings[3],
  16: PartNameStrings[4],
  32: PartNameStrings[5],
  64: PartNameStrings[6],
  128: PartNameStrings[7],
  256: PartNameStrings[8],
  512: PartNameStrings[9],
  1024: PartNameStrings[10],
  2048: PartNameStrings[11],
  4096: PartNameStrings[12],
  8192: PartNameStrings[13],
  16384: PartNameStrings[14],
  32768: PartNameStrings[15],
  65536: PartNameStrings[16]},
 {1: PartNameStrings[0],
  2: PartNameStrings[1],
  4: PartNameStrings[2],
  8: PartNameStrings[3],
  16: PartNameStrings[4],
  32: PartNameStrings[5],
  64: PartNameStrings[6],
  128: PartNameStrings[7],
  256: PartNameStrings[8],
  512: PartNameStrings[9],
  1024: PartNameStrings[10],
  2048: PartNameStrings[11],
  4096: PartNameStrings[12],
  8192: PartNameStrings[13],
  16384: PartNameStrings[14],
  32768: PartNameStrings[15],
  65536: PartNameStrings[16]})
suitTypes = PythonUtil.Enum(('NoSuit', 'NoMerits', 'FullSuit'))

def getNextPart(parts, partIndex, dept):
    dept = dept2deptIndex(dept)
    needMask = PartsPerSuitBitmasks[dept] & PartsQueryMasks[partIndex]
    haveMask = parts[dept] & PartsQueryMasks[partIndex]
    nextPart = ~needMask | haveMask
    nextPart = nextPart ^ nextPart + 1
    nextPart = nextPart + 1 >> 1
    return nextPart


def getPartName(partArray):
    index = 0
    for part in partArray:
        if part:
            return PartsQueryNames[index][part]
        index += 1


def isSuitComplete(parts, dept):
    dept = dept2deptIndex(dept)
    for p in xrange(len(PartsQueryMasks)):
        if getNextPart(parts, p, dept):
            return 0

    return 1

def getTotalMerits(toon, index):
    from toontown.battle import SuitBattleGlobals
    cogIndex = toon.cogTypes[index] + SuitDNA.suitsPerDept * index
    cogTypeStr = SuitDNA.suitHeadTypes[cogIndex]
    cogBaseLevel = SuitBattleGlobals.SuitAttributes[cogTypeStr]['level']
    cogLevel = toon.cogLevels[index] - cogBaseLevel
    cogLevel = max(min(cogLevel, len(MeritsPerLevel[cogIndex]) - 1), 0)
    return MeritsPerLevel[cogIndex][cogLevel]


def getTotalParts(bitString, shiftWidth = 32):
    sum = 0
    for shift in xrange(0, shiftWidth):
        sum = sum + (bitString >> shift & 1)

    return sum


def asBitstring(number):
    array = []
    shift = 0
    if number == 0:
        array.insert(0, '0')
    while pow(2, shift) <= number:
        if number >> shift & 1:
            array.insert(0, '1')
        else:
            array.insert(0, '0')
        shift += 1

    str = ''
    for i in xrange(0, len(array)):
        str = str + array[i]

    return str


def asNumber(bitstring):
    num = 0
    for i in xrange(0, len(bitstring)):
        if bitstring[i] == '1':
            num += pow(2, len(bitstring) - 1 - i)

    return num


def dept2deptIndex(dept):
    if type(dept) == types.StringType:
        dept = SuitDNA.suitDepts.index(dept)
    return dept

