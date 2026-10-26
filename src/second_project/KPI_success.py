KPI_success

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats

# Combine web data and convert time 


df_web = pd.concat([df1, df2], axis=0, ignore_index=True)
df_web['date_time'] = pd.to_datetime(df_web['date_time'], errors='coerce')

print(df_web.shape)
df_web.head()


# Merge in Variation, filter to experiment clients only

df_web = pd.merge(df_web, df_exp, on='client_id', how='left')

# Filter out clients not part of the experiment (preview before/after)
df_web_all = df_web.copy()                          # keep full version for reference
df_web = df_web[df_web['Variation'].notnull()]      # filtered working version

print(f"Before filtering: {df_web_all.shape}")
print(f"After filtering to experiment clients: {df_web.shape}")
df_web['Variation'].value_counts()


df_web = df_web.sort_values(
    by=['visit_id', 'date_time']
).reset_index(drop=True)


journey_check = (
    df_web.groupby('visit_id')['process_step']
    .apply(list)
    .reset_index(name='journey')
)

journey_check.head(10)



ideal_path = ['start', 'step_1', 'step_2', 'step_3', 'confirm']

journey_check['is_ideal'] = (
    journey_check['journey']
    .apply(lambda x: x == ideal_path)
)

journey_check['is_ideal'].value_counts()



non_ideal = journey_check[
    ~journey_check['is_ideal']
]

non_ideal.head(20)



successful_nonlinear = journey_check[
    journey_check['journey'].apply(lambda x:
    ('confirm' in x) &
    (x != ideal_path)
)
]

successful_nonlinear.head(20)




journey_check['has_backtracking'] = journey_check['journey'].apply(
    lambda x: any(
    step_order_map[x[i]] > step_order_map[x[i+1]]
    for i in range(len(x)-1)
    )
)

journey_check['has_backtracking'].value_counts()



sample_visit = df_web['visit_id'].sample(1).iloc[0]

df_web.loc[
    df_web['visit_id'] == sample_visit,
        ['visit_id', 'date_time', 'process_step']
].sort_values('date_time')



# Map process_step to a numeric order

step_order_map = {
    'start': 0,
    'step_1': 1,
    'step_2': 2,
    'step_3': 3,
    'confirm': 4
}
df_web['step_order'] = df_web['process_step'].map(step_order_map)

# Sort so every visit's events are in chronological order
df_web = df_web.sort_values(by=['visit_id', 'date_time']).reset_index(drop=True)



# Build one row per visit_id (journey-level table)

def build_journey(group):
    # Collapse consecutive duplicate steps (e.g. step_2, step_2 -> step_2)
    steps_in_order = group['process_step'].tolist()
    collapsed = [steps_in_order[0]]
    for s in steps_in_order[1:]:
        if s != collapsed[-1]:
            collapsed.append(s)

    return pd.Series({
        'client_id': group['client_id'].iloc[0],
        'Variation': group['Variation'].iloc[0],
        'step_sequence': collapsed,
        'start_time': group.loc[group['process_step'] == 'start', 'date_time'].min(),
        'confirm_time': group.loc[group['process_step'] == 'confirm', 'date_time'].min(),
        'n_events': len(group)
    })

journeys = df_web.groupby('visit_id').apply(build_journey, include_groups=False).reset_index()

print(journeys.shape)
journeys.head()


# Build one row per visit_id without collapsing repeated steps

def build_journey_raw(group):

    return pd.Series({
        'client_id': group['client_id'].iloc[0],
        'Variation': group['Variation'].iloc[0],
        'step_sequence': group['process_step'].tolist(), # keep all steps
        'start_time': group.loc[group['process_step']=='start', 'date_time'].min(),
        'confirm_time': group.loc[group['process_step']=='confirm', 'date_time'].min(),
        'n_events': len(group)
})

journeys_raw = (
    df_web
    .sort_values(['visit_id', 'date_time'])
    .groupby('visit_id')
    .apply(build_journey_raw, include_groups=False)
    .reset_index()
)

journeys_raw.head()




