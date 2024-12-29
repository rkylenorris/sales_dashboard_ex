import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# Load and preprocess data (replace with your data file if needed)
file_path = 'data/US_Regional_Sales_Data.csv'
sales_data = pd.read_csv(file_path)

# Data cleaning
date_columns = [
    'ProcuredDate',
    'OrderDate',
    'ShipDate',
    'DeliveryDate',
]
for col in date_columns:
    sales_data[col] = pd.to_datetime(sales_data[col], dayfirst=True, errors='coerce')
    

# Convert currency columns from string to float
sales_data['Unit Cost'] = sales_data['Unit Cost'].replace('[\$,]', '', regex=True).astype(float)
sales_data['Unit Price'] = sales_data['Unit Price'].replace('[\$,]', '', regex=True).astype(float)

# add total sales column
sales_data['Total Sales'] = sales_data['Order Quantity'] * sales_data['Unit Price']

# Dashboard app setup
app = dash.Dash(__name__, external_stylesheets=[
    "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
])

# App layout

app.layout = html.Div([
    html.Div([
        html.H1("Sales Dashboard", className="text-center text-primary my-4")
    ], className="container"),
    
    # KPI Section
    html.Div([
        html.H2("Key Performance Indicators", className="text-center my-4"),
    html.Div([
        html.Div([
            html.Div([
                html.H3("Total Sales", className="text-primary"),
                html.H4(f"${sales_data['Total Sales'].sum():,.2f}", className="text-success")
            ], className="card p-3 shadow-sm ")
        ], className="col-md-2"),
        
        html.Div([
            html.Div([
                html.H3("Total Orders", className="text-primary"),
                html.H4(f"{sales_data['OrderNumber'].nunique()}", className="text-success")
            ], className="card p-3 shadow-sm")
        ], className="col-md-2"),
        
        html.Div([
            html.Div([
                html.H3("Average Discount", className="text-primary"),
                html.H4(f"{sales_data['Discount Applied'].mean() * 100:.2f}%", className="text-success")
            ], className="card p-3 shadow-sm")
        ], className="col-md-2"),
        
        html.Div([
            html.Div([
                html.H3("Average Unit Price", className="text-primary"),
                html.H4(f"${sales_data['Unit Price'].mean():,.2f}", className="text-success")
            ], className="card p-3 shadow-sm")
        ], className="col-md-2"),
    ], className="row justify-content-center gy-4"),
    ], className='container-fluid'),
    
    # Filters Section
    html.Div([html.Hr(className='shadow-sm')], className="container"),
    html.Div([
        html.Div([
            html.Label("Date Range", className="form-label"),
            dcc.DatePickerRange(
                id='date-picker',
                start_date=sales_data['OrderDate'].min(),
                end_date=sales_data['OrderDate'].max(),
                className="form-control"
            ),
        ], className="col-md-auto mb-3 center"),
        
        html.Div([
            html.Label("Sales Channel", className="form-label"),
            dcc.Dropdown(
                id='channel-dropdown',
                options=[{'label': ch, 'value': ch} for ch in sales_data['Sales Channel'].unique()],
                multi=True,
                placeholder="Select Sales Channel",
                className="form-select"
            )
        ], className="col-md-auto mb-3 center"),
        
        html.Div([
            html.Label("Warehouse", className="form-label"),
            dcc.Dropdown(
                id='warehouse-dropdown',
                options=[{'label': wh, 'value': wh} for wh in sales_data['WarehouseCode'].unique()],
                multi=True,
                placeholder="Select Warehouse",
                className="form-select"
            )
        ], className="col-md-auto mb-3 center")
    ], className="container center"),

    # Graphs Section
    html.Div([
        html.H2("Sales Visualizations", className="text-center my-4"),
        html.Div([
            dcc.Graph(id='sales-over-time', className="shadow-lg")
        ], className="col-lg-auto mb-4"),
        
        html.Div([
        html.Div([
            dcc.Graph(id='sales-by-channel', className="shadow-lg")
        ], className="col-md-5 mb-4"),
        
        html.Div([
            dcc.Graph(id='sales-by-warehouse', className="shadow-lg")
        ], className="col-md-5 mb-4")
        ], className="row container justify-content-center"),
        
    ], className="container center")
], className="container-fluid")


# Callbacks for interactivity
@app.callback(
    [Output('sales-over-time', 'figure'),
     Output('sales-by-channel', 'figure'),
     Output('sales-by-warehouse', 'figure')],
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date'),
     Input('channel-dropdown', 'value'),
     Input('warehouse-dropdown', 'value')]
)
def update_graphs(start_date, end_date, channels, warehouses):
    filtered_data = sales_data[
        (sales_data['OrderDate'] >= start_date) & (sales_data['OrderDate'] <= end_date)
    ]
    if channels:
        filtered_data = filtered_data[filtered_data['Sales Channel'].isin(channels)]
    if warehouses:
        filtered_data = filtered_data[filtered_data['WarehouseCode'].isin(warehouses)]
    
    # Sales over time
    sales_over_time_fig = px.line(
        filtered_data.groupby('OrderDate')['Total Sales'].sum().reset_index(),
        x='OrderDate', y='Total Sales',
        title="Sales Over Time"
    )
    
    # Sales by channel
    sales_by_channel_fig = px.pie(
        filtered_data.groupby('Sales Channel')['Total Sales'].sum().reset_index(),
        names='Sales Channel', values='Total Sales',
        title="Sales by Channel"
    )
    
    # Sales by warehouse
    sales_by_warehouse_fig = px.bar(
        filtered_data.groupby('WarehouseCode')['Total Sales'].sum().reset_index(),
        x='WarehouseCode', y='Total Sales',
        title="Sales by Warehouse"
    )
    
    return sales_over_time_fig, sales_by_channel_fig, sales_by_warehouse_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
