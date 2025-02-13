from pybaseball import statcast
from pybaseball import playerid_lookup
from pybaseball import statcast_pitcher
from pybaseball import pitching_stats

data = pitching_stats(2014,2016)
print(data.head())

