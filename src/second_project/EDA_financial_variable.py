# EDA - FINANCIALS VARIABLES


# Inspection of df_demo

df_demo.info()
df_demo.isnull().sum()

# Inspection of df_exp

print(df_exp.shape)
df_exp.info()
df_exp['Variation'].value_counts()

# Explore the distribution of financial variables

financial_cols = ['bal', 'num_accts', 'clnt_age', 'clnt_tenure_yr', 'calls_6_mnth', 'logons_6_mnth']

# Histograms for visual sense of shape/skew
df_demo[financial_cols].hist(bins=30, figsize=(12, 8))
plt.tight_layout()
plt.show()




# Balance specifically is usually heavily skewed (a few very high balances)

plt.figure(figsize=(8, 4))
plt.hist(df_demo['bal'].dropna(), bins=50)
plt.title('Distribution of Account Balance (bal)')
plt.xlabel('Balance')
plt.ylabel('Number of Clients')
plt.show()

plt.figure(figsize=(8, 4))
plt.hist(df_demo['bal'].dropna(), bins=50)
plt.yscale('log')
plt.title('Distribution of Account Balance (log scale)')
plt.xlabel('Balance')
plt.ylabel('Number of Clients (log scale)')
plt.show()



# Summarize with descriptive statistics

df_demo[financial_cols].describe()




# Median and skew balance is likely right-skewed (a few very wealthy clients)

summary_stats = df_demo[financial_cols].agg(['mean', 'median', 'std', 'min', 'max', 'skew']).T
print(summary_stats)


df_demo[financial_cols].skew().sort_values(ascending=False)


# Gender breakdown (relevant to the customer profile)

df_demo['gendr'].value_counts()


# Customer profile

profile_summary = pd.DataFrame({
    'metric': [
        'Average age',
        'Median age',
        'Average tenure (years)',
        'Average balance',
        'Median balance',
        'Average number of accounts',
        'Average calls (6mo)',
        'Average logons (6mo)'
    ],
    'value': [
        df_demo['clnt_age'].mean(),
        df_demo['clnt_age'].median(),
        df_demo['clnt_tenure_yr'].mean(),
        df_demo['bal'].mean(),
        df_demo['bal'].median(),
        df_demo['num_accts'].mean(),
        df_demo['calls_6_mnth'].mean(),
        df_demo['logons_6_mnth'].mean()
    ]
})
print(profile_summary)




# Identify patterns / segments / unusual observations


# Age segments 
bins = [0, 30, 45, 60, 100]
labels = ['<30', '30-45', '45-60', '60+']
df_demo['age_group'] = pd.cut(df_demo['clnt_age'], bins=bins, labels=labels)

print(df_demo['age_group'].value_counts())
df_demo.groupby('age_group', observed=True)['bal'].mean()



# Balance vs tenure relationship 

df_demo.groupby('age_group', observed=True)[['bal', 'num_accts', 'logons_6_mnth']].mean()


# Unusual observations: outlier balances (IQR method)

Q1 = df_demo['bal'].quantile(0.25)
Q3 = df_demo['bal'].quantile(0.75)
IQR = Q3 - Q1
upper_bound = Q3 + 1.5 * IQR

outliers = df_demo[df_demo['bal'] > upper_bound]
print(f"Upper bound for 'normal' balance: {upper_bound:,.2f}")
print(f"Number of outlier clients (very high balance): {len(outliers)}")
outliers[['client_id', 'bal', 'clnt_age', 'num_accts']].sort_values('bal', ascending=False).head(10)


# Clients with very low digital engagement (0 logons in 6 months)

low_engagement = df_demo[df_demo['logons_6_mnth'] == 0]
print(f"Clients with 0 logons in the last 6 months: {len(low_engagement)}")


# Correlation between financial/engagement variables

corr = df_demo[financial_cols].corr()
print(corr)


# Bring in the A/B test group for context (merge on client_id)

df_demo_exp = pd.merge(df_demo, df_exp, on='client_id', how='left')

