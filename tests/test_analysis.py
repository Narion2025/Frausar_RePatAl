import pytest
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.analysis.core import analyze_monthly_scores

@pytest.fixture
def sample_chat_df():
    data = [
        {'timestamp': datetime(2024, 1, 10), 'author': 'Ben', 'message': 'Das ist gut.'},
        {'timestamp': datetime(2024, 1, 20), 'author': 'Zoe', 'message': 'Das ist ein Problem.'},
        {'timestamp': datetime(2024, 2, 5), 'author': 'Ben', 'message': 'Nochmal danke!'},
        {'timestamp': datetime(2024, 2, 15), 'author': 'Zoe', 'message': 'Das ist schlecht.'},
        {'timestamp': datetime(2024, 3, 1), 'author': 'Ben', 'message': 'Nichts relevantes.'}
    ]
    return pd.DataFrame(data)

@pytest.fixture
def sample_markers_config():
    return {
        'markers': {
            'positive': {'keywords': ['gut', 'danke'], 'score': 1},
            'negative': {'keywords': ['schlecht', 'problem'], 'score': -2}
        }
    }

def test_analyze_monthly_scores_by_author(sample_chat_df, sample_markers_config):
    result_df = analyze_monthly_scores(sample_chat_df, sample_markers_config)
    assert 'author' in result_df.columns
    
    ben_scores = result_df[result_df['author'] == 'Ben'].set_index('month')['score'].to_dict()
    zoe_scores = result_df[result_df['author'] == 'Zoe'].set_index('month')['score'].to_dict()

    expected_ben = {pd.Timestamp('2024-01-01'): 1, pd.Timestamp('2024-02-01'): 1}
    expected_zoe = {pd.Timestamp('2024-01-01'): -2, pd.Timestamp('2024-02-01'): -2}
    
    assert ben_scores == expected_ben
    assert zoe_scores == expected_zoe

def test_analyze_with_empty_dataframe():
    empty_df = pd.DataFrame(columns=['timestamp', 'author', 'message'])
    markers = {'markers': {'test': {'keywords': ['a'], 'score': 1}}}
    result = analyze_monthly_scores(empty_df, markers)
    assert result.empty 