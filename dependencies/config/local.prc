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
model-cache-models #t
model-cache-textures #t
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

# Art assets:
vfs-mount resources/phase_3 /phase_3
vfs-mount resources/phase_3.5 /phase_3.5
vfs-mount resources/phase_4 /phase_4
vfs-mount resources/phase_5 /phase_5
vfs-mount resources/phase_5.5 /phase_5.5
vfs-mount resources/phase_6 /phase_6
vfs-mount resources/phase_7 /phase_7
vfs-mount resources/phase_8 /phase_8
vfs-mount resources/phase_9 /phase_9
vfs-mount resources/phase_10 /phase_10
vfs-mount resources/phase_11 /phase_11
vfs-mount resources/phase_12 /phase_12
vfs-mount resources/phase_13 /phase_13
vfs-mount resources/phase_14 /phase_14
vfs-mount resources/server /server
model-path /

# DClass file:
dc-file dependencies/astron/dclass/stride.dc

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
want-governbot-headquarters #f
want-eurekabot-headquarters #f
want-buildbot-headquarters #f
want-viralbot-headquarters #f

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
want-garden-game #f
want-language-selection #f

# Chat:
want-whitelist #t
want-sequence-list #f

# Developer options:
show-population #t
want-instant-parties #t
want-instant-delivery #t
cogdo-pop-factor 0.5
cogdo-ratio 0.5
default-directnotify-level info
accountdb-type developer

# Crates:
dont-destroy-crate #f
get-key-reward-always #t
get-crate-reward-always #t

# Temporary:
smooth-lag 0.4
want-old-fireworks #t