print(df_demo_exp.shape)
df_demo_exp['Variation'].value_counts(dropna=False)


# Sanity check: are Test and Control groups reasonably balanced on the financial variables? (important for a valid A/B test)

df_demo_exp.groupby('Variation')[financial_cols].mean()


# Filter out clients not in the experiment

df_ab = df_demo_exp[df_demo_exp['Variation'].notnull()].copy()
print(df_ab['Variation'].value_counts())



# Visualize distributions

financial_cols = ['bal', 'num_accts', 'clnt_age', 'clnt_tenure_yr', 'calls_6_mnth', 'logons_6_mnth']
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
axes = axes.flatten()
for i, col in enumerate(financial_cols):
    df_ab.boxplot(column=col, by='Variation', ax=axes[i])
    axes[i].set_title(col)
    axes[i].set_xlabel('')
plt.suptitle('')
plt.tight_layout()
plt.show()




# Compare full descriptive statistics

df_ab.groupby('Variation')[financial_cols].describe().T


# Standardized mean differences (SMD)

import numpy as np

grp = df_demo_exp.groupby('Variation')[financial_cols]

n_c = len(df_demo_exp[df_demo_exp['Variation'] == 'Control'])
n_t = len(df_demo_exp[df_demo_exp['Variation'] == 'Test'])

mean_c = grp.mean().loc['Control']
mean_t = grp.mean().loc['Test']
std_c  = grp.std().loc['Control']
std_t  = grp.std().loc['Test']

s_pooled = np.sqrt(((n_c - 1) * std_c**2 + (n_t - 1) * std_t**2) / (n_c + n_t - 2))
smd = (mean_t - mean_c) / s_pooled

smd_df = smd.to_frame(name='SMD')
smd_df['Mean_Diff'] = mean_t - mean_c
smd_df['Std_Control'] = std_c
smd_df['Std_Test'] = std_t
smd_df


# Formal statistical test

from scipy import stats
control = df_ab[df_ab['Variation'] == 'Control']
test = df_ab[df_ab['Variation'] == 'Test']
for col in financial_cols:
    stat, p_value = stats.ttest_ind(
        control[col].dropna(),
        test[col].dropna(),
        equal_var=False  # Welch's t-test, safer default (doesn't assume equal variance)
    )
    result = "Significant difference" if p_value < 0.05 else "No significant difference"
    print(f"{col}: p-value = {p_value:.4f} -> {result}")


# Investigate the 20,109 clients with no Variation


# Filter: clients NOT in the experiment
not_in_experiment = df_demo_exp[df_demo_exp['Variation'].isnull()]

# Filter: clients IN the experiment
in_experiment = df_demo_exp[df_demo_exp['Variation'].notnull()]

print(f"Not in experiment: {len(not_in_experiment)}")
print(f"In experiment: {len(in_experiment)}")


# Compare their profiles -- are the excluded clients demographically
# different, or do they look like a random subset? (helps distinguish
# "excluded by design" vs "data linkage issue")
comparison = pd.DataFrame({
    'in_experiment_mean': in_experiment[financial_cols].mean(),
    'not_in_experiment_mean': not_in_experiment[financial_cols].mean()
})
print(comparison)


# Check if the excluded group also appears in the web activity log
# (if they DO show activity but no Variation, that points to a
# data linkage issue rather than deliberate exclusion)
excluded_ids = not_in_experiment['client_id']
excluded_with_web_activity = df_demo_exp[df_demo_exp['client_id'].isin(excluded_ids)]

print(f"Excluded clients who DO have web activity: {excluded_with_web_activity['client_id'].nunique()}")
print(f"Excluded clients total: {excluded_ids.nunique()}")


# Missing values -- filter to preview before/after (no rows dropped from df_demo_exp itself)


# Preview: rows WITH missing values (the "before" view)
rows_with_missing = df_demo_exp[df_demo_exp.isnull().any(axis=1)]
print(f"Rows with at least one missing value: {len(rows_with_missing)}")
rows_with_missing.head(15)




