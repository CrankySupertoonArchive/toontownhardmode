from direct.showbase.PythonUtil import Enum, invertDictLossless
from direct.interval.IntervalGlobal import *
import types
import random
Tricks = Enum('JUMP, BEG, PLAYDEAD, ROLLOVER, BACKFLIP, DANCE, SPEAK, BALK,')
NonHappyMinActualTrickAptitude = 0.5
NonHappyMaxActualTrickAptitude = 0.75
MinActualTrickAptitude = 0.8
MaxActualTrickAptitude = 0.97
AptitudeIncrementDidTrick = 0.05
MaxAptitudeIncrementGotPraise = 0.03
MaxTrickFatigue = 0.05
MinTrickFatigue = 0.01
ScId2trickId = {21200: Tricks.JUMP,
 21201: Tricks.BEG,
 21202: Tricks.PLAYDEAD,
 21203: Tricks.ROLLOVER,
 21204: Tricks.BACKFLIP,
 21205: Tricks.DANCE,
 21206: Tricks.SPEAK}
TrickId2scIds = invertDictLossless(ScId2trickId)
TrickAnims = {Tricks.JUMP: 'jump',
 Tricks.BEG: ('toBeg', 'beg', 'fromBeg'),
 Tricks.PLAYDEAD: ('playDead', 'fromPlayDead'),
 Tricks.ROLLOVER: 'rollover',
 Tricks.BACKFLIP: 'backflip',
 Tricks.DANCE: 'dance',
 Tricks.SPEAK: 'speak',
 Tricks.BALK: 'neutral'}
TrickLengths = {Tricks.JUMP: 2.0,
 Tricks.BEG: 5.167,
 Tricks.PLAYDEAD: 15.21,
 Tricks.ROLLOVER: 8.0,
 Tricks.BACKFLIP: 4.88,
 Tricks.DANCE: 7.42,
 Tricks.SPEAK: 0.75,
 Tricks.BALK: 1.0}
TrickAccuracies = {Tricks.JUMP: 1.0,
 Tricks.BEG: 1.0,
 Tricks.PLAYDEAD: 0.95,
 Tricks.ROLLOVER: 0.95,
 Tricks.BACKFLIP: 0.9,
 Tricks.DANCE: 0.9,
 Tricks.SPEAK: 0.85,
 Tricks.BALK: 1.0}
TrickHeals = {Tricks.JUMP: (15, 20),
 Tricks.BEG: (15, 20),
 Tricks.PLAYDEAD: (20, 25),
 Tricks.ROLLOVER: (20, 25),
 Tricks.BACKFLIP: (25, 30),
 Tricks.DANCE: (25, 30),
 Tricks.SPEAK: (30, 35 ),
 Tricks.BALK: (0, 0)}
TrickSounds = {Tricks.BACKFLIP: 'phase_5/audio/sfx/backflip.ogg',
 Tricks.ROLLOVER: 'phase_5/audio/sfx/rollover.ogg',
 Tricks.PLAYDEAD: 'phase_5/audio/sfx/play_dead.ogg',
 Tricks.BEG: 'phase_5/audio/sfx/beg.ogg',
 Tricks.DANCE: 'phase_5/audio/sfx/heal_dance.ogg',
 Tricks.JUMP: 'phase_5/audio/sfx/jump.ogg',
 Tricks.SPEAK: 'phase_5/audio/sfx/speak_v1.ogg'}

def getSoundIval(trickId):
    sounds = TrickSounds.get(trickId, None)
    if sounds:
        if type(sounds) == types.StringType:
            sound = loader.loadSfx(sounds)
            return SoundInterval(sound)
        else:
            soundIval = Sequence()
            for s in sounds:
                sound = loader.loadSfx(s)
                soundIval.append(SoundInterval(sound))

            return soundIval
    return


def getTrickIval(pet, trickId):
    anims = TrickAnims[trickId]
    animRate = random.uniform(0.9, 1.1)
    waitTime = random.uniform(0.0, 1.0)
    if type(anims) == types.StringType:
        if trickId == Tricks.JUMP:
            animIval = Parallel()
            animIval.append(ActorInterval(pet, anims, playRate=animRate))
            animIval.append(Sequence(Wait(0.36), ProjectileInterval(pet, startPos=pet.getPos(), endPos=pet.getPos(), duration=1.0, gravityMult=0.5)))
        elif trickId == Tricks.ROLLOVER:
            animIval = Sequence()
            animIval.append(ActorInterval(pet, anims, playRate=animRate))
            animIval.append(ActorInterval(pet, anims, playRate=-1.0 * animRate))
        elif trickId == Tricks.SPEAK:
            animIval = ActorInterval(pet, anims, startFrame=10, playRate=animRate)
        else:
            animIval = ActorInterval(pet, anims, playRate=animRate)
    else:
        animIval = Sequence()
        for anim in anims:
            animIval.append(ActorInterval(pet, anim, playRate=animRate))

    trickIval = Parallel(animIval)
    soundIval = getSoundIval(trickId)
    if soundIval:
        trickIval.append(soundIval)
    return Sequence(Func(pet.lockPet), Wait(waitTime), trickIval, Func(pet.unlockPet))