comparison = (
    journeys[['visit_id', 'n_events']]
    .merge(
        journeys_raw[['visit_id', 'n_events']],
        on='visit_id',
        suffixes=('_collapsed', '_raw')
    )
)

comparison['duplicates_removed'] = (
    comparison['n_events_raw']
    - comparison['n_events_collapsed']
)

comparison['duplicates_removed'].describe()




comparison = comparison.merge(
    journeys[['visit_id', 'Variation']],
    on='visit_id'
)

comparison.groupby('Variation')['duplicates_removed'].agg([
    'count',
    'mean',
    'median',
    'max'
])



# Journey Length

journeys_raw.groupby('Variation')['n_events'].describe()



journeys_raw['path'] = journeys_raw['step_sequence'].apply(
    lambda x: " > ".join(x)
)

journeys_raw.groupby('Variation')['path']\
    .value_counts()\
    .groupby(level=0)\
    .head(10)


# Flag successful journeys (exact expected sequence)

expected_sequence = ['start', 'step_1', 'step_2', 'step_3', 'confirm']

journeys['is_successful'] = journeys['step_sequence'].apply(lambda seq: seq == expected_sequence)

success_counts = journeys['is_successful'].value_counts()
print(success_counts)
print(f"Success rate: {journeys['is_successful'].mean() * 100:.2f}%")




# Preview a few successful and unsuccessful journeys side by side

print("Example successful journey:")
print(journeys[journeys['is_successful']].iloc[0][['visit_id', 'step_sequence']])

print("\nExample unsuccessful journey:")
print(journeys[~journeys['is_successful']].iloc[0][['visit_id', 'step_sequence']])





# Filter to successful journeys only

journeys_success = journeys[journeys['is_successful']].copy()

print(f"All journeys: {len(journeys)}")
print(f"Successful journeys: {len(journeys_success)}")
print(journeys_success['Variation'].value_counts())




success_counts.plot(
    kind='barh',
    color=['tomato', 'seagreen'],
    figsize=(8,4)
)

plt.title('Successful vs Unsuccessful Journeys')
plt.xlabel('Number of Clients')
plt.ylabel('')

plt.show()



plt.figure(figsize=(6,6))

plt.pie(
    success_counts,
    labels=['Not Successful', 'Successful'],
    autopct='%1.1f%%',
    startangle=90
)

plt.title('Percentage of Successful Journeys')
plt.show()



journey_summary = journeys.groupby(['Variation', 'is_successful']) \
                            .size() \
                            .unstack(fill_value=0)

journey_summary.plot(
    kind='bar',
    stacked=True,
    figsize=(8,5),
    color=['salmon', 'steelblue']
)

plt.title('Journey Outcomes by Variation')
plt.xlabel('Variation')
plt.ylabel('Number of Journeys')
plt.legend(['Unsuccessful', 'Successful'])

plt.xticks(rotation=0)

plt.show()



# Success rate Comparison 

success_rate = (
    journeys.groupby('Variation')['is_successful']
    .mean()
    .mul(100)
    .reset_index()
)

plt.figure(figsize=(6,4))

sns.barplot(
    data=success_rate,
    x='Variation',
    y='is_successful',
    palette='Set2'
)



pd.crosstab(
    journeys['Variation'],
    journeys['is_successful'],
    normalize='index'
) * 100



success_by_group = pd.crosstab(
    journeys['Variation'],
    journeys['is_successful'],
    normalize='index'
) * 100



sample_visits = (
    journeys_success['visit_id']
    .sample(10, random_state=42)
)

sample_journeys = df_web[
    df_web['visit_id'].isin(sample_visits)
    ].sort_values(['visit_id', 'date_time'])

sample_journeys[
    ['visit_id',
    'client_id',
    'Variation',
    'date_time',
    'process_step']
]



sample_journeys['time_to_next_step'] = (
    sample_journeys.groupby('visit_id')['date_time']
    .diff()
    .dt.total_seconds()
)

sample_journeys




