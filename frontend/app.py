import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import base64
import io
import sys
import os

# Fügt das Projektverzeichnis zum Python-Pfad hinzu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.data_import.readers import load_yaml_markers, load_chat_log_from_txt
from backend.analysis.core import analyze_monthly_scores

# --- Dash App-Initialisierung ---
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server
app.title = "Frausar_RePatAl"

# --- Layout der Anwendung ---
app.layout = html.Div([
    html.H1('Frausar_RePatAl: Beziehungsanalyse-Dashboard'),
    html.P('Lade deine Chat-Chronik (.txt) und deine Marker-Definitionen (.yaml) hoch, um die Analyse zu starten.'),
    
    html.Div([
        dcc.Upload(
            id='upload-chat-data',
            children=html.Div(['Chat-Datei (.txt) hierher ziehen oder auswählen']),
            style={
                'width': '48%', 'height': '60px', 'lineHeight': '60px',
                'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                'textAlign': 'center', 'margin': '10px', 'display': 'inline-block'
            },
        ),
        dcc.Upload(
            id='upload-marker-data',
            children=html.Div(['Marker-Datei (.yaml) hierher ziehen oder auswählen']),
            style={
                'width': '48%', 'height': '60px', 'lineHeight': '60px',
                'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                'textAlign': 'center', 'margin': '10px', 'display': 'inline-block'
            },
        )
    ]),
    
    html.Div(id='output-data-upload', children=html.Div(['Bitte lade beide Dateien hoch.']))
])


@app.callback(
    Output('output-data-upload', 'children'),
    [Input('upload-chat-data', 'contents'),
     Input('upload-marker-data', 'contents')],
    [State('upload-chat-data', 'filename'),
     State('upload-marker-data', 'filename')],
    prevent_initial_call=True
)
def update_output(chat_contents, marker_contents, chat_filename, marker_filename):
    if not chat_contents or not marker_contents:
        return html.Div(['Ein oder beide Uploads fehlen. Bitte lade beide Dateien hoch.'])

    try:
        # Chat-Datei verarbeiten
        _, chat_content_string = chat_contents.split(',')
        decoded_chat = base64.b64decode(chat_content_string)
        chat_stream = io.StringIO(decoded_chat.decode('utf-8'))
        chat_df = load_chat_log_from_txt(chat_stream)
        
        # Marker-Datei verarbeiten
        _, marker_content_string = marker_contents.split(',')
        decoded_marker = base64.b64decode(marker_content_string)
        marker_stream = io.StringIO(decoded_marker.decode('utf-8'))
        markers = load_yaml_markers(marker_stream)

    except Exception as e:
        return html.Div([
            f'Beim Verarbeiten der Datei ist ein Fehler aufgetreten: {e}. Stelle sicher, dass das Format korrekt ist.'
        ])

    # Analyse durchführen
    author_monthly_scores_df = analyze_monthly_scores(chat_df, markers)

    if author_monthly_scores_df.empty:
        return html.Div(['Keine der definierten Marker wurden im Text gefunden.'])

    # Gesamt-Score berechnen
    total_monthly_scores_df = author_monthly_scores_df.groupby('month')['score'].sum().reset_index()
    total_monthly_scores_df['author'] = 'Gesamt'
    
    combined_df = pd.concat([author_monthly_scores_df, total_monthly_scores_df], ignore_index=True)

    fig = px.line(
        combined_df, 
        x='month', 
        y='score', 
        color='author',
        title='Monatlicher Beziehungs-Score nach Partner',
        markers=True,
        labels={'month': 'Monat', 'score': 'Score', 'author': 'Partner'}
    )
    fig.update_layout(title_x=0.5)

    return html.Div([
        html.Hr(),
        html.H3(f"Analyse für: {chat_filename} | Marker: {marker_filename}"),
        dcc.Graph(id='relationship-score-graph', figure=fig),
        html.H4("Detail-Daten (pro Partner)"),
        dash_table.DataTable(
            id='analysis-table',
            columns=[{"name": i, "id": i} for i in author_monthly_scores_df.columns],
            data=author_monthly_scores_df.to_dict('records'),
            sort_action="native",
            filter_action="native",
            page_size=10,
        )
    ])


if __name__ == '__main__':
    app.run(debug=True)