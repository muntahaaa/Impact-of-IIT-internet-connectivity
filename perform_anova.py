import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import f_oneway
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
import warnings
warnings.filterwarnings('ignore')

# Load the comprehensive mapped data
df = pd.read_csv("comprehensive_anova_data.csv")

print("=== COMPREHENSIVE ANOVA ANALYSIS ===")
print(f"Dataset: {df.shape[0]} responses × {df.shape[1]} variables")
print("All variables are numeric and ready for ANOVA testing!")

# Define variable categories for different types of ANOVA
independent_vars = {
    'Demographics': ['Academic_Year_Score', 'Device_Capability_Score', 'Residence_Score'],
    'Infrastructure': ['WiFi_Speed_Score', 'Reliability_Score', 'Peak_Performance_Score', 'Outage_Frequency_Score'],
    'Usage_Patterns': ['Daily_Hours_Score', 'Alternative_Sources_Score', 'Schedule_Changes_Score', 'Download_Frequency_Score'],
    'Spending': ['Monthly_Spending_Score']
}

dependent_vars = {
    'Academic_Performance': ['Programming_Impact_Score', 'Collaboration_Score', 'LMS_Access_Score', 'Productivity_Influence_Score'],
    'Performance_Issues': ['Task_Abandonment_Score', 'Time_Lost_Score'],
    'Adaptation': ['Offpeak_Effectiveness_Score'],
    'Future_Expectations': ['Future_Performance_Score']
}

print("\n" + "="*80)
print("1. ONE-WAY ANOVA: WiFi Speed vs Academic Performance Variables")
print("="*80)

# Perform one-way ANOVA for WiFi Speed vs each academic performance variable
wifi_groups = {}
for speed in sorted(df['WiFi_Speed_Score'].unique()):
    wifi_groups[speed] = df[df['WiFi_Speed_Score'] == speed]

speed_labels = {1: 'Very Poor', 2: 'Poor', 3: 'Average', 4: 'Good'}

print("📊 Testing: Does WiFi Speed affect Academic Performance?")
print("\nWiFi Speed Groups:")
for speed, label in speed_labels.items():
    count = len(wifi_groups.get(speed, []))
    print(f"  {label} WiFi (Score {speed}): {count} students")

# Test each academic performance variable
academic_vars = ['Programming_Impact_Score', 'Collaboration_Score', 'LMS_Access_Score', 'Productivity_Influence_Score']

anova_results = []
for var in academic_vars:
    print(f"\n🔍 ANOVA: WiFi Speed → {var}")
    
    # Prepare groups for ANOVA
    groups = []
    group_stats = []
    for speed in sorted(df['WiFi_Speed_Score'].unique()):
        group_data = df[df['WiFi_Speed_Score'] == speed][var].values
        if len(group_data) > 0:
            groups.append(group_data)
            group_stats.append({
                'speed': speed_labels[speed],
                'n': len(group_data),
                'mean': np.mean(group_data),
                'std': np.std(group_data, ddof=1)
            })
    
    # Perform ANOVA
    if len(groups) >= 2:
        f_stat, p_value = f_oneway(*groups)
        
        print(f"   F-statistic: {f_stat:.4f}")
        print(f"   P-value: {p_value:.4f}")
        print(f"   Significant: {'✅ Yes' if p_value < 0.05 else '❌ No'} (α = 0.05)")
        
        # Store results
        anova_results.append({
            'Independent': 'WiFi_Speed_Score',
            'Dependent': var,
            'F_statistic': f_stat,
            'P_value': p_value,
            'Significant': p_value < 0.05
        })
        
        # Show group statistics
        print("   Group Statistics:")
        for stat in group_stats:
            print(f"     {stat['speed']:10} (n={stat['n']:2d}): Mean={stat['mean']:.2f}, Std={stat['std']:.2f}")
    else:
        print("   ⚠️  Not enough groups for ANOVA")

print("\n" + "="*80)
print("2. TWO-WAY ANOVA: WiFi Speed + Reliability vs Productivity")
print("="*80)

# Two-way ANOVA using statsmodels
print("📊 Testing: Do WiFi Speed AND Reliability together affect Productivity?")

