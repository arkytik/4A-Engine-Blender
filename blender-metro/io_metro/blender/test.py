from formats.level import Level

lvl = Level()
lvl.read(r"C:\Games\Projects\4A SDK\content\maps\2033\l00_intro\level.geom_pc")

print(len(lvl.level_parts))
