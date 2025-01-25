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

# Filter for different stadiums
# Add a new column indicating the stadium
sox_games <- sox_games %>%
  mutate(
    runs = awr + hmr,  # Combined runs for both teams
    stadium = case_when(
      ParkID == "CHI10" ~ "Comiskey",
      ParkID == "CHI12" ~ "Rate Field",
      TRUE ~ "Other"
    ),
    year = year(ymd(Date))  # Extract year from the Date column
  )

# Plot
ggplot(sox_games, aes(x = year, y = runs, color = stadium)) +
  # Plotting mean lines for each stadium group
  stat_summary(fun = mean, geom = "line", aes(group = stadium), size = 1.2) +
  # Add points for clarity (optional)
  stat_summary(fun = mean, geom = "point", size = 2) +
  # Customize labels and titles
  xlab("Season") +
  ylab("Average Runs per Game (Combined)") +
  ggtitle("Run Scoring Trends by Stadium for Chicago White Sox Games (1981 - 2001)") +
  labs(caption = "Data retrieved via Retrosheet") +
  # Color palette for the stadium categories
  scale_color_manual(
    name = "Stadium",
    values = c("Comiskey" = "blue", "Rate Field" = "red", "Other" = "black")
  ) +
  # Theme adjustments for a clean, professional look
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold", size = 16), # Centered, bold title
    legend.position = "top", # Move legend to the top
    legend.title = element_text(face = "bold"), # Bold legend title
    legend.text = element_text(size = 12), # Larger legend text
    axis.text = element_text(size = 12), # Larger axis text
    axis.title = element_text(size = 14) # Larger axis titles
  )