for visit in sample_visits[:5]:

    temp = (
    df_web[df_web['visit_id'] == visit]
    .sort_values('date_time')
)

    print(f"\nVisit ID: {visit}")
    print("-"*50)

    for _, row in temp.iterrows():
        print(
            f"{row['date_time']} -> {row['process_step']}"
)





journeys_success['completion_time_sec'] = (
    journeys_success['confirm_time']
    - journeys_success['start_time']
).dt.total_seconds()



fastest = journeys_success.nsmallest(
    5,
    'completion_time_sec'
)

slowest = journeys_success.nlargest(
    5,
    'completion_time_sec'
)

print("FASTEST JOURNEYS")
display(
    fastest[['visit_id', 'Variation', 'completion_time_sec']]
)

print("SLOWEST JOURNEYS")
display(
    slowest[['visit_id', 'Variation', 'completion_time_sec']]
)




top5_fast = journeys_success.nsmallest(
    5,
    'completion_time_sec'
)

top5_slow = journeys_success.nlargest(
    5,
    'completion_time_sec'
)

plt.figure(figsize=(10,6))

plt.barh(
    top5_fast['visit_id'].astype(str),
    top5_fast['completion_time_sec'],
    color='green',
    label='Fastest'
)

plt.barh(
    top5_slow['visit_id'].astype(str),
    top5_slow['completion_time_sec'],
    color='red',
    label='Slowest'
)

plt.xlabel('Completion Time (seconds)')
plt.title('Fastest vs Slowest Successful Journeys')
plt.legend()
plt.show()




fast_visit = fastest.iloc[0]['visit_id']
slow_visit = slowest.iloc[0]['visit_id']

fast_journey = (
    df_web[df_web['visit_id'] == fast_visit]
    .sort_values('date_time')
)

slow_journey = (
    df_web[df_web['visit_id'] == slow_visit]
    .sort_values('date_time')
)




fast_journey = fast_journey.copy()
slow_journey = slow_journey.copy()

fast_journey['elapsed_sec'] = (
    fast_journey['date_time']
    - fast_journey['date_time'].min()
).dt.total_seconds()

slow_journey['elapsed_sec'] = (
    slow_journey['date_time']
    - slow_journey['date_time'].min()

).dt.total_seconds()



# Calculate completion time (in minutes) per journey

journeys_success['completion_time_min'] = (
    journeys_success['confirm_time'] - journeys_success['start_time']
).dt.total_seconds() / 60

journeys_success['completion_time_min'].describe()



# Visualize the distribution
plt.figure(figsize=(8, 4))
plt.hist(journeys_success['completion_time_min'], bins=50)
plt.title('Distribution of Completion Time (successful journeys)')
plt.xlabel('Minutes')
plt.ylabel('Number of Journeys')
plt.show()





# Flag (not remove) unusually long completion times

Q1 = journeys_success['completion_time_min'].quantile(0.25)
Q3 = journeys_success['completion_time_min'].quantile(0.75)
IQR = Q3 - Q1
upper_bound = Q3 + 1.5 * IQR

journeys_success['is_long_completion'] = journeys_success['completion_time_min'] > upper_bound

print(f"Upper bound for 'normal' completion time: {upper_bound:.2f} minutes")
print(f"Flagged as unusually long: {journeys_success['is_long_completion'].sum()}")
print(f"Percentage flagged: {journeys_success['is_long_completion'].mean() * 100:.2f}%")






# visualisation

success_counts = journeys_success['Variation'].value_counts()

plt.figure(figsize=(6,4))

sns.barplot(
    x=success_counts.index,
    y=success_counts.values,
    palette='Set2',
)
plt.title('Successful Journeys by Variation'),
plt.xlabel('Variation'),
plt.ylabel('Number of Successful Journeys'),



for i, value in enumerate(success_counts.values):
    plt.text(i, value + 100, f'{value:,}', ha='center')

plt.show()




# Compare the KPI with vs. without the flagged long journeys
with_outliers = journeys_success['completion_time_min'].mean()
without_outliers = journeys_success.loc[~journeys_success['is_long_completion'], 'completion_time_min'].mean()

