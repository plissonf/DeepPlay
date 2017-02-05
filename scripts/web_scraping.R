# File-Name:       Web_scraping.R
# Date:            2016-02-02
# Author:          Fabien Plisson
# Purpose:         Scrape ranking records from AIDA website 

# Loading packages
install.packages('rvest')
install.packages('XML')
install.packages('xml2')
install.packages('stringr')
install.packages('tidyr')

library(httr)
library(xml2)
library(rvest)
library(stringr)
library(tidyr)
library(curl)
library(lubridate)

# first page - The default webpage has the discipline CWT (Constant Weight)
url <- paste("https://www.aidainternational.org/Ranking/Rankings?page=1") # get URL
webpage <- read_html(url, header=TRUE)
aida_table <- html_nodes(webpage, 'table') # isolate the text and save it into a table "aida"
aida <- html_table(aida_table)[[1]] 
head(aida)

# Web scraping into R multiple links with similar URL using a for loop or lapply
## Create all URLs with initial values
page_start <- 1
page_end <- 402
base_url <- paste0("https://www.aidainternational.org/Ranking/Rankings?page=")
disc_url <- paste0("&disciplineId=7")
urls <- paste0(base_url, page_start:page_end, disc_url)

## Flatten list of lists. Loop over the urls, downloading & extracting the table with lapply()
lol <- lapply(urls, . %>% read_html() %>% html_nodes("table") %>% html_table())
aida <- do.call(rbind, lapply(lol, as.data.frame)) 
head(aida) # 8 variables and observations vary according to discipline

## Change variables values or formats in aida dataframe
# Replace first column X. by Ranking 
# Convert Result character into integer 
# Convert Date to date format with lubridate package
# Separate Name (Athlete) and Country of Origin
aida$Ranking <- aida$X.
aida$Ranking <- as.numeric(aida$Ranking)
aida$X. <- NULL

aida$Result <- gsub(" m", "", as.character(aida$Result))
aida$Result <- as.numeric(aida$Result)

aida$Result <- gsub(" min", "", as.character(aida$Result))

aida$Date <- mdy(aida$Date)
aida$Country <- str_extract_all(aida$Name, "\\([^()]+\\)")
aida$Country <- substring(aida$Country, 2, nchar(aida$Country)-1)
aida$Name <- gsub("\\([^()]+\\)", "", as.character(aida$Name))
col_idx <- grep("Ranking", names(aida))
aida <- aida[, c(col_idx, (1:ncol(aida))[-col_idx])]
names(aida)
aida <- unique(aida)
colnames(aida) <- c("Ranking", "Name", "Result_m", "Announced", "Points", "Penalties", "Date", "Place", "Country")
write.csv(aida, file = "scraped_data/results_dnf.csv",row.names=FALSE)

## CWT (Constant Weight) is the selected discipline to be displayed on screen by default
## Web-scraping data for other disciplines (option value): STA(8), DYN(6), DNF(7), CNF(4), FIM(5), CEC (10) requires some modifications











