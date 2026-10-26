## Second project. Vanguard Digital Experience Analysis

### Business goal
Vanguard believed that a more intuitive and modern User Interface (UI), coupled with timely in-context prompts (cues, messages, hints, or instructions provided to users directly within the context of their current task or action), could make the online process smoother for clients. The critical question was: Would these changes encourage more clients to complete the process?

### Progect goal
Analysis of A/B test results for redisined client process based on collected client events. This repo contains the analysis notebooks and the final stakeholder presentation (vanguard_ab_test.ppt).

### Contribution
**Nadia**
Notebooks: 
- Step1_web_data_pt1.ipynb, 
- Step2_web_data_pt2.ipynb, 
- Step3_web_data_concat.ipynb, 
- Step4_EDA_Financial.ipynb, 
- Step5_KPI_Success.ipynb

Additional files:
- Tableu dashboards

Covered steps:
 - data cleaning and investigation
 - focusing on data from "Digital Footprints (df_final_web_data)", than merging and grouping the data from all dataframes
 - investigating finential metrics
 - EDA validatin for experiment
 - calculations of success KPIs (completion rate, rate of reaching confirm, and completion time — and compared Test vs. Control (Step 5))
 - statistical tests for variance, confidence intervals, and outlier-robustness checks on the completion-time result

**Carla**
Notebooks:
- demographic_comparision_carla.ipynb, 
- customer's_journey_carla.ipynb, 
- Abandoned_journey.ipynb

Covered steps:
- data cleaning and investigation
- focusing on data from "Client Profiles (df_final_demo)", than merging and grouping the data from all dataframes
- investigating demographical metrics
- EDA validatin for experiment
- calculations of KPIs for abandonment journeys (a journey that reaches start but never reaches confirm) and built the journey-level dataset to measure it

**Kseniia**
Notebooks:
- customr_journey_Kseniia_Iukhlina.ipynb, 
- df_investigations_Kseniia_iukhlina.ipynb,

Additional files:
- Presentation

Covered steps:
- data cleaning and investigation
- focusing on data from "Experiment Roster (df_final_experiment_clients)", than merging and grouping the data from all dataframes
- investigating digital engagement metrics
- EDA validatin for experiment
- calculations of KPIs for journeys that reached confirmation but contains errors (backwards and duplicated steps)

