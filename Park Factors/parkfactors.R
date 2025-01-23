### Computing Park Factors
remotes::install_github("beanumber/abdwr3edata")
install.packages("fs")
install.packages("here")
library(fs)
library(abdwr3edata)
library(tidyverse)
library(here)

# Function to pull retrosheet gamelogs
retrosheet_gamelog <- function(season) {
  require(abdwr3edata)
  require(fs)
  dir <- tempdir()
  glheaders <- retro_gl_header
  remote <- paste0(
    "http://www.retrosheet.org/gamelogs/gl",
    season,
    ".zip"
  )
  local <- path(dir, paste0("gl", season, ".zip"))
  download.file(url = remote, destfile=local)
  unzip(local, exdir = dir)
  local_txt <- gsub(".zip", ".txt", local)
  gamelog <- here::here(local_txt) |>
    read_csv(col_names = names(glheaders))
  file.remove(local)
  file.remove(local_txt)
  return(gamelog)
}

# Read gamelog for 2024
gl2024 <- retrosheet_gamelog(2024)

# Transfer data to PostgreSQL
if (dbExistsTable(con, "gamelogs")) {
  dbRemoveTable(con, "gamelogs")
}
con |>
  dbWriteTable(
    name = "gamelogs", value = gl2024,
    append = FALSE,
    field.types = c(
      CompletionInfo = "varchar(50)", 
      AdditionalInfo = "varchar(255)",
      HomeBatting1Name = "varchar(50)",
      HomeBatting2Name = "varchar(50)",
      HomeBatting3Name = "varchar(50)",
      HomeBatting4Name = "varchar(50)",
      HomeBatting5Name = "varchar(50)",
      HomeBatting6Name = "varchar(50)",
      HomeBatting7Name = "varchar(50)",
      HomeBatting8Name = "varchar(50)",
      HomeBatting9Name = "varchar(50)",
      HomeManagerName = "varchar(50)",
      VisitorStartingPitcherName = "varchar(50)",
      VisitorBatting1Name = "varchar(50)",
      VisitorBatting2Name = "varchar(50)",
      VisitorBatting3Name = "varchar(50)",
      VisitorBatting4Name = "varchar(50)",
      VisitorBatting5Name = "varchar(50)",
      VisitorBatting6Name = "varchar(50)",
      VisitorBatting7Name = "varchar(50)",
      VisitorBatting8Name = "varchar(50)",
      VisitorBatting9Name = "varchar(50)",
      VisitorManagerName = "varchar(50)",
      HomeLineScore = "varchar(30)",
      VisitorLineScore = "varchar(30)",
      SavingPitcherName = "varchar(50)",
      ForfeitInfo = "varchar(10)",
      ProtestInfo = "varchar(10)",
      UmpireLFID = "varchar(8)",
      UmpireRFID = "varchar(8)",
      UmpireLFName = "varchar(50)",
      UmpireRFName = "varchar(50)"
    )
  )

gamelogs <- con |>
  tbl("gamelogs")
head(gamelogs)
