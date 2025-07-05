#!/usr/bin/env python3
"""
Visualization of ANOVA Results for IIT Internet Connectivity Study
Creates comprehensive visualizations of the ANOVA analysis findings
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def create_anova_visualizations():
    """Create comprehensive visualizations of ANOVA results"""
    
    # Load the data
    print("📊 Loading ANOVA results and dataset...")
    data = pd.read_csv('comprehensive_anova_data.csv')
    anova_results = pd.read_csv('anova_results.csv')
    
    # Set up the plotting style
    plt.style.use('seaborn-v0_8')
    fig = plt.figure(figsize=(20, 15))
    
    # 1. ANOVA Results Summary (Effect Sizes and Significance)
    ax1 = plt.subplot(3, 3, 1)
    
    # Prepare data for plotting
    anova_results['Variable_Pair'] = anova_results['Independent_Variable'] + '\n→ ' + anova_results['Dependent_Variable']
    anova_results['Log_P_Value'] = -np.log10(anova_results['P_value'])
    
    # Create scatter plot of effect size vs significance
    colors = ['red' if sig else 'gray' for sig in anova_results['Significant']]
    scatter = ax1.scatter(anova_results['Effect_Size'], anova_results['Log_P_Value'], 
                         c=colors, s=100, alpha=0.7)
    
    # Add significance line
    ax1.axhline(y=-np.log10(0.05), color='blue', linestyle='--', alpha=0.5, label='p=0.05 threshold')
    
    # Annotate significant points
    for i, row in anova_results.iterrows():
        if row['Significant']:
            ax1.annotate(f"{i+1}", (row['Effect_Size'], row['Log_P_Value']), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    ax1.set_xlabel('Effect Size (η²)')
    ax1.set_ylabel('-log₁₀(p-value)')
    ax1.set_title('ANOVA Results: Effect Size vs Significance')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. WiFi Speed vs Task Abandonment (Most Significant Result)
    ax2 = plt.subplot(3, 3, 2)
    
    # Create box plot for the most significant finding
    wifi_groups = {1: 'Very Poor', 2: 'Poor', 3: 'Average', 4: 'Good'}
    data['WiFi_Category'] = data['WiFi_Speed_Score'].map(wifi_groups)
    
    sns.boxplot(data=data, x='WiFi_Category', y='Task_Abandonment_Score', ax=ax2)
    ax2.set_title('WiFi Speed → Task Abandonment\n(F=22.45, p<0.001)')
    ax2.set_ylabel('Task Abandonment Score')
    ax2.set_xlabel('WiFi Speed Category')
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
    
    # 3. WiFi Speed vs Time Lost (Second Most Significant)
    ax3 = plt.subplot(3, 3, 3)
    
    sns.boxplot(data=data, x='WiFi_Category', y='Time_Lost_Score', ax=ax3)
    ax3.set_title('WiFi Speed → Time Lost\n(F=8.03, p=0.001)')
    ax3.set_ylabel('Time Lost Score')
    ax3.set_xlabel('WiFi Speed Category')
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
    
    # 4. Effect Sizes Bar Chart
    ax4 = plt.subplot(3, 3, 4)
    
    # Sort by effect size
    sorted_results = anova_results.sort_values('Effect_Size', ascending=True)
    y_pos = np.arange(len(sorted_results))
    
    bars = ax4.barh(y_pos, sorted_results['Effect_Size'], 
                   color=['red' if sig else 'gray' for sig in sorted_results['Significant']])
    
    ax4.set_yticks(y_pos)
    ax4.set_yticklabels([f"{row['Independent_Variable'][:8]}→{row['Dependent_Variable'][:8]}" 
                        for _, row in sorted_results.iterrows()], fontsize=8)
    ax4.set_xlabel('Effect Size (η²)')
    ax4.set_title('Effect Sizes by Variable Pair')
    ax4.grid(True, alpha=0.3, axis='x')
    
    # Add effect size interpretation lines
    ax4.axvline(x=0.01, color='green', linestyle=':', alpha=0.5, label='Small (0.01)')
    ax4.axvline(x=0.06, color='orange', linestyle=':', alpha=0.5, label='Medium (0.06)')
    ax4.axvline(x=0.14, color='red', linestyle=':', alpha=0.5, label='Large (0.14)')
    ax4.legend(loc='lower right', fontsize=8)
    
    # 5. Correlation Heatmap of Key Variables
    ax5 = plt.subplot(3, 3, 5)
    
    key_vars = ['WiFi_Speed_Score', 'Reliability_Score', 'Peak_Performance_Score', 
                'Task_Abandonment_Score', 'Time_Lost_Score', 'Productivity_Influence_Score']
    corr_matrix = data[key_vars].corr()
    
    sns.heatmap(corr_matrix, annot=True, cmap='RdBu_r', center=0, 
                square=True, ax=ax5, cbar_kws={'shrink': 0.8})
    ax5.set_title('Correlation Matrix\n(Key Variables)')
    plt.setp(ax5.xaxis.get_majorticklabels(), rotation=45, ha='right')
    plt.setp(ax5.yaxis.get_majorticklabels(), rotation=0)
    
    # 6. Distribution of WiFi Speed Scores
    ax6 = plt.subplot(3, 3, 6)
    
    counts = data['WiFi_Speed_Score'].value_counts().sort_index()
    ax6.bar(counts.index, counts.values, color='skyblue', alpha=0.7)
    ax6.set_xlabel('WiFi Speed Score')
    ax6.set_ylabel('Number of Students')
    ax6.set_title('Distribution of WiFi Speed Ratings')
    ax6.set_xticks([1, 2, 3, 4])
    ax6.set_xticklabels(['Very Poor', 'Poor', 'Average', 'Good'])
    
    # Add count labels on bars
    for i, v in enumerate(counts.values):
        ax6.text(counts.index[i], v + 0.1, str(v), ha='center', va='bottom')
    
    # 7. Peak Performance vs Issues Scatter
    ax7 = plt.subplot(3, 3, 7)
    
    ax7.scatter(data['Peak_Performance_Score'], data['Task_Abandonment_Score'], 
               color='red', alpha=0.6, label='Task Abandonment')
    ax7.scatter(data['Peak_Performance_Score'], data['Time_Lost_Score'], 
               color='blue', alpha=0.6, label='Time Lost')
    
    ax7.set_xlabel('Peak Performance Score')
    ax7.set_ylabel('Issue Score')
    ax7.set_title('Peak Performance vs Performance Issues')
    ax7.legend()
    ax7.grid(True, alpha=0.3)
    
    # 8. F-Statistics Comparison
    ax8 = plt.subplot(3, 3, 8)
    
    f_stats = anova_results['F_statistic'].values
    labels = [f"{row['Independent_Variable'][:8]}\n→{row['Dependent_Variable'][:8]}" 
              for _, row in anova_results.iterrows()]
    
    bars = ax8.bar(range(len(f_stats)), f_stats, 
                  color=['red' if sig else 'gray' for sig in anova_results['Significant']])
    
    ax8.set_xticks(range(len(f_stats)))
    ax8.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
    ax8.set_ylabel('F-statistic')
    ax8.set_title('F-statistics by Variable Pair')
    ax8.grid(True, alpha=0.3, axis='y')
    
    # Add F-statistic values on bars
    for i, v in enumerate(f_stats):
        ax8.text(i, v + 0.5, f'{v:.1f}', ha='center', va='bottom', fontsize=8)
    
    # 9. Summary Statistics Table
    ax9 = plt.subplot(3, 3, 9)
    ax9.axis('off')
    
    # Create summary text
    total_tests = len(anova_results)
    significant_tests = anova_results['Significant'].sum()
    max_effect = anova_results['Effect_Size'].max()
    min_p_value = anova_results['P_value'].min()
    
    summary_text = f"""ANOVA ANALYSIS SUMMARY

