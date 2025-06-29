import yaml
from typing import Dict, Any
import pandas as pd
import re
from typing import List

def load_yaml_markers(file_path: str) -> Dict[str, Any]:
    """
    Lädt Marker-Definitionen aus einer YAML-Datei.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data if data is not None else {}
    except FileNotFoundError:
        print(f"Fehler: Die Datei unter {file_path} wurde nicht gefunden.")
        raise
    except yaml.YAMLError as e:
        print(f"Fehler beim Parsen der YAML-Datei {file_path}: {e}")
        raise

# Annahme für das Chat-Format: [DD.MM.YY, HH:MM:SS] Author: Message
CHAT_LINE_REGEX = re.compile(r"\[(\d{2}\.\d{2}\.\d{2}, \d{2}:\d{2}:\d{2})\] ([^:]+): (.*)")

def load_chat_log_from_txt(file_path) -> pd.DataFrame:
    """
    Lädt einen Chatverlauf aus einer .txt-Datei oder einem Stream und wandelt ihn in einen DataFrame um.
    """
    if isinstance(file_path, str):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Fehler: Die Datei unter {file_path} wurde nicht gefunden.")
            raise
    else: # StringIO-Objekt
        lines = file_path.readlines()

    chat_data: List[Dict[str, any]] = []
    for line in lines:
        match = CHAT_LINE_REGEX.match(line)
        if match:
            chat_data.append({
                'timestamp': pd.to_datetime(match.group(1), format='%d.%m.%y, %H:%M:%S'),
                'author': match.group(2).strip(),
                'message': match.group(3).strip()
            })
        elif chat_data:
            chat_data[-1]['message'] += "\n" + line.strip()

    if not chat_data:
        return pd.DataFrame(columns=['timestamp', 'author', 'message'])

    return pd.DataFrame(chat_data) 