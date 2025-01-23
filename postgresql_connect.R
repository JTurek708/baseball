### PostgreSQL Connection
install.packages("RPostgres")
library(RPostgres)

# Connection to PostgreSQL DB
con <- dbConnect(
  RPostgres::Postgres(), user = "postgres", 
  password = "MarquetteWarriors2013!!",
  dbname = "baseball",
  host = "localhost",
  port = 5434
)
class(con)
