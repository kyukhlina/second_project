Concatenate_final notebook

# Import Pandas

import pandas as pd

# Load the two datasets

url_pt1 = "https://raw.githubusercontent.com/data-bootcamp-v4/lessons/refs/heads/main/5_6_eda_inf_stats_tableau/project/files_for_project/df_final_web_data_pt_1.txt"
url_pt2 = "https://raw.githubusercontent.com/data-bootcamp-v4/lessons/refs/heads/main/5_6_eda_inf_stats_tableau/project/files_for_project/df_final_web_data_pt_2.txt"

df1 = pd.read_csv(url_pt1)
df2 = pd.read_csv(url_pt2)

# Check df1

print(df1.shape)
df1.head()


# Check df2 

print(df2.shape)
df2.head()


# Check column and data types for both 

df1.info()
df2.info()


# Check for missing values for both 

df1.isnull().sum()
df2.isnull().sum()



# Check for duplicate rows (both dfs)

print("df1 duplicates:", df1.duplicated().sum())
print("df2 duplicates:", df2.duplicated().sum())


# Sanity Check that both dfs have the same columns (Before concatenating)


print(df1.columns.tolist())
print(df2.columns.tolist())
print(df1.columns.equals(df2.columns))


# Check for overlap between df1 and df2 (make sure no identical rows exist in both files before stacking them)

overlap = pd.merge(df1, df2, how='inner')
print("Overlapping rows:", len(overlap))


# Concatenate df1 and df2 into one dataset (should equal df1.shape[0] + df2.shape[0] rows, same 5 columns)

df_web_data = pd.concat([df1, df2], axis=0, ignore_index=True)

print(df_web_data.shape)



# Verify the combined dataset

df_web_data.info()
df_web_data.isnull().sum()
print("Combined duplicates:", df_web_data.duplicated().sum())
df_web_data.head()



# QUALITY CHECK 1: Missing values

df_web_data.isnull().sum()


# QUALITY CHECK 2: Duplicated rows (rows where ALL 5 columns are identical)

print("Fully duplicated rows:", df_web_data.duplicated().sum())


# view them
df_web_data[df_web_data.duplicated(keep=False)].sort_values(
    by=['client_id', 'visit_id', 'date_time']
).head(10)



#  QUALITY CHECK 3: Duplicated events
# (same client/visit/step happening again, even if the
#  exact timestamp differs slightly — for ex if a user clicking "confirm" 3 times in a row)
# ==========================================================
duplicated_events = df_web_data.duplicated(
    subset=['client_id', 'visit_id', 'process_step'], keep=False
)
print("Rows involved in duplicated events:", duplicated_events.sum())

df_web_data[duplicated_events].sort_values(
    by=['client_id', 'visit_id', 'date_time']
).head(10)


# QUALITY CHECK 4: Verify date and time column
# Convert date_time from text to datetime type
df_web_data['date_time'] = pd.to_datetime(df_web_data['date_time'], errors='coerce')


# Check if any dates failed to convert
print("Rows with invalid date_time:", df_web_data['date_time'].isnull().sum())



# Check the overall date range makes sense
print("Earliest date:", df_web_data['date_time'].min())
print("Latest date:", df_web_data['date_time'].max())



# QUALITY CHECK 5: Categorical values for inconsistencies
# process_step is the only true categorical column here
print(df_web_data['process_step'].unique())
print(df_web_data['process_step'].value_counts())

# Look for things like: extra whitespace, inconsistent casing,
# typos (e.g. "Step_1" vs "step_1" vs "step1")
print(df_web_data['process_step'].str.strip().str.lower().unique())




# QUALITY CHECK 6: Impossible or unexpected values
# Check ID columns aren't negative/zero

print(df_web_data['client_id'].describe())



# Check for any empty strings hiding in object columns
# (these won't show up in isnull() but are effectively missing)

for col in ['visitor_id', 'visit_id', 'process_step']:
    empty_count = (df_web_data[col].str.strip() == '').sum()
    print(f"{col}: {empty_count} empty string values")



# Check date_time isn't in the future or absurdly old

today = pd.Timestamp.today()
future_dates = df_web_data[df_web_data['date_time'] > today]
print("Future-dated rows:", len(future_dates))



 Check visitor_id / visit_id format consistency
