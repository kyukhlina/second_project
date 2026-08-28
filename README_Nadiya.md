# Vanguard Digital Experience Analysis

## Project Overview

Vanguard ran an A/B test to evaluate whether a redesigned online process (a new step-by-step
UI) improves the client experience compared to the existing website. This project covers the
data inspection, cleaning planning, and exploratory analysis stages that precede the formal
evaluation of that experiment — establishing whether the underlying data is trustworthy and
the experimental groups are comparable before any KPI or completion-rate comparison is made.

The central question guiding this phase of the work is:

> **Would these changes encourage more clients to complete the process?**

---

# Installation

1. **Clone the repository**:

```bash
git clone https://github.com/YourUsername/repository_name.git
```

2. **Install UV**

If you're a MacOS/Linux user type:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

If you're a Windows user open an Anaconda Powershell Prompt and type :

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

3. **Create an environment**

```bash
uv venv 
```

3. **Activate the environment**

If you're a MacOS/Linux user type (if you're using a bash shell):

```bash
source ./venv/bin/activate
```

If you're a MacOS/Linux user type (if you're using a csh/tcsh shell):

```bash
source ./venv/bin/activate.csh
```

If you're a Windows user type:

```bash
.\venv\Scripts\activate
```

4. **Install dependencies**:

```bash
uv pip install -r requirements.txt

---
## Questions

This analysis was structured around the following business questions:

1. What information does each dataset contribute to the project?
2. Are there any data quality issues that could affect the analysis?
3. Which identifier should be used for each type of analysis?
4. Can every client be confidently assigned to a single experimental group?
5. Are you confident that your data is ready for KPI computation? Why or why not?
6. Who are Vanguard's customers?
7. Do the Control and Test groups appear comparable based on their customer characteristics?
8. What statistical evidence can help determine whether observed differences are greater than
   what might be expected from sampling variability?
9. Would any observed differences meaningfully affect the experiment?
10. Is there any evidence that could make the Control vs. Test comparison unfair or affect
    interpretation of the results?

---

## Dataset

The project draws on three linked sources, joined via `client_id`:

| Dataset | Contents | Role |
|---|---|---|
| `df_final_web_data_pt_1` + `pt_2` | Clickstream/event log: `client_id`, `visitor_id`, `visit_id`, `process_step`, `date_time` | Reconstructs each client's step-by-step journey through the process (start → step_1 → step_2 → step_3 → confirm) |
| `df_final_demo` | Client demographics/financials: tenure, age, gender, number of accounts, balance, calls (6mo), logons (6mo) | Client-level profile, used to check group balance and segment behavior |
| `df_final_experiment_clients` | `client_id`, `Variation` (Test/Control) | Assigns clients to the experimental groups being compared |

The two web-data files were combined via `pd.concat` (identical schema, split rows). 
The demographics and experiment-group files were combined via `pd.merge` on `client_id` (each
contributes distinct columns).


## Notebooks 

Follow this sequence: 

Step1 Web data -> Step 2 Web data -> Step 3 Web data (Concat) -> Step4 EDA -> Step5 KPI


---

## Main Dataset Issues

**Web data (clickstream):**
- 10,764 fully duplicated rows, and 319,806 rows involved in repeated visit/step
  combinations — mostly re-clicks or reloads rather than corrupted data.
- 1,645 `visitor_id`s linked to more than one `client_id`, breaking the expected
  `client_id → visitor_id → visit_id` hierarchy.
- Widespread repeated steps (72,542 visits), backward navigation (40,516 visits), and
  multiple `confirm` events (8,965 visits) — all of which can distort funnel and
  conversion metrics if not handled deliberately.
- 43.2% of visits never reach `confirm` (incomplete journeys).

**Demographics data:**
- 14–15 rows (out of 70,609) with missing values across tenure, age, gender, accounts,
  balance, calls, and logons — a negligible ~0.02% of the dataset.
- `bal` is heavily right-skewed: mean ($147,445) is more than double the median ($63,333),
  driven by ~8,018 high-balance outlier clients.

**Experiment-group data:**
- 20,109 of the 70,609 demographic clients have no `Variation` assignment (`NaN`) — they
  were not part of the experiment, but this needed to be confirmed rather than assumed.
- Not every `client_id` in the web log necessarily has a matching `Variation` label, which
  must be checked before any Test/Control comparison of behavior.

---

## Solutions for the Dataset Issues

- **Duplicates/repeated events:** flagged and quantified rather than blindly dropped, since
  many repeats reflect genuine user behavior (re-confirming, going back a step) rather than
  logging errors. A documented rule (e.g., keep first `confirm` per visit) will be applied
  before computing conversion metrics.
- **Broken identifier hierarchy:** the 1,645 `visitor_id`s spanning multiple clients were
  isolated for review rather than silently merged or dropped, preserving the ability to
  audit them later.
- **Missing values in demographics:** filtered (not deleted) into before/after views —
  `df_demo_exp_nomiss` (rows filtered out) and `df_demo_exp_imputed` (median/mode-filled) —
  so both approaches can be compared. Given the negligible volume (0.02%), filtering out is
  the recommended default.
- **Clients with no `Variation`:** cross-referenced against the web activity log to
  distinguish clients excluded by design from a possible data-linkage issue, rather than
  assuming either explanation.
- **Balance skew/outliers:** addressed by reporting median alongside mean throughout, and by
  isolating the outlier segment (via IQR) for separate review instead of letting it distort
  headline averages.
- **Group balance:** assessed using both statistical tests (Welch's t-test) and effect sizes
  (Cohen's d), since p-values alone are misleading at this sample size (~50K clients) —
  distinguishing statistically significant differences from practically meaningful ones.

---

## Conclusions

**Who are Vanguard's customers?**
Middle-aged, long-tenured investors (mean age ~46, mean tenure ~12 years) with a median
balance around $63K and an average of ~2.3 accounts. They are moderately active digitally
(~5–6 logons per 6 months) and contact support a few times per half-year (~3–4 calls).
Balances rise substantially with age, while account counts stay fairly constant across age
groups.

**Are Control and Test comparable?**
Yes. Mean and median balances, tenure, age, account counts, calls, and logons are all very
close between groups, and quartiles/spreads are nearly identical. The only notable
difference — a higher maximum balance in Test ($8.3M vs. lower in Control) — is consistent
with the extreme right-skew already known in the data, not a systematic group difference.

**Is the "significant" difference in some variables a real concern?**
No. `num_accts`, `clnt_age`, `calls_6_mnth`, and `logons_6_mnth` returned statistically
significant p-values, but all corresponding Cohen's d values are below 0.04 — far under the
conventional 0.2 threshold for even a "small" effect. At this sample size, statistical
significance is easy to reach even for trivial differences (e.g., 47.50 vs. 47.16 years of
age), so these results reflect sample size sensitivity, not a meaningful imbalance.

**Is there evidence of unfair comparison?**
No. Aside from the outlier-driven maximum balance noted above, there is no evidence that
Control and Test differ in any way likely to bias the interpretation of the experiment's
results.

**Is the data ready for KPI computation?**
Largely yes, with caveats to carry forward: the web data's duplicate/repeated-event handling
rule must be finalized and applied consistently before computing completion rates, and the
20,109 non-experiment clients must be excluded from any Test/Control comparison. Once these
steps are applied, the data supports a fair, well-balanced comparison of the two groups.

---

**Successful Journey KPI Results (Completion Rate, Funnel, Completion Time, Effective Time)**

Following on from the data analyis above, customer journeys were reconstructed at the visit_id level. A journey was counted as successful only if it followed the exact expected sequence — start → step_1 → step_2 → step_3 → confirm — with no skipped or out-of-order steps.

**Overall completion**:
	• 24,858 successful journeys vs. 44,347 unsuccessful — an overall success rate of 35.96%.
	• Of the unsuccessful journeys, 31,525 never reached confirm at all, while 12,792 did reach confirm but only via an unusual/out-of-order route (so were not counted as "successful" under the strict definition).

**Completion Rate — Control vs. Test**:

Group	Success Rate
Control	35.21%
Test	36.62%

Test outperforms Control by +1.41 percentage points (two-proportion z-test: z = 3.85, p = 0.00012; 95% CI for the difference: [0.69%, 2.12%]). Statistically significant.

**Funnel progression** — % of journeys reaching each step:

Step	Control	Test
start	96.02%	89.28%
step_1	66.69%	64.47%
step_2	56.07%	56.31%
step_3	52.13%	53.38%
confirm	47.67%	57.70%

The two groups are similar through the middle of the funnel, but diverge sharply at the final step — Test converts to confirm about 10 percentage points more often than Control. This is the clearest behavioral difference found in the entire analysis.

**Completion Time (successful journeys only)**:

	• Overall: mean 5.15 min, median 3.65 min (right-skewed; 7.80% of journeys flagged as unusually long via IQR, threshold 11.28 min).
	• By group: Control mean 5.51 min / median 4.07 min; Test mean 4.85 min / median 3.33 min.
	• Welch's t-test: p < 0.00001 (statistically significant). Cohen's d = 0.127 — a small effect size, well under the 0.2 threshold. Test clients complete faster, but the size of the improvement is modest.

**Effective Time (forward-progress time, excluding abnormal pauses)**:
	• Mean difference (Test − Control): −0.65 minutes (Test faster), 95% CI [−0.78, −0.52]. Consistent with the Completion Time result and does not cross zero, supporting a real, if small, difference.

A nuance worth flagging: backward navigation was more common in Test (27.08% of visits) than Control (20.47%) — despite Test having both a higher completion rate and a faster completion time. This suggests the new design doesn't eliminate people going back a step, but does still get more of them to the end, and faster overall.

---

## Next Steps

	• Hand off unsuccessful-journey patterns (31,525 never-reached-confirm, 12,792 reached-confirm-via-unusual-route) to the team members covering error/abandonment rate, since this notebook intentionally scoped to successful journeys only.
	• Reconcile the backward-navigation nuance (higher in Test despite better outcomes) with the Step Backs KPI once the error-rate teammates' analysis is complete.
	• Finalize the Tableau dashboard: funnel progression, funnel conversion, completion rate, completion time, and error rate, all split Control vs. Test, with statistical significance annotated per chart.
	• Where a KPI shows a real gap between groups, break it down by age group and balance segment to check whether the new UI performs differently across customer segments.
	• Document all cleaning decisions (duplicate handling, missing-value treatment, outlier treatment) in a data dictionary so the analysis is fully reproducible.
