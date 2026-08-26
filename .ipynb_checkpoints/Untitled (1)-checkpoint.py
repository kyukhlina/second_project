# Sort the DataFrame by 'client_id' and 'date_time'
test_cpl_rate= filtered_df.sort_values(by=['client_id', 'date_time'])
# Calculate the time spent on each step by taking the difference between consecutive timestamps
test_cpl_rate['time_spent'] = test_cpl_rate.groupby('client_id')['date_time'].diff()
# If you want the time in seconds, you can convert it like this
test_cpl_rate['time_spent_seconds'] = test_cpl_rate['time_spent'].dt.total_seconds()
# Now 'time_spent_seconds' column will contain the time spent on each step in seconds