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
steamer_hitters <- read_csv("steamer_fantasy.csv") %>% 
  rename_at(vars(-Name), ~ paste0(., "_steamer")) 
oopsy_hitters <- read_csv("oopsy_fantasy.csv") %>% 
  rename_at(vars(-Name), ~ paste0(., "_oopsy")) 

# Merge
merged <- zips_hitters %>%
  full_join(steamer_hitters, by = "Name") %>%
  full_join(oopsy_hitters, by = "Name")

# We want to average across columns from each projection system.
# Identify all columns that end with one of our suffixes.
projection_suffixes <- c("zips", "steamer", "oopsy")
stat_cols <- names(merged)[grepl("_(zips|steamer|oopsy)$", names(merged))]
# Extract the unique base stat names (e.g., "FPTS", "HR", "RBI", "ERA", etc.)
stat_names <- unique(sub("_(zips|steamer|oopsy)$", "", stat_cols))
# For each stat, compute a consensus column using the row mean of the corresponding columns.
for (stat in stat_names) {
  cols <- grep(paste0("^", stat, "_(zips|steamer|oopsy)$"), names(merged), value = TRUE)
  # Convert each selected column to numeric if it isn't already.
  numeric_data <- as.data.frame(lapply(merged[, cols, drop = FALSE], function(x) as.numeric(as.character(x))))
  merged[[paste0("consensus_", stat)]] <- rowMeans(numeric_data, na.rm = TRUE)
}
# ----- Create a Consensus Data Frame -----
consensus_df <- merged %>% select(Name, starts_with("consensus_"))
consensus_df <- consensus_df %>%
  mutate(across(where(is.numeric), ~ round(.x, 0)))
View(consensus_df)

## Process Pitchers
# Read pitchers projection files for ZiPS, Steamer, and OOPSY
zips_pitchers <- read_csv("zipspitchers_fantasy.csv") %>% 
  rename_at(vars(-Name), ~ paste0(., "_zips")) 
steamer_pitchers <- read_csv("steamerpitcher_fantasy.csv") %>% 
  rename_at(vars(-Name), ~ paste0(., "_steamer")) 
oopsy_pitchers <- read_csv("oopsypitcher_fantasy.csv") %>% 
  rename_at(vars(-Name), ~ paste0(., "_oopsy")) 

# Merge
merged_pitchers <- zips_pitchers %>%
  full_join(steamer_pitchers, by = "Name") %>%
  full_join(oopsy_pitchers, by = "Name")

# We want to average across columns from each projection system.
# Identify all columns that end with one of our suffixes.
projection_suffixes <- c("zips", "steamer", "oopsy")
stat_cols <- names(merged_pitchers)[grepl("_(zips|steamer|oopsy)$", names(merged_pitchers))]
# Extract the unique base stat names (e.g., "FPTS", "HR", "RBI", "ERA", etc.)
stat_names <- unique(sub("_(zips|steamer|oopsy)$", "", stat_cols))

# For each stat, compute a consensus column using the row mean of the corresponding columns.
for (stat in stat_names) {
  cols <- grep(paste0("^", stat, "_(zips|steamer|oopsy)$"), names(merged_pitchers), value = TRUE)
  # Convert each selected column to numeric if it isn't already.
  numeric_data <- as.data.frame(lapply(merged_pitchers[, cols, drop = FALSE], function(x) as.numeric(as.character(x))))
  merged_pitchers[[paste0("consensus_", stat)]] <- rowMeans(numeric_data, na.rm = TRUE)
}

# ----- Step 4: Create a Consensus Data Frame -----
# You can choose to keep only the "Name" and consensus columns.
consensus_df_pitchers <- merged_pitchers %>% select(Name, starts_with("consensus_"))
consensus_df_pitchers <- consensus_df_pitchers %>%
  mutate(across(where(is.numeric), ~ round(.x, 0)))
#View(consensus_df_pitchers)



