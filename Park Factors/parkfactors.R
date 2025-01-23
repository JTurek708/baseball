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
