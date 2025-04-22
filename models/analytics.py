# Your proposal mentions:
# 
# Symptom frequency
# Disease prevalence
# Severity distribution
# Correlations
# 
# These don’t live in the DB, they live in Pandas.
# 
# So AnalyticsModel is where you:
# 
# Load data (from DB or CSV)
# Run aggregations
# Return plots, stats, summaries
# 
# Use this model only for the Analytics View/Page
# 
# Functions might include:
# 
# get_symptom_frequency()
# get_most_common_diseases()
# get_average_severity_per_symptom()
# get_symptom_correlation_matrix() (Optional with SciPy)