#     (based on what you've seen, these look like "number_number")
bad_visitor_id = ~df_web_data['visitor_id'].str.match(r'^\d+_\d+$')
bad_visit_id = ~df_web_data['visit_id'].str.match(r'^\d+_\d+_\d+$')
print("Unexpected visitor_id format:", bad_visitor_id.sum())
print("Unexpected visit_id format:", bad_visit_id.sum())


# IDENTIFIERS

# 1. Relationship between client_id and visitor_id

# How many unique visitors does each client have?
client_visitor_counts = df_web_data.groupby('client_id')['visitor_id'].nunique()
print(client_visitor_counts.describe())
print(client_visitor_counts.sort_values(ascending=False).head(10))


# How many unique clients does each visitor belong to? (ideally a visitor_id belong to one client)
visitor_client_counts = df_web_data.groupby('visitor_id')['client_id'].nunique()
print(visitor_client_counts.value_counts())


# 2. Relationship between visitor_id and visit_id

# How many visits does each visitor have?
visitor_visit_counts = df_web_data.groupby('visitor_id')['visit_id'].nunique()
print(visitor_visit_counts.describe())
print(visitor_visit_counts.sort_values(ascending=False).head(10))


# How many unique visitors does each visit_id belong to? (ideally a visit_id belong to one visitor)
visit_visitor_counts = df_web_data.groupby('visit_id')['visitor_id'].nunique()
print(visit_visitor_counts.value_counts())


3. Can one client have multiple visitors or sessions (visits)?
# ==========================================================
clients_multiple_visitors = client_visitor_counts[client_visitor_counts > 1]
print(f"Clients with more than 1 visitor_id: {len(clients_multiple_visitors)}")
print(clients_multiple_visitors.head(10))


client_visit_counts = df_web_data.groupby('client_id')['visit_id'].nunique()
clients_multiple_visits = client_visit_counts[client_visit_counts > 1]
print(f"Clients with more than 1 visit: {len(clients_multiple_visits)}")
print(clients_multiple_visits.sort_values(ascending=False).head(10))




# 4. Can one visit contain multiple events?
visit_event_counts = df_web_data.groupby('visit_id').size()
print(visit_event_counts.describe())
print(visit_event_counts.sort_values(ascending=False).head(10))

# How many visits only have 1 event (e.g. just "start" and nothing else)?
print("Visits with only 1 event:", (visit_event_counts == 1).sum())



# 5. Verify the expected identifier hierarchy
# client_id -> visitor_id -> visit_id -> process_step (event)

# A) Every visitor_id should map to exactly ONE client_id
broken_visitor_to_client = visitor_client_counts[visitor_client_counts > 1]
print(f"visitor_ids linked to more than one client_id: {len(broken_visitor_to_client)}")



# B) Every visit_id should map to exactly ONE visitor_id
broken_visit_to_visitor = visit_visitor_counts[visit_visitor_counts > 1]
print(f"visit_ids linked to more than one visitor_id: {len(broken_visit_to_visitor)}")


# C) Combine into one summary table
hierarchy_check = pd.DataFrame({
    'visitor_ids_per_client': [client_visitor_counts.mean()],
    'visits_per_visitor': [visitor_visit_counts.mean()],
    'events_per_visit': [visit_event_counts.mean()],
    'visitor_ids_violating_hierarchy': [len(broken_visitor_to_client)],
    'visit_ids_violating_hierarchy': [len(broken_visit_to_visitor)]
})
print(hierarchy_check)


# EXPLORE WEB 

# 1. Distribution of process steps
# ==========================================================
step_counts = df_web_data['process_step'].value_counts()
print(step_counts)

# As percentages
step_pct = df_web_data['process_step'].value_counts(normalize=True) * 100
print(step_pct.round(2))


# Visualize the distribution
# ==========================================================
import matplotlib.pyplot as plt

# Define the logical funnel order (not alphabetical)
step_order = ['start', 'step_1', 'step_2', 'step_3', 'confirm']

step_counts.reindex(step_order).plot(kind='bar')
plt.title('Distribution of Process Steps')
plt.xlabel('Process Step')
plt.ylabel('Number of Events')
plt.xticks(rotation=0)
plt.show()



