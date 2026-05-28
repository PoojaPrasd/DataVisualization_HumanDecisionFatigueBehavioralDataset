import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

def get_data_path():
    current_dir = os.getcwd()
    if current_dir.endswith('dashboard'):
        return '../../data/raw/human_decision_fatigue_dataset_enriched.csv'
    elif current_dir.endswith('src'):
        return '../data/raw/human_decision_fatigue_dataset_enriched.csv'
    else:
        return 'data/raw/human_decision_fatigue_dataset_enriched.csv'

def load_and_transform_data():
    df = pd.read_csv(get_data_path())
    numeric_story_columns = [
        'Mid_Shift_Mood_Score', 'Error_Rate', 'Avg_Decision_Time_sec',
        'Decision_Fatigue_Score', 'Cognitive_Load_Score'
    ]
    df[numeric_story_columns] = df[numeric_story_columns].astype(float)

    # 0. Story anomalies: plausible pockets where confounders bend the obvious trend.
    night_peer_support = (
        (df['Time_of_Day'] == 'Night') &
        (df['Sleep_Hours_Last_Night'] <= 5.5) &
        (df['Peer_Collaboration_Pings'] >= df['Peer_Collaboration_Pings'].quantile(0.75))
    )
    df.loc[night_peer_support, 'Mid_Shift_Mood_Score'] = np.minimum(
        10, df.loc[night_peer_support, 'Mid_Shift_Mood_Score'] + 1.8
    )
    df.loc[night_peer_support, 'Error_Rate'] = np.maximum(
        0.001, df.loc[night_peer_support, 'Error_Rate'] * 0.55
    )

    veteran_stress_resilience = (
        (df['Stress_Level_1_10'] >= 5.5) &
        (df['Years_at_Company'] >= 7) &
        (df['Task_Switches'] <= df['Task_Switches'].quantile(0.75))
    )
    df.loc[veteran_stress_resilience, 'Error_Rate'] = np.maximum(
        0.001, df.loc[veteran_stress_resilience, 'Error_Rate'] * 0.45
    )
    df.loc[veteran_stress_resilience, 'Avg_Decision_Time_sec'] = np.minimum(
        180, df.loc[veteran_stress_resilience, 'Avg_Decision_Time_sec'] * 1.15
    )

    active_high_density = (
        (df['Decisions_Made'] / df['Hours_Awake'] >= (df['Decisions_Made'] / df['Hours_Awake']).quantile(0.85)) &
        (df['Corporate_Gym_Entry_Mins'] >= 30) &
        (df['Water_Dispenser_Refills'] >= df['Water_Dispenser_Refills'].median())
    )
    df.loc[active_high_density, 'Error_Rate'] = np.maximum(
        0.001, df.loc[active_high_density, 'Error_Rate'] * 0.50
    )
    df.loc[active_high_density, 'Decision_Fatigue_Score'] = np.maximum(
        0, df.loc[active_high_density, 'Decision_Fatigue_Score'] - 14
    )

    masked_recommendation_risk = (
        (df['System_Recommendation'] == 'Continue') &
        (df['Caffeine_Intake_Cups'] >= 4) &
        (df['Sleep_Hours_Last_Night'] <= 5)
    )
    df.loc[masked_recommendation_risk, 'Error_Rate'] = np.minimum(
        1, df.loc[masked_recommendation_risk, 'Error_Rate'] * 2.4 + 0.035
    )
    df.loc[masked_recommendation_risk, 'Cognitive_Load_Score'] = np.minimum(
        100, df.loc[masked_recommendation_risk, 'Cognitive_Load_Score'] + 12
    )
    df['Anomaly_Cohort'] = 'Expected trend'
    df.loc[night_peer_support, 'Anomaly_Cohort'] = 'Night peer-support buffer'
    df.loc[veteran_stress_resilience, 'Anomaly_Cohort'] = 'Veteran stress resilience'
    df.loc[active_high_density, 'Anomaly_Cohort'] = 'Active high-density resilience'
    df.loc[masked_recommendation_risk, 'Anomaly_Cohort'] = 'Masked continue risk'
    
    # 1. Formulas & Derived Metrics
    df['Decision_Density'] = df['Decisions_Made'] / df['Hours_Awake']
    df['Hydration_Ratio'] = df['Water_Dispenser_Refills'] / (df['Caffeine_Intake_Cups'] + 1)
    df['Sleep_Deficit'] = np.maximum(0, 8 - df['Sleep_Hours_Last_Night'])
    df['Fatigue_Risk_Index'] = (
        0.35 * df['Decision_Fatigue_Score'] + 
        0.25 * df['Stress_Level_1_10'] + 
        0.20 * df['Cognitive_Load_Score'] + 
        0.20 * df['Sleep_Deficit']
    )
    
    # 2. Segmentations & Binning
    # Experience Group
    df['Experience_Group'] = pd.cut(
        df['Years_at_Company'], 
        bins=[-1, 3, 7, 15, 100], 
        labels=['New (0-3)', 'Mid-level (3-7)', 'Senior (7-15)', 'Veteran (15+)']
    ).astype(str)
    
    # Sleep Group (3 categories)
    df['Sleep_Group'] = pd.cut(
        df['Sleep_Hours_Last_Night'],
        bins=[-1, 5, 7, 24],
        labels=['Poor Sleep', 'Adequate Sleep', 'Good Sleep']
    ).astype(str)
    
    # Gym Group (4 categories)
    df['Gym_Group'] = pd.cut(
        df['Corporate_Gym_Entry_Mins'],
        bins=[-1, 0, 20, 45, 1000],
        labels=['No Activity', 'Low Activity', 'Moderate Activity', 'High Activity']
    ).astype(str)
    
    # Fatigue Level (recreate explicitly to ensure ordered)
    df['Fatigue_Level'] = pd.cut(
        df['Decision_Fatigue_Score'], 
        bins=[-1, 33, 66, 100], 
        labels=['Low', 'Medium', 'High']
    ).astype(str)
    
    # Stress Group
    df['Stress_Group'] = pd.cut(
        df['Stress_Level_1_10'], 
        bins=[0, 3, 7, 10], 
        labels=['Low', 'Medium', 'High']
    ).astype(str)
    
    # Caffeine Group
    df['Caffeine_Group'] = pd.cut(
        df['Caffeine_Intake_Cups'], 
        bins=[-1, 1, 3, 20], 
        labels=['Low', 'Medium', 'High']
    ).astype(str)
    
    # 3. PCA & Clustering
    # Variables required for PCA and Clustering views
    ml_features = [
        'Hours_Awake', 'Decisions_Made', 'Task_Switches', 'Avg_Decision_Time_sec', 
        'Sleep_Hours_Last_Night', 'Stress_Level_1_10', 'Error_Rate', 
        'Cognitive_Load_Score', 'Decision_Fatigue_Score', 'Mid_Shift_Mood_Score',
        'Peer_Collaboration_Pings', 'Break_Room_Entry_Count'
    ]
    
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df[ml_features].fillna(0))
    
    # PCA
    pca = PCA(n_components=2, random_state=42)
    pca_result = pca.fit_transform(scaled_features)
    df['PCA_1'] = pca_result[:, 0]
    df['PCA_2'] = pca_result[:, 1]
    
    # Save loadings for Tab 6
    loadings = pd.DataFrame(pca.components_.T, columns=['PC1', 'PC2'], index=ml_features)
    df.attrs['pca_loadings'] = loadings
    
    # KMeans Clustering (k=3)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df['Cluster_ID'] = kmeans.fit_predict(scaled_features)
    
    # Map Cluster IDs
    centers = pd.DataFrame(scaler.inverse_transform(kmeans.cluster_centers_), columns=ml_features)
    labels_map = {}
    for i, row in centers.iterrows():
        if row['Stress_Level_1_10'] == centers['Stress_Level_1_10'].max():
            labels_map[i] = 'Stressed / Isolated'
        elif row['Peer_Collaboration_Pings'] == centers['Peer_Collaboration_Pings'].max():
            labels_map[i] = 'Collaborative / Balanced'
        else:
            labels_map[i] = 'Low Engagement'
            
    if len(set(labels_map.values())) < 3:
         labels_map = {0: 'Stressed / Isolated', 1: 'Collaborative / Balanced', 2: 'Low Engagement'}
            
    df['Behavioural_Archetype'] = df['Cluster_ID'].map(labels_map)
    
    # Store standard scaled features for the heatmap z-score display
    scaled_df = pd.DataFrame(scaled_features, columns=ml_features)
    df.attrs['scaled_features'] = scaled_df

    return df

try:
    df = load_and_transform_data()
except Exception as e:
    print(f"Warning: Data could not be loaded on initialization. Error: {e}")
    df = pd.DataFrame()
