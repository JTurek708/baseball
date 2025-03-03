### Park Factors forAndrew Vaughn
library(baseballr)

# Load data
plays2021 <- read.csv("2021plays.csv")
plays2022 <- read.csv("2022plays.csv")
plays2023 <- read.csv("2023plays.csv")
plays2024 <- read.csv("2024plays.csv")

all_plays <- bind_rows(plays2021, plays2022, plays2023, plays2024)
View(all_plays)

# Filter for Andrew Vaughn
events <- all_plays |>
  map(pluck, "event") |>
  bind_rows() |>
  as_tibble()
View(events)
