Loading and Exploring 

import pandas as pd

url_1 = "https://raw.githubusercontent.com/data-bootcamp-v4/lessons/refs/heads/main/5_6_eda_inf_stats_tableau/project/files_for_project/df_final_web_data_pt_1.txt"

df_final_web_data = pd.read_csv(url_1, sep=",")

df_final_web_data.head(3)


# Size of dataset
print(df1.shape)


# Check column names and data types
df1.info()


# Check for missing values
df1.isnull().sum()

# Check for duplicate rows
print(df1.duplicated().sum()) 


# Actual duplicate rows 
df1[df1.duplicated()] 


# Check unique values
df1['process_step'].unique() 

# Rows per stage ?
df1['process_step'].value_counts()  


# just checking column date

df1['date_time'].dtype

print("dtype:", df1['date_time'].dtype)

print("Missing:", df1['date_time'].isna().sum())

print("Unique:", df1['date_time'].nunique())

print("Duplicates:", df1['date_time'].duplicated().sum())



# Check for unique values for column client, visitor and visit

print("Unique client_id:", df1["client_id"].nunique())
print("Unique visitor_id:", df1["visitor_id"].nunique())
print("Unique visit_id:", df1["visit_id"].nunique())
print("Rows:", len(df1))


# Check if one client has multiple visits

df1.groupby("client_id")["visit_id"].nunique().sort_values(ascending=False).head()


# Client --> Visitor

df1.groupby("client_id")["visitor_id"].nunique().value_counts().sort_index()



# Visit --> Client 

df1.groupby("visit_id")["client_id"].nunique().value_counts()


# Visit --> Visitor 

df1.groupby("visit_id")["visitor_id"].nunique().value_counts()


# one visitor belongs to multiple clients

df1.groupby("visitor_id")["client_id"].nunique().value_counts()


# Checking for exact duplicates

df1[df1.duplicated(keep=False)].sort_values(
["client_id", "visit_id"]
)


# Check repeated process steps within a visit

duplicates_steps = df1[
    df1.duplicated(
        subset=["client_id", "visit_id", "process_step"],
        keep=False
)
]

duplicates_steps.sort_values(
["client_id", "visit_id", "process_step", "date_time"]
)




# How often it happens
(
df1.groupby(["client_id", "visit_id", "process_step"])
    .size()
    .sort_values(ascending=False)
    .head(20)
)



# inspect time differences 

df1["date_time"] = pd.to_datetime(df1["date_time"])


sample = duplicates_steps.sort_values(
    ["client_id", "visit_id", "process_step", "date_time"]
)

sample.head(10)


############################

Customer-level analysis


# Unique customers

df1["client_id"].nunique()

# Number of visits per customer
visits_per_client = df1.groupby("client_id")["visit_id"].nunique()

visits_per_client.describe()

#######

Visit (Session)-level analysis

# Verify visit -> visitor relationship
df1.groupby("visit_id")["visitor_id"].nunique().value_counts()

# Verify visit -> client relationship
df1.groupby("visit_id")["client_id"].nunique().value_counts()

#####

Event-level analysis

# Repeated process steps
(
df1.groupby(
    ["client_id", "visit_id", "process_step"]
)
    .size()
    .sort_values(ascending=False)
    .head(10)
)


# check for duplicate

df1.duplicated().sum()






# Basic descriptive stats
df1.describe(include='all')



df2.shape
df2.info()
df2.isnull().sum()
df2.duplicated().sum()