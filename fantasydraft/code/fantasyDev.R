### Fantasy Baseball ###
library(tidyverse)

zips_fantasy <- zips_fantasy %>% rename_at(vars(-Name), ~paste0(., "_zips"))
steamer_fantasy <- steamer_fantasy %>% rename_at(vars(-Name), ~paste0(., "_steamer"))
oopsy_fantasy <- oopsy_fantasy %>% rename_at(vars(-Name), ~paste0(., "_oopsy"))

# Merge
merged <- zips_fantasy %>%
  full_join(steamer_fantasy, by = "Name") %>%
  full_join(oopsy_fantasy, by = "Name")
View(merged)

# ----- Step 3: Compute Consensus for Every Stat -----
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

# ----- Step 4: Create a Consensus Data Frame -----
# You can choose to keep only the "Name" and consensus columns.
consensus_df <- merged %>% select(Name, starts_with("consensus_"))
consensus_df <- consensus_df %>%
  mutate(across(where(is.numeric), ~ round(.x, 0)))
View(consensus_df)