# Create a combined dataset for two-way ANOVA
df_twoway = df[['WiFi_Speed_Score', 'Reliability_Score', 'Productivity_Influence_Score']].copy()
df_twoway = df_twoway.dropna()

print(f"Sample size: {len(df_twoway)} complete cases")

# Convert to categorical for better interpretation
df_twoway['WiFi_Category'] = df_twoway['WiFi_Speed_Score'].map(speed_labels)
reliability_labels = {1: 'Unreliable', 2: 'Moderate', 3: 'Reliable'}
df_twoway['Reliability_Category'] = df_twoway['Reliability_Score'].map(reliability_labels)

# Show group sizes
print("\nGroup Combinations:")
group_counts = df_twoway.groupby(['WiFi_Category', 'Reliability_Category']).size()
for (wifi, rel), count in group_counts.items():
    if count > 0:
        mean_prod = df_twoway[(df_twoway['WiFi_Category'] == wifi) & 
                             (df_twoway['Reliability_Category'] == rel)]['Productivity_Influence_Score'].mean()
        print(f"  {wifi} WiFi + {rel} Reliability: {count} students (Mean Productivity: {mean_prod:.2f})")

# Perform two-way ANOVA
try:
    model = ols('Productivity_Influence_Score ~ C(WiFi_Category) + C(Reliability_Category) + C(WiFi_Category):C(Reliability_Category)', 
                data=df_twoway).fit()
    anova_table = anova_lm(model, typ=2)
    
    print(f"\n🔍 Two-Way ANOVA Results:")
    print(anova_table)
    
    print(f"\nInterpretation:")
    wifi_p = anova_table.loc['C(WiFi_Category)', 'PR(>F)']
    rel_p = anova_table.loc['C(Reliability_Category)', 'PR(>F)']
    int_p = anova_table.loc['C(WiFi_Category):C(Reliability_Category)', 'PR(>F)']
    
    print(f"  WiFi Speed main effect: {'✅ Significant' if wifi_p < 0.05 else '❌ Not significant'} (p={wifi_p:.4f})")
    print(f"  Reliability main effect: {'✅ Significant' if rel_p < 0.05 else '❌ Not significant'} (p={rel_p:.4f})")
    print(f"  Interaction effect: {'✅ Significant' if int_p < 0.05 else '❌ Not significant'} (p={int_p:.4f})")
    
except Exception as e:
    print(f"⚠️  Two-way ANOVA error: {e}")

print("\n" + "="*80)
print("3. MULTIPLE ONE-WAY ANOVAs: Infrastructure vs Performance Issues")
print("="*80)

print("📊 Testing: How do different infrastructure factors affect performance issues?")

infrastructure_vars = ['WiFi_Speed_Score', 'Reliability_Score', 'Peak_Performance_Score', 'Outage_Frequency_Score']
performance_vars = ['Task_Abandonment_Score', 'Time_Lost_Score']

# Create a summary table of all ANOVA results
all_anova_results = []

for infra_var in infrastructure_vars:
    for perf_var in performance_vars:
        print(f"\n🔍 ANOVA: {infra_var} → {perf_var}")
        
        # Group data by infrastructure variable
        groups = []
        for level in sorted(df[infra_var].unique()):
            group_data = df[df[infra_var] == level][perf_var].values
            if len(group_data) > 0:
                groups.append(group_data)
        
        if len(groups) >= 2:
            f_stat, p_value = f_oneway(*groups)
            
            print(f"   F = {f_stat:.4f}, p = {p_value:.4f} {'✅' if p_value < 0.05 else '❌'}")
            
            all_anova_results.append({
                'Independent_Variable': infra_var,
                'Dependent_Variable': perf_var,
                'F_statistic': f_stat,
                'P_value': p_value,
                'Significant': p_value < 0.05,
                'Effect_Size': f_stat / (f_stat + len(df) - len(groups))  # Eta-squared approximation
            })

print("\n" + "="*80)
print("4. COMPREHENSIVE ANOVA RESULTS SUMMARY")
print("="*80)