# 2. Determine how events are ordered
# (assign a numeric order to each step so we can check
#  sequencing later)
# ==========================================================
step_order_map = {
    'start': 0,
    'step_1': 1,
    'step_2': 2,
    'step_3': 3,
    'confirm': 4
}

df_web_data['step_order'] = df_web_data['process_step'].map(step_order_map)
df_web_data[['process_step', 'step_order']].drop_duplicates()



# 3. Check whether timestamps are chronological within each visit 
# (for ex:  did the user move forward through the funnel in time order, or jump around?)

# Sort by visit and time first
df_sorted = df_web_data.sort_values(by=['visit_id', 'date_time'])



# For each visit, check if step_order INCREASES as time increases
# (a "reversal" means a later timestamp has a LOWER step number than the one before it in that same visit)

df_sorted['step_order_prev'] = df_sorted.groupby('visit_id')['step_order'].shift(1)
df_sorted['is_reversal'] = df_sorted['step_order'] < df_sorted['step_order_prev']

reversal_counts = df_sorted.groupby('visit_id')['is_reversal'].sum()
visits_with_reversals = reversal_counts[reversal_counts > 0]

print(f"Total visits: {df_sorted['visit_id'].nunique()}")
print(f"Visits with at least one out-of-order step: {len(visits_with_reversals)}")
print(f"Percentage: {len(visits_with_reversals) / df_sorted['visit_id'].nunique() * 100:.2f}%")


# an example of a visit with reversals (sanity-check what "out of order" actually looks like in real data)

example_visit_id = visits_with_reversals.index[0]

df_sorted[df_sorted['visit_id'] == example_visit_id][
    ['client_id', 'visitor_id', 'visit_id', 'process_step', 'date_time', 'step_order']
]



# 4. Check journey completeness (does each visit start at "start" and how far does it get?)
# The furthest step reached in each visit

furthest_step = df_sorted.groupby('visit_id')['step_order'].max()
furthest_step_label = furthest_step.map({v: k for k, v in step_order_map.items()})

print(furthest_step_label.value_counts())



# 5. Identify incomplete journeys
# (visits that never reached "confirm")

furthest_step = df_sorted.groupby('visit_id')['step_order'].max()

incomplete_visits = furthest_step[furthest_step < step_order_map['confirm']]
complete_visits = furthest_step[furthest_step == step_order_map['confirm']]

print(f"Total visits: {furthest_step.shape[0]}")
print(f"Complete journeys (reached confirm): {len(complete_visits)}")
print(f"Incomplete journeys: {len(incomplete_visits)}")
print(f"Incomplete rate: {len(incomplete_visits) / furthest_step.shape[0] * 100:.2f}%")

# Breakdown of WHERE incomplete journeys dropped off
furthest_step_label = furthest_step.map({v: k for k, v in step_order_map.items()})
print(furthest_step_label.value_counts())


# 6. Investigate repeated events (same client + visit + step happening more than once)

repeated_events = df_sorted.groupby(
    ['visit_id', 'process_step']
).size().reset_index(name='event_count')

repeated_events = repeated_events[repeated_events['event_count'] > 1]

print(f"Visit/step combinations with repeats: {len(repeated_events)}")
print(repeated_events.sort_values('event_count', ascending=False).head(10))

# Which step gets repeated the most?
print(repeated_events.groupby('process_step')['event_count'].sum().sort_values(ascending=False))


# 7. Investigate multiple start events (a single visit logging "start" more than once)

start_counts = df_sorted[df_sorted['process_step'] == 'start'].groupby('visit_id').size()

multiple_starts = start_counts[start_counts > 1]
print(f"Visits with more than one 'start' event: {len(multiple_starts)}")
print(multiple_starts.sort_values(ascending=False).head(10))

# Look at an example
example_visit = multiple_starts.index[0]
df_sorted[df_sorted['visit_id'] == example_visit][
    ['client_id', 'visitor_id', 'visit_id', 'process_step', 'date_time']
]


# 8. Investigate multiple confirm events (a single visit logging "confirm" more than once)

confirm_counts = df_sorted[df_sorted['process_step'] == 'confirm'].groupby('visit_id').size()

multiple_confirms = confirm_counts[confirm_counts > 1]
print(f"Visits with more than one 'confirm' event: {len(multiple_confirms)}")
print(multiple_confirms.sort_values(ascending=False).head(10))

