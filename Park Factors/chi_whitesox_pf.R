### Fun with Park Factors & Comiskey
library(fs)
library(abdwr3edata)
library(tidyverse)
library(here)
library(ggthemes)

# Query database
query <- "
SELECT \"Date\", \"ParkID\", \"VisitingTeam\", \"HomeTeam\",
       \"VisitorRunsScored\" AS awR, \"HomeRunsScore\" AS hmR
FROM gamelogs
WHERE (\"HomeTeam\" = 'CHA' OR \"VisitingTeam\" = 'CHA')
  AND \"Date\" BETWEEN 19810101 AND 20011231;
"
sox_games <- dbGetQuery(con, query)
View(sox_games)
