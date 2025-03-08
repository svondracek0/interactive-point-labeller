import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
from plotly import graph_objs as go, express as px
import base64
import io
import json
from logging import getLogger
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = getLogger(__name__)


class InteractivePointLabeller:
    """
    First version of the dash app to annotate points in a scatterplot (meant to be for time series purposes at first
    """
    def __init__(self, x_axis_var: str = "date", y_axis_var: str = "value", annotated_var: str = "outlier",
                 annotation_options: tuple[str] = ("no-outlier", "point", "seasonal"),
                 download_dir: str | None = None, port: int = 8050, host: str = "0.0.0.0"):
        """
        :param x_axis_var: Variable to be plotted on the x-axis
        :param y_axis_var: Variable to be plotted on the y-axis
        :param annotated_var: Name of the variable to be used for annotation. If not present in the original data frame,
            it will be created with the first value in annotation_options
        :param annotation_options: Tuple of strings with the possible values for the annotation variable
        :param download_dir: Directory where the annotated data will be saved
        """
        self.x_axis_var = x_axis_var
        self.y_axis_var = y_axis_var
        self.annotated_var = annotated_var
        self.annotation_options = annotation_options
        self.app = dash.Dash(__name__)
        self.configure_layout()
        self.configure_callbacks()
        self.download_dir = download_dir
        self.port = port
        self.host = host

    def configure_layout(self):
        self.app.layout = html.Div([
            html.H1("Point Highlighter App", style={'textAlign': 'center'}),
            dcc.Upload(
                id='upload-data',
                children=html.Div(['Drag and Drop or ', html.A('Select a CSV File')]),
                style={
                    'width': '50%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'borderAlign': 'center',
                    'margin': '10px'
                },
                multiple=False
            ),
            html.Div(
                dcc.Graph(id='scatter-plot'),
                style={'position': 'sticky', 'top': '0', 'zIndex': '1000', 'backgroundColor': 'white'}
            ),
            html.Button("Download CSV", id="btn-download"),
            dcc.Download(id="download-dataframe-csv"),
            html.Div(id='original-data', style={'display': 'none'}),
            html.Div(id='stored-data', style={'display': 'none'}),
            html.Div(id='file-name', style={'display': 'none'})
        ], style={'backgroundColor': '#fff', 'color': '#000'})

    def configure_callbacks(self):
        @self.app.callback(
            Output('stored-data', 'children'),
            Output('file-name', 'children'),
            Input('upload-data', 'contents'),
            Input('scatter-plot', 'clickData'),
            State('upload-data', 'filename'),
            State('stored-data', 'children')
        )
        def update_data_or_point_label(contents, clickData, filename, data):
            ctx = dash.callback_context

            if not ctx.triggered:
                return json.dumps([]), ""

            trigger = ctx.triggered[0]['prop_id'].split('.')[0]

            if trigger == 'upload-data':
                if contents is None:
                    return json.dumps([]), ""

                content_type, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                df['annotated'] = 0
                if self.annotated_var not in df.columns:
                    df[self.annotated_var] = self.annotation_options[0]
                df[self.annotated_var] = self.annotation_options[0]
                return df.to_json(date_format='iso', orient='split'), filename

            elif trigger == 'scatter-plot':
                if clickData is None or data is None:
                    return data, filename

                try:
                    df = pd.read_json(io.StringIO(data), orient='split')
                except ValueError("Data is not in the correct format"):
                    return data, filename

                point_index = clickData['points'][0]['pointIndex']
                unique_annotations = list(self.annotation_options)

                current_annotation = df.at[point_index, self.annotated_var]
                logger.info(f"Annotated point {point_index} to {current_annotation}")

                df.at[point_index, self.annotated_var] = self.yield_next_element_inifinitely(current_annotation,
                                                                                             unique_annotations)
                df.at[point_index, 'annotated'] = 1
                return df.to_json(date_format='iso', orient='split'), filename

            return json.dumps([]), ""

        @self.app.callback(
            Output('scatter-plot', 'figure'),
            Input('stored-data', 'children'),
            Input('file-name', 'children')
        )
        def update_graph(data, filename):
            if data is None:
                fig = go.Figure()
                fig.update_layout(width=2000, height=1000,
                                  title="Please drag and drop an input file to display the data")
                return fig

            df = pd.read_json(io.StringIO(data), orient='split')

            colors = px.colors.qualitative.Plotly

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=df[self.x_axis_var],
                    y=df[self.y_axis_var],
                    mode='markers',
                    marker_color=df[self.annotated_var].apply(lambda x: colors[self.annotation_options.index(x)]),
                    showlegend=False  # Hide the default legend
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=df[self.x_axis_var],
                    y=df[self.y_axis_var],
                    mode='lines',
                    line=dict(color='black'),
                    opacity=0.5,
                    showlegend=False  # Hide the default legend
                )
            )

            # Manually add legend entries
            for annotation in self.annotation_options:
                fig.add_trace(
                    go.Scatter(
                        x=[None], y=[None],  # Dummy data
                        mode='markers',
                        marker=dict(color=colors[self.annotation_options.index(annotation)]),
                        name=annotation
                    )
                )
            title = filename.replace('.csv',
                                     '') if filename else f"Time series plot with annotated {self.annotated_var}"

            fig.update_layout(
                title=title,
                width=2000,
                height=1000,
                xaxis=dict(minor=dict(ticks="inside", showgrid=True))
            )
            return fig

        @self.app.callback(
            Output("download-dataframe-csv", "data"),
            Input("btn-download", "n_clicks"),
            State('stored-data', 'children'),
            State('file-name', 'children'),
            prevent_initial_call=True
        )
        def download_csv(n_clicks, data, filename):
            if data is None:
                return None

            df = pd.read_json(io.StringIO(data), orient='split')
            filename = f"{filename.replace('.csv', '')}_annotated.csv"
            return dcc.send_data_frame(df.to_csv, filename=f"{filename.replace('.csv', '')}.csv")

    def yield_next_element_inifinitely(self, current_value, values):
        val_index = values.index(current_value)
        return values[(val_index + 1) % len(values)]

    def run(self):
        self.app.run_server(debug=True, port=self.port, host=self.host)
