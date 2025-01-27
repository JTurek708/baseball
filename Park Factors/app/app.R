### Average Runs Scored Shiny App
library(fs)
library(abdwr3edata)
library(tidyverse)
library(here)
library(ggthemes)
library(shiny)
library(shinydashboard)
library(rsconnect)

weather_runs_scored <- read.csv("weather_runs_scored.csv")
team_mapping <- read.csv('team_mapping.csv')
# Convert and preprocess the data
games <- weather_runs_scored %>%
  mutate(
    Date = ymd(as.character(Date)),
    runs = awr +hmr,
    month = floor_date(Date, "month"),
    month_name = factor(
      format(month, "%B"),
      levels = month.name
    ),
    year = year(Date)
  )

games <- games %>%
  # Map team names for HomeTeam
  left_join(team_mapping, by = c("HomeTeam" = "ID")) %>%
  rename(HomeTeamName = Team) %>%  # Rename the new column for clarity
  # Map team names for VisitingTeam
  left_join(team_mapping, by = c("VisitingTeam" = "ID")) %>%
  rename(VisitingTeamName = Team) %>%  # Rename the new column for clarity
  select(-HomeTeam, -VisitingTeam) 
games <- games %>%
  select(Date, ParkID, HomeTeamName, VisitingTeamName, awr, hmr, everything()) %>%
  arrange(HomeTeamName)

# Function to calculate monthly averages
calculate_team_averages <- function(team, games_df) {
  # Identify the team's home stadium(s)
  home_stadiums <- games_df %>%
    filter(HomeTeamName == team) %>%
    pull(ParkID) %>%
    unique()
  
  # Classify games as "Home" or "Other"
  games_df %>%
    mutate(
      location = case_when(
        ParkID %in% home_stadiums ~ "Home", # Game played at team's home stadium(s)
        TRUE ~ "Other"                     # All other stadiums
      )
    ) %>%
    group_by(month_name, location) %>%
    summarize(
      avg_runs = mean(runs, na.rm = TRUE),  # Average runs scored
      .groups = "drop"
    )
}

# Function to calculate yearly averages
calculate_yearly_averages <- function(team, games_df) {
  # Identify the team's home stadium(s)
  home_stadiums <- games_df %>%
    filter(HomeTeamName == team) %>%
    pull(ParkID) %>%
    unique()
  
  # Classify games as "Home" or "Other"
  games_df %>%
    mutate(
      location = case_when(
        ParkID %in% home_stadiums ~ "Home", # Game played at team's home stadium(s)
        TRUE ~ "Other"                     # All other stadiums
      )
    ) %>%
    group_by(year, location) %>%
    summarize(
      avg_runs = mean(runs, na.rm = TRUE),  # Average runs scored
      .groups = "drop"
    )
}

# UI
ui <- fluidPage(
  titlePanel("MLB Run Scoring: Home vs. Away Stadiums (2014-2024)"),
  sidebarLayout(
    sidebarPanel(
      selectInput(
        "team",
        "Select a Team:",
        choices = unique(c(games$HomeTeamName, games$VisitingTeamName))
        #selected = "CHA"
      )
    ),
    mainPanel(
      plotOutput("teamRunsPlot"),
      br(),
      plotOutput("teamYearlyPlot")
    )
  )
)
# Shiny App Server
server <- function(input, output) {
  output$teamRunsPlot <- renderPlot({
    # Calculate averages for the selected team
    team_data <- calculate_team_averages(input$team, games)
    
    # Plot the data
    ggplot(team_data, aes(x = month_name, y = avg_runs, color = location, group = location)) +
      geom_line(size = 1.2) +
      labs(
        title = paste("Average Runs Scoring: Home vs. Away Stadiums for", input$team),
        x = "Month",
        y = "Average Runs per Game",
        color = "Location"
      ) +
      scale_color_manual(
        values = c("Home" = "blue", "Other" = "gray")
      ) +
      theme_minimal(base_size = 14) +
      theme(
        plot.title = element_text(hjust = 0.5, size = 16, face = "bold"),
        legend.position = "top"
      )
  })
  
  # Yearly graph: Yearly averages
  output$teamYearlyPlot <- renderPlot({
    team_data <- games %>%
      filter(HomeTeamName == input$team | VisitingTeamName == input$team) %>%
      mutate(
        location = case_when(
          ParkID %in% (games %>%
                         filter(HomeTeamName == input$team) %>%
                         pull(ParkID) %>%
                         unique()) ~ "Home",
          TRUE ~ "Other"
        )
      ) %>%
      group_by(year, month_name, location) %>%
      summarize(avg_runs = mean(runs, na.rm = TRUE), .groups = "drop")
    
    #print(head(team_data))
    
    # Split data by year and create individual plots
    ggplot(team_data, aes(x = month_name, y = avg_runs, color = location, group = location)) +
      geom_line(size = 1.2) +
      facet_wrap(~ year, ncol = 3) +  # Facet by year
      labs(
        title = paste("Monthly Average Run Scoring: Home vs. Away Stadiums for", input$team),
        x = "Month",
        y = "Average Runs per Game",
        color = "Location"
      ) +
      scale_color_manual(
        values = c("Home" = "blue", "Other" = "gray")
      ) +
      theme_minimal(base_size = 14) +
      theme(
        plot.title = element_text(hjust = 0.5, size = 16, face = "bold"),
        axis.text.x = element_text(angle = 45, hjust = 1),  # Rotate x-axis labels
        legend.position = "top"
      )
  })
}
# Run the App
shinyApp(ui = ui, server = server)