# Preview: what the dataset would look like AFTER dropping (stored as a separate df, original is untouched)
df_demo_exp_nomiss = df_demo_exp[df_demo_exp.notnull().all(axis=1)]

print(f"Before: {df_demo_exp.shape}")
print(f"After (missing rows filtered out): {df_demo_exp_nomiss.shape}")



# Alternative preview: what it would look like if imputed instead (median for numeric columns, mode for gendr) -- also a separate df
df_demo_exp_imputed = df_demo_exp.copy()

numeric_cols = ['clnt_tenure_yr', 'clnt_tenure_mnth', 'clnt_age',
                 'num_accts', 'bal', 'calls_6_mnth', 'logons_6_mnth']

for col in numeric_cols:
    df_demo_exp_imputed[col] = df_demo_exp_imputed[col].fillna(df_demo_exp_imputed[col].median())

df_demo_exp_imputed['gendr'] = df_demo_exp_imputed['gendr'].fillna(df_demo_exp_imputed['gendr'].mode()[0])

print(f"Missing values after imputation: {df_demo_exp_imputed.isnull().sum().sum()}")



#Engagement imbalance caveat -- filter Test/Control and quantify the calls/logons gap directly on the web data


# Filter to only clients that are in BOTH the experiment AND have web data
web_client_ids = df_demo_exp['client_id'].unique()
df_ab_with_web = df_ab[df_ab['client_id'].isin(web_client_ids)]

print(f"Experiment clients with matching web activity: {len(df_ab_with_web)}")




# Filter Control and Test separately (for a clean before/after-style
# comparison of the engagement variables specifically)
control_engagement = df_ab[df_ab['Variation'] == 'Control'][['calls_6_mnth', 'logons_6_mnth']]
test_engagement = df_ab[df_ab['Variation'] == 'Test'][['calls_6_mnth', 'logons_6_mnth']]

engagement_summary = pd.DataFrame({
    'Control_mean': control_engagement.mean(),
    'Test_mean': test_engagement.mean(),
    'difference': control_engagement.mean() - test_engagement.mean()
})
print(engagement_summary)


# Effect sizes (Cohen's d) -- practical significance, not just statistical significance


def cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    var1, var2 = group1.var(ddof=1), group2.var(ddof=1)
    pooled_std = (((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2)) ** 0.5
    return (group1.mean() - group2.mean()) / pooled_std

control = df_ab[df_ab['Variation'] == 'Control']
test = df_ab[df_ab['Variation'] == 'Test']

effect_sizes = {}
for col in financial_cols:
    d = cohens_d(control[col].dropna(), test[col].dropna())
    effect_sizes[col] = d

effect_sizes_df = pd.DataFrame.from_dict(effect_sizes, orient='index', columns=['cohens_d'])
effect_sizes_df['abs_d'] = effect_sizes_df['cohens_d'].abs()

def interpret_d(d):
    d = abs(d)
    if d < 0.2:
        return 'Negligible'
    elif d < 0.5:
        return 'Small'
    elif d < 0.8:
        return 'Medium'
    else:
        return 'Large'

effect_sizes_df['interpretation'] = effect_sizes_df['cohens_d'].apply(interpret_d)
print(effect_sizes_df)




























# Standardized mean differences (SMD)

import numpy as np

grp = df_demo_exp.groupby('Variation')[financial_cols]

n_c = len(df_demo_exp[df_demo_exp['Variation'] == 'Control'])
n_t = len(df_demo_exp[df_demo_exp['Variation'] == 'Test'])

mean_c = grp.mean().loc['Control']
mean_t = grp.mean().loc['Test']
std_c  = grp.std().loc['Control']
std_t  = grp.std().loc['Test']

s_pooled = np.sqrt(((n_c - 1) * std_c**2 + (n_t - 1) * std_t**2) / (n_c + n_t - 2))
smd = (mean_t - mean_c) / s_pooled

smd_df = smd.to_frame(name='SMD')
smd_df['Mean_Diff'] = mean_t - mean_c
smd_df['Std_Control'] = std_c
smd_df['Std_Test'] = std_t
smd_df




































