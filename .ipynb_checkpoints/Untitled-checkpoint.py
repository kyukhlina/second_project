# Sort DataFrame by client_id, visit_id, and date_time
test_group.sort_values(by=['client_id', 'visit_id', 'date_time'], inplace=True)

# Define the required sequence of steps
required_steps = ['start', 'step_1', 'step_2', 'step_3', 'confirm']

# Group by client_id and visit_id, then aggregate the process steps into a list
groups = test_group.groupby(['client_id', 'visit_id'])['process_step'].agg(list)

# Filter groups to include only those with the complete sequence
filtered_groups = groups[groups.apply(lambda x: x == required_steps)]

# Merge filtered groups back with the original DataFrame to get the rows for the clients with the required sequence
filtered_df = pd.merge(df, filtered_groups, on=['client_id', 'visit_id'])

filtered_df.shape