Total Tests Performed: {total_tests}
Significant Results: {significant_tests} ({significant_tests/total_tests*100:.1f}%)

Strongest Effects:
• WiFi Speed → Task Abandonment
  F = 22.45, p < 0.001, η² = 0.53

• WiFi Speed → Time Lost  
  F = 8.03, p = 0.001, η² = 0.29

• Peak Performance → Time Lost
  F = 6.66, p = 0.003, η² = 0.25

Key Findings:
✓ WiFi speed significantly affects 
  task abandonment and time lost

✓ Peak performance during high usage
  impacts productivity issues

✓ Reliability alone shows weaker
  associations with outcomes

Effect Size Interpretation:
Small: η² ≥ 0.01, Medium: η² ≥ 0.06
Large: η² ≥ 0.14
"""
    
    ax9.text(0.05, 0.95, summary_text, transform=ax9.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('anova_results_visualization.png', dpi=300, bbox_inches='tight')
    print("📊 Visualization saved as 'anova_results_visualization.png'")
    
    # Create a detailed results table
    print("\n" + "="*80)
    print("DETAILED ANOVA RESULTS TABLE")
    print("="*80)
    
    for i, row in anova_results.iterrows():
        sig_symbol = "✅" if row['Significant'] else "❌"
        effect_size_interpretation = (
            "Large" if row['Effect_Size'] >= 0.14 else
            "Medium" if row['Effect_Size'] >= 0.06 else
            "Small" if row['Effect_Size'] >= 0.01 else
            "Negligible"
        )
        
        print(f"\n{i+1}. {row['Independent_Variable']} → {row['Dependent_Variable']}")
        print(f"   F-statistic: {row['F_statistic']:.3f}")
        print(f"   P-value: {row['P_value']:.6f}")
        print(f"   Significant: {sig_symbol}")
        print(f"   Effect Size (η²): {row['Effect_Size']:.3f} ({effect_size_interpretation})")
    
    plt.show()
    return anova_results, data

if __name__ == "__main__":
    results, data = create_anova_visualizations()
    print("\n🎉 ANOVA analysis and visualization complete!")
    print("📋 All results saved and visualized successfully!")
