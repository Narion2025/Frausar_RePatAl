import pytest
import pandas as pd
import yaml
import sys
import os
import io

# Fügt das Projektverzeichnis zum Python-Pfad hinzu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.data_import.readers import load_yaml_markers, load_chat_log_from_txt

@pytest.fixture
def temp_marker_file(tmp_path):
    content = {'markers': {'positive': {'keywords': ['gut'], 'score': 1}}}
    file_path = tmp_path / "markers.yaml"
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(content, f)
    return str(file_path)

@pytest.fixture
def temp_chat_file(tmp_path):
    content = "[01.01.24, 10:00:00] User1: Das war gut.\n"
    file_path = tmp_path / "chat.txt"
    file_path.write_text(content, encoding='utf-8')
    return str(file_path)

def test_load_yaml_markers_success(temp_marker_file):
    markers = load_yaml_markers(temp_marker_file)
    assert 'markers' in markers
    assert 'positive' in markers['markers']

def test_load_chat_log_from_txt_file_success(temp_chat_file):
    df = load_chat_log_from_txt(temp_chat_file)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.iloc[0]['author'] == 'User1'

def test_load_chat_log_from_stream_success():
    content = "[01.01.24, 10:00:00] User1: Stream-Test.\n"
    stream = io.StringIO(content)
    df = load_chat_log_from_txt(stream)
    assert len(df) == 1
    assert df.iloc[0]['author'] == 'User1'

def test_load_non_existent_file_raises_error():
    with pytest.raises(FileNotFoundError):
        load_yaml_markers("non_existent_file.yaml")
    with pytest.raises(FileNotFoundError):
        load_chat_log_from_txt("non_existent_file.txt") 