# Convert results to DataFrame for easy viewing
results_df = pd.DataFrame(all_anova_results)
if len(results_df) > 0:
    print("📊 All ANOVA Test Results:")
    print(f"{'Independent Variable':<25} {'Dependent Variable':<25} {'F-stat':<8} {'P-value':<8} {'Significant':<12} {'Effect Size':<10}")
    print("-" * 95)
    
    for _, row in results_df.iterrows():
        sig_symbol = "✅ Yes" if row['Significant'] else "❌ No"
        print(f"{row['Independent_Variable']:<25} {row['Dependent_Variable']:<25} {row['F_statistic']:<8.3f} {row['P_value']:<8.4f} {sig_symbol:<12} {row['Effect_Size']:<10.3f}")

    # Summary statistics
    total_tests = len(results_df)
    significant_tests = results_df['Significant'].sum()
    print(f"\n📈 Summary:")
    print(f"   Total ANOVA tests performed: {total_tests}")
    print(f"   Significant results (p < 0.05): {significant_tests}")
    print(f"   Percentage significant: {(significant_tests/total_tests)*100:.1f}%")

    # Most significant results
    significant_results = results_df[results_df['Significant']].sort_values('P_value')
    if len(significant_results) > 0:
        print(f"\n🏆 Most Significant Findings:")
        for i, (_, row) in enumerate(significant_results.head(3).iterrows(), 1):
            print(f"   {i}. {row['Independent_Variable']} → {row['Dependent_Variable']}")
            print(f"      F = {row['F_statistic']:.3f}, p = {row['P_value']:.4f}, Effect Size = {row['Effect_Size']:.3f}")

print("\n" + "="*80)
print("5. POST-HOC ANALYSIS: Tukey's HSD Test")
print("="*80)

# Perform Tukey's HSD for the most significant result if any
if len(results_df) > 0 and results_df['Significant'].any():
    most_sig = results_df.loc[results_df['P_value'].idxmin()]
    indep_var = most_sig['Independent_Variable']
    dep_var = most_sig['Dependent_Variable']
    
    print(f"📊 Post-hoc analysis for: {indep_var} → {dep_var}")
    print(f"   (Most significant result: p = {most_sig['P_value']:.4f})")
    
    try:
        # Prepare data for Tukey's test
        tukey_data = df[[indep_var, dep_var]].dropna()
        tukey_result = pairwise_tukeyhsd(tukey_data[dep_var], tukey_data[indep_var], alpha=0.05)
        
        print(f"\n🔍 Tukey's HSD Results:")
        print(tukey_result)
        
    except Exception as e:
        print(f"⚠️  Tukey's HSD error: {e}")

print("\n" + "="*80)
print("6. ASSUMPTIONS CHECK")
print("="*80)

print("📊 Checking ANOVA Assumptions:")

# Check normality for key variables
key_vars = ['WiFi_Speed_Score', 'Productivity_Influence_Score', 'Task_Abandonment_Score']
print(f"\n🔍 Normality Check (Shapiro-Wilk test):")
for var in key_vars:
    stat, p_value = stats.shapiro(df[var])
    normal = "✅ Normal" if p_value > 0.05 else "❌ Not Normal"
    print(f"   {var}: W = {stat:.4f}, p = {p_value:.4f} ({normal})")

# Check homogeneity of variance
print(f"\n🔍 Homogeneity of Variance (Levene's test):")
try:
    groups = [df[df['WiFi_Speed_Score'] == speed]['Productivity_Influence_Score'].values 
              for speed in sorted(df['WiFi_Speed_Score'].unique())]
    groups = [g for g in groups if len(g) > 0]
    
    if len(groups) >= 2:
        stat, p_value = stats.levene(*groups)
        homogeneous = "✅ Homogeneous" if p_value > 0.05 else "❌ Not Homogeneous"
        print(f"   WiFi Speed groups: W = {stat:.4f}, p = {p_value:.4f} ({homogeneous})")
except Exception as e:
    print(f"   ⚠️  Levene's test error: {e}")

print(f"\n✅ ANOVA ANALYSIS COMPLETE!")
print(f"📁 Results saved to variables for further analysis")
print(f"📊 Use the results to interpret the relationships in your data")

# Save results to CSV
if len(results_df) > 0:
    results_df.to_csv("anova_results.csv", index=False)
    print(f"💾 Detailed results saved to: anova_results.csv")
