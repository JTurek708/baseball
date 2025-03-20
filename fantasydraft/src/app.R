### Draft Shiny Dashboard ###
library(shiny)
library(shinydashboard)
library(tidyverse)
library(DT)
library(readr)

## Process Hitters ##
# Read hitters projection files for ZiPS, Steamer, and OOPSY
zips_hitters <- read_csv("zips_fantasy.csv") %>% 
  rename_at(vars(-Name), ~ paste0(., "_zips")) 
View(zips_hitters)
steamer_hitters <- read_csv("steamer_fantasy.csv") %>% 
  rename_at(vars(-Name), ~ paste0(., "_steamer")) 
View(steamer_hitters)
oopsy_hitters <- read_csv("oopsy_fantasy.csv") %>% 
  rename_at(vars(-Name), ~ paste0(., "_oopsy")) 
View(oopsy_hitters)