print(f"Mean completion time (all successful journeys): {with_outliers:.2f} min")
print(f"Mean completion time (excluding flagged long ones): {without_outliers:.2f} min")
print(f"Median completion time (robust to outliers): {journeys_success['completion_time_min'].median():.2f} min")



plt.figure(figsize=(10,6))

sns.histplot(
    journeys_success['completion_time_min'],
    bins=50,
    kde=True
)

plt.axvline(
    journeys_success['completion_time_min'].median(),
    color='green',
    linestyle='--',
    label='Median'
)

plt.axvline(
    journeys_success['completion_time_min'].mean(),
    color='red',
    linestyle='--',
    label='Mean'
)

plt.legend()
plt.title('Distribution of Completion Times')
plt.xlabel('Minutes')

plt.show()




# Compare completion time by Variation

completion_by_group = journeys_success.groupby('Variation')['completion_time_min'].agg(
    ['count', 'mean', 'median', 'std']
)
print(completion_by_group)



# Same comparison, excluding flagged long journeys
completion_by_group_no_outliers = journeys_success[~journeys_success['is_long_completion']].groupby('Variation')['completion_time_min'].agg(
    ['count', 'mean', 'median', 'std']
)
print(completion_by_group_no_outliers)



# Boxplot for a visual comparison
journeys_success.boxplot(column='completion_time_min', by='Variation', figsize=(6, 5))
plt.title('Completion Time by Group')
plt.suptitle('')
plt.ylabel('Minutes')
plt.show()



kpi_compare = pd.DataFrame({
    'With Long Journeys': journeys_success.groupby('Variation')['completion_time_min'].mean(),
    'Without Long Journeys':
        journeys_success.loc[
            ~journeys_success['is_long_completion']
        ].groupby('Variation')['completion_time_min'].mean()
})

kpi_compare.plot(
    kind='bar',
    figsize=(9,6)
)

plt.title('Average Completion Time: With vs Without Long Journeys')
plt.ylabel('Minutes')

plt.show()



# t-test + Cohen's d on completion time

control_time = journeys_success[journeys_success['Variation'] == 'Control']['completion_time_min']
test_time = journeys_success[journeys_success['Variation'] == 'Test']['completion_time_min']

t_stat, p_value = stats.ttest_ind(control_time, test_time, equal_var=False)

def cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    var1, var2 = group1.var(ddof=1), group2.var(ddof=1)
    pooled_std = (((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2)) ** 0.5
    return (group1.mean() - group2.mean()) / pooled_std

d = cohens_d(control_time, test_time)

print(f"p-value: {p_value:.5f}")
print(f"Cohen's d: {d:.4f}")




# Correlate calls_6_mnth / logons_6_mnth with success

# Bring in demographic data and merge onto the journey-level table
url_demo = "https://raw.githubusercontent.com/data-bootcamp-v4/lessons/refs/heads/main/5_6_eda_inf_stats_tableau/project/files_for_project/df_final_demo.txt"
df_demo = pd.read_csv(url_demo)

journeys_full = pd.merge(journeys, df_demo[['client_id', 'calls_6_mnth', 'logons_6_mnth']],
                          on='client_id', how='left')

# Compare engagement levels: successful vs unsuccessful journeys
journeys_full.groupby('is_successful')[['calls_6_mnth', 'logons_6_mnth']].mean()




# Point-biserial correlation (binary is_successful vs continuous variable)
from scipy.stats import pointbiserialr

corr_calls, p_calls = pointbiserialr(journeys_full['is_successful'], journeys_full['calls_6_mnth'])
corr_logons, p_logons = pointbiserialr(journeys_full['is_successful'], journeys_full['logons_6_mnth'])

print(f"calls_6_mnth vs success: r = {corr_calls:.4f}, p = {p_calls:.5f}")
print(f"logons_6_mnth vs success: r = {corr_logons:.4f}, p = {p_logons:.5f}")




# Effective Time for successful journeys excluding any single gap that looks like an abnormal pause rather than real UI time

def compute_step_gaps(visit_id, df):
    visit_data = df[df['visit_id'] == visit_id].sort_values('date_time')
    # Only keep one timestamp per distinct step (first occurrence),
    # since successful journeys are already collapsed to one of each
    first_occurrence = visit_data.drop_duplicates(subset='process_step', keep='first')
    times = first_occurrence.sort_values('step_order')['date_time'].tolist()
    gaps = [(times[i+1] - times[i]).total_seconds() / 60 for i in range(len(times)-1)]
    return gaps

# Apply only to successful journeys (can be slow on the full dataset --
# consider running on a sample first to confirm logic, then scale up)
sample_visits = journeys_success['visit_id'].head(1000)  # start with a sample
gap_records = []
for vid in sample_visits:
    gaps = compute_step_gaps(vid, df_web)
    gap_records.append({'visit_id': vid, 'gaps': gaps, 'max_gap': max(gaps), 'total_gap': sum(gaps)})

gap_df = pd.DataFrame(gap_records)
gap_df.head()




#Flag abnormally long individual gaps (using IQR on the max gap per journey)

Q1 = gap_df['max_gap'].quantile(0.25)
Q3 = gap_df['max_gap'].quantile(0.75)
IQR = Q3 - Q1
gap_upper_bound = Q3 + 1.5 * IQR

gap_df['has_abnormal_pause'] = gap_df['max_gap'] > gap_upper_bound
print(f"Abnormal pause threshold: {gap_upper_bound:.2f} minutes")
print(f"Journeys with an abnormal pause: {gap_df['has_abnormal_pause'].sum()}")

# Effective time = total time MINUS any single abnormal pause
gap_df['effective_time_min'] = gap_df.apply(
    lambda row: row['total_gap'] - row['max_gap'] if row['has_abnormal_pause'] else row['total_gap'],
    axis=1
)
gap_df[['visit_id', 'total_gap', 'effective_time_min', 'has_abnormal_pause']].head()




# Check statistical assumptions before comparison

from scipy.stats import shapiro, levene

control_time = journeys_success[journeys_success['Variation'] == 'Control']['completion_time_min']
test_time = journeys_success[journeys_success['Variation'] == 'Test']['completion_time_min']

# 1. Normality (Shapiro's test is sensitive at large N -- pair with a visual check)
print("Normality check (visual is more reliable at this sample size):")
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].hist(control_time, bins=40)
axes[0].set_title('Control - Completion Time')
axes[1].hist(test_time, bins=40)
axes[1].set_title('Test - Completion Time')
plt.show()

# 2. Equal variance
levene_stat, levene_p = levene(control_time, test_time)
print(f"Levene's test p-value: {levene_p:.5f}")
print("-> Use Welch's t-test (unequal variance) if p < 0.05; standard t-test otherwise")

# 3. Independence: check how many clients have multiple successful journeys
repeat_clients = journeys_success['client_id'].value_counts()
print(f"Clients with more than 1 successful journey: {(repeat_clients > 1).sum()}")

# 4. Sample size per group
print(journeys_success['Variation'].value_counts())





unsuccessful_journeys = journeys[
    journeys['is_successful'] == False
]

print(f"Number of unsuccessful journeys: {len(unsuccessful_journeys)}")

unsuccessful_journeys.head()



unsuccessful_journeys = journeys[~journeys['is_successful']]


unsuccessful_journeys[['visit_id', 'Variation', 'step_sequence']].head(20)


unsuccessful_journeys['path'] = unsuccessful_journeys['step_sequence'].astype(str)

(
        unsuccessful_journeys['path']
        .value_counts()
        .head(20)
)



no_confirm = unsuccessful_journeys[
    unsuccessful_journeys['step_sequence'].apply(
        lambda x: 'confirm' not in x
    )
]

print(len(no_confirm))



confirm_but_not_ideal = unsuccessful_journeys[
    unsuccessful_journeys['step_sequence'].apply(
        lambda x: 'confirm' in x
    )
]

print(len(confirm_but_not_ideal))
















































































































































































































































































































































































































































































































































































































































































































































































