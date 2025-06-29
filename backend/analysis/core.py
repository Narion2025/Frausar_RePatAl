import pandas as pd
from typing import Dict, Any

def analyze_monthly_scores(chat_df: pd.DataFrame, markers_config: Dict[str, Any]) -> pd.DataFrame:
    """
    Analysiert den Chatverlauf auf Basis von Markern und aggregiert die Scores 
    pro Autor und pro Monat.

    Args:
        chat_df: DataFrame mit den Chat-Daten ('timestamp', 'author', 'message').
        markers_config: Dictionary mit der Marker-Konfiguration.

    Returns:
        Ein DataFrame mit den monatlichen Scores, aufgeschlüsselt nach Autor
        ('month', 'author', 'score').
    """
    if chat_df.empty:
        return pd.DataFrame(columns=['month', 'author', 'score'])

    df = chat_df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    df['month'] = df['timestamp'].dt.to_period('M')

    scores = []
    marker_definitions = markers_config.get('markers', {})

    for _, row in df.iterrows():
        message_score = 0
        for marker_name, marker_data in marker_definitions.items():
            keywords = marker_data.get('keywords', [])
            score_value = marker_data.get('score', 0)
            
            for keyword in keywords:
                if keyword.lower() in row['message'].lower():
                    message_score += score_value
        scores.append(message_score)
    
    df['score'] = scores

    # Nach Monat UND Autor gruppieren und die Scores summieren
    author_monthly_scores = df.groupby(['month', 'author'])['score'].sum().reset_index()
    
    # Filtern von Einträgen mit Score 0, um die Datenmenge zu reduzieren
    author_monthly_scores = author_monthly_scores[author_monthly_scores['score'] != 0]

    if not author_monthly_scores.empty:
        author_monthly_scores['month'] = author_monthly_scores['month'].dt.to_timestamp()

    return author_monthly_scores 