# Look at an example
example_visit = multiple_confirms.index[0]
df_sorted[df_sorted['visit_id'] == example_visit][
    ['client_id', 'visitor_id', 'visit_id', 'process_step', 'date_time']
]


# 9. Summary table: pulling it all together

summary = pd.DataFrame({
    'metric': [
        'Total visits',
        'Complete journeys (reached confirm)',
        'Incomplete journeys',
        'Visits with repeated steps',
        'Visits with multiple starts',
        'Visits with multiple confirms'
    ],
    'count': [
        furthest_step.shape[0],
        len(complete_visits),
        len(incomplete_visits),
        repeated_events['visit_id'].nunique(),
        len(multiple_starts),
        len(multiple_confirms)
    ]
})
print(summary)




# 10. Investigate repeated process steps consecutive repeats — the same step logged
#  back-to-back within a visit, which is different from the same step appearing twice non-consecutively)

df_sorted['prev_step'] = df_sorted.groupby('visit_id')['process_step'].shift(1)
df_sorted['is_consecutive_repeat'] = df_sorted['process_step'] == df_sorted['prev_step']
print(f"Consecutive repeated steps: {df_sorted['is_consecutive_repeat'].sum()}")

# Which step is repeated back-to-back the most?
print(df_sorted[df_sorted['is_consecutive_repeat']]['process_step'].value_counts())


# Example
example_visit = df_sorted[df_sorted['is_consecutive_repeat']]['visit_id'].iloc[0]
df_sorted[df_sorted['visit_id'] == example_visit][
    ['client_id', 'visit_id', 'process_step', 'date_time']
]





# 11. Investigate backward navigation (a later timestamp has a LOWER step number than the
#  previous event in the same visit -> user moved backward)

df_sorted['step_order_prev'] = df_sorted.groupby('visit_id')['step_order'].shift(1)
df_sorted['is_backward'] = df_sorted['step_order'] < df_sorted['step_order_prev']
backward_counts = df_sorted.groupby('visit_id')['is_backward'].sum()
visits_with_backward = backward_counts[backward_counts > 0]

print(f"Visits with backward navigation: {len(visits_with_backward)}")
print(f"Percentage of all visits: {len(visits_with_backward) / df_sorted['visit_id'].nunique() * 100:.2f}%")


# Which step transitions go backward the most? (e.g. step_3 -> step_2)
backward_transitions = df_sorted[df_sorted['is_backward']].copy()
backward_transitions['transition'] = (
    backward_transitions['prev_step'] + ' -> ' + backward_transitions['process_step']
)
print(backward_transitions['transition'].value_counts())




# 12. Investigate unusually long sessions (both by TIME duration and by EVENT count)

# Session duration in minutes (first to last event per visit)
session_duration = df_sorted.groupby('visit_id')['date_time'].agg(['min', 'max'])
session_duration['duration_minutes'] = (
    session_duration['max'] - session_duration['min']
).dt.total_seconds() / 60

print(session_duration['duration_minutes'].describe())



# Flag outliers using the IQR method

Q1 = session_duration['duration_minutes'].quantile(0.25)
Q3 = session_duration['duration_minutes'].quantile(0.75)
IQR = Q3 - Q1
upper_bound = Q3 + 1.5 * IQR
long_sessions = session_duration[session_duration['duration_minutes'] > upper_bound]

print(f"Upper bound for 'normal' session length: {upper_bound:.2f} minutes")
print(f"Unusually long sessions: {len(long_sessions)}")
print(long_sessions.sort_values('duration_minutes', ascending=False).head(10))




# Unusually long sessions by EVENT COUNT (not just time)

visit_event_counts = df_sorted.groupby('visit_id').size()

print(visit_event_counts.describe())

Q1_e = visit_event_counts.quantile(0.25)
Q3_e = visit_event_counts.quantile(0.75)
IQR_e = Q3_e - Q1_e
upper_bound_e = Q3_e + 1.5 * IQR_e
long_event_sessions = visit_event_counts[visit_event_counts > upper_bound_e]

print(f"Upper bound for 'normal' event count: {upper_bound_e:.2f}")
print(f"Sessions with unusually many events: {len(long_event_sessions)}")
print(long_event_sessions.sort_values(ascending=False).head(10))






































































































