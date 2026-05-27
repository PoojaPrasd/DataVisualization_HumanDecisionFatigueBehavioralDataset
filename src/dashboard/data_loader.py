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
