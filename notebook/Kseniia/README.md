## Vanguard Digital Experience Analysis
Analysis of Vangard's A/B test results for redesigned client process based on collected client events.

## Business goals
1. Can we trust our data in groups?
2. How data distributed between test-group and control group?
3. Error cases on customer journey based on confirmed flow (with "start" and "confirmed" steps).
   - Do we have backward steps?
   - Does error cases decreased in test group?
   - Can we say, that the flow of test-group becomes better? In which metrics?
  
## Datasets
 - Client Profiles ([df_final_demo](https://github.com/data-bootcamp-v4/lessons/blob/main/5_6_eda_inf_stats_tableau/project/files_for_project/df_final_demo.txt)): Demographics like age, gender, and account details of our clients.
 - Digital Footprints (df_final_web_data): A detailed trace of client interactions online, divided into two parts: [pt_1](https://github.com/data-bootcamp-v4/lessons/blob/main/5_6_eda_inf_stats_tableau/project/files_for_project/df_final_web_data_pt_1.txt) and [pt_2](https://github.com/data-bootcamp-v4/lessons/blob/main/5_6_eda_inf_stats_tableau/project/files_for_project/df_final_web_data_pt_2.txt). It's recommended to merge these two files prior to a comprehensive data analysis.
 - Experiment Roster ([df_final_experiment_clients](https://github.com/data-bootcamp-v4/lessons/blob/main/5_6_eda_inf_stats_tableau/project/files_for_project/df_final_experiment_clients.txt)): A list revealing which clients were part of the grand experiment.

## Tools
 - Python (pandas, numpy, matplotlib, seaborn)

## Methods & Techniques
 - EDA (Exploratory Data Analysis)
 - Data cleaning
 - Data merging
 - Hypothesis Testing
 - Descriptive Statistics
 - Conversion (test/control groups)
 - Completion time (test/control groups) 
 - Error rate

## Results & Conclusions
 - Control and test group are perfectly distributed and have the same customer types by financial and demographical parameters
 - The percentage of losses at each step of the process decreased in the test group
 - Duration of sessions was increased in test group
 - Backward steps still help clients to continue the process: with backward flow the amount of visits is higher for each step than in forward flow
 - Amount of completed journeys in test group decreased
 -  Step 3 become more stable in test group; however, we still observe a decline in the number of clients here.

    
