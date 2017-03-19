# Window settings:
window-title Toontown Ultimate
win-origin -1 -1
icon-filename phase_3/etc/icon.ico
cursor-filename phase_3/etc/toonmono.cur

# Audio:
audio-library-name p3openal_audio
video-library-name p3ffmpeg

# Graphics:
aux-display pandagl
aux-display pandadx9
aux-display p3tinydisplay

# Models:
model-cache-models #f
model-cache-textures #f
default-model-extension .bam

# Textures:
texture-anisotropic-degree 16

# Preferences:
preferences-filename user/preferences.json

# Backups:
backups-filepath dependencies/backups/
backups-extension .json

# Server:
server-timezone EST/EDT/-5
server-port 7199
account-bridge-filename astron/databases/account-bridge.db

# Performance:
texture-power-2 none
gl-check-errors #f
garbage-collect-states #t

# Egg object types:
egg-object-type-barrier <Scalar> collide-mask { 0x01 } <Collide> { Polyset descend }
egg-object-type-trigger <Scalar> collide-mask { 0x01 } <Collide> { Polyset descend intangible }
egg-object-type-sphere <Scalar> collide-mask { 0x01 } <Collide> { Sphere descend }
egg-object-type-trigger-sphere <Scalar> collide-mask { 0x01 } <Collide> { Sphere descend intangible }
egg-object-type-floor <Scalar> collide-mask { 0x02 } <Collide> { Polyset descend }
egg-object-type-dupefloor <Scalar> collide-mask { 0x02 } <Collide> { Polyset keep descend }
egg-object-type-camera-collide <Scalar> collide-mask { 0x04 } <Collide> { Polyset descend }
egg-object-type-camera-collide-sphere <Scalar> collide-mask { 0x04 } <Collide> { Sphere descend }
egg-object-type-camera-barrier <Scalar> collide-mask { 0x05 } <Collide> { Polyset descend }
egg-object-type-camera-barrier-sphere <Scalar> collide-mask { 0x05 } <Collide> { Sphere descend }
egg-object-type-model <Model> { 1 }
egg-object-type-dcs <DCS> { 1 }

# Safe zones:
want-safe-zones #t
want-toontown-central #t
want-donalds-dock #t
want-daisys-garden #t
want-minnies-melodyland #t
want-the-brrrgh #t
want-donalds-dreamland #t
want-goofy-speedway #t
want-outdoor-zone #t
want-golf-zone #t
want-construction-zone #t

# Safe zone settings:
want-treasure-planners #t
want-suit-planners #t
want-butterflies #t

# Trolley minigames:
want-minigames #t

# Picnic table board games:
want-game-tables #t

# Cog headquarters:
want-cog-headquarters #t
want-sellbot-headquarters #t
want-cashbot-headquarters #t
want-lawbot-headquarters #t
want-bossbot-headquarters #t

# Cog battles:
base-xp-multiplier 1.0

# SOS toons:
sos-card-reward 2

# CogDominiums (Field Offices):
want-emblems #t
cogdo-want-barrel-room #t
want-lawbot-cogdo #t

# Cog buildings:
want-cogbuildings #f

# Optional:
show-total-population #t
want-mat-all-tailors #t
estate-day-night #t
want-garden-game #t
want-language-selection #f


# Chat:
want-whitelist #t
want-sequence-list #f

# Developer options:
want-dev #f
want-pstats 0

# Temporary:
smooth-lag 0.4
want-old-fireworks #t
