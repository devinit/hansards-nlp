list.of.packages <- c("data.table", "anytime")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
lapply(list.of.packages, require, character.only=T)

setwd("~/git/hansards-nlp/data")

dat = fread("ke_mombasa_health_sector.csv")
filename_split = strsplit(dat$filename, split="_")
filename_indices = c()
for(i in 1:length(filename_split)){
  filename_index = filename_split[[i]][length(filename_split[[i]])]
  filename_indices = c(filename_indices, filename_index)
}
dat$filename = substr(dat$filename, 1, nchar(dat$filename)-2)
dat$batch_index = filename_indices

unique_filenames = unique(dat$filename)
for(filename in unique_filenames){
  data_indices = which(dat$filename==filename)
  dat_sub = dat[data_indices,]
  dat_sub_first = dat_sub[which(dat_sub$batch_index==0)]
  first_date_str = dat_sub_first$transcript_date
  dat[data_indices, "transcript_date"] = first_date_str
}

dat$transcript_date = gsub(" , ", ", ", dat$transcript_date)
for(weekday in c("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")){
  weekday_with_comma = paste0(weekday,", ")
  dat$transcript_date = gsub(weekday_with_comma, "", dat$transcript_date)
  weekday_with_space = paste0(weekday," ")
  dat$transcript_date = gsub(weekday_with_space, "", dat$transcript_date)
}

for(suffix in c("st ", "nd " ,"rd ", "th ")){
  dat$transcript_date = gsub(suffix, " ", dat$transcript_date)
}

for(first_digit in 0:9){
  for(second_digit in 0:9){
    two_digit_number_with_space = paste(first_digit, second_digit)
    two_digit_number_without_space = paste0(first_digit, second_digit)
    dat$transcript_date = gsub(two_digit_number_with_space, two_digit_number_without_space, dat$transcript_date)
  }
}

for(wonky_february in c("Februa ry", "Febru ary")){
  dat$transcript_date = gsub(wonky_february, "February", dat$transcript_date)
}

dat$transcript_date_parsed = anydate(dat$transcript_date)
sum(is.na(dat$transcript_date_parsed))

dat = dat[order(dat$transcript_date_parsed, dat$filename, dat$batch_index),
          c(
            "transcript_date_parsed"
            ,"filename"
            ,"batch_index"
            ,"health_discussed"
            ,"health_discussed_people_names"
            ,"health_data_information_systems_discussed"
            ,"health_data_information_systems_summary"
            ,"health_data_challenges"
            ,"health_service_delivery_improvement_recommendations"
            ,"health_sector_decisions"
            ,"health_evidence_base"
            ,"health_evidence_requested"
          )
        ]

names(dat) = c(
  "Date",
  "Filename",
  "Batch Index",
  "Was health discussed at any point during this transcript?",
  "People that participated in discussions about health",
  "Were there discussions about health data or health information systems at any point during this transcript?",
  "Summary of discussions about health data or health information systems",
  "What challenges did the discussions around health data or health information systems identify?",
  "What recommendations were discussed to improve health service delivery?",
  "What decisions or resolutions or policies or laws were made regarding financing the health sector?",
  "What evidence was used to inform any decisions or recommendations or resolutions or policies or laws?",
  "What health information was requested or demanded, and who was it requested from?"
)
fwrite(dat,"ke_mombasa_health_sector_formatted.csv")