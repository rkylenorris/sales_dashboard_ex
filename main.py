# imports
import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# Load data
file_path = 'data/US_Regional_Sales_Data.csv'
sales_data = pd.read_csv(file_path)

# Data cleaning and type conversions
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
    # title and date range display
    html.Div([
        html.H1("Sales Dashboard", className="text-center text-primary my-4"),
        html.H3(f"{sales_data['OrderDate'].min().strftime('%B %d, %Y')} - {sales_data['OrderDate'].max().strftime('%B %d, %Y')}", className="text-center text-secondary", id="date-range-display"),
    ], className="container"),
    
    # KPI Section
    html.Div([
        html.H2("Key Performance Indicators", className="text-center my-4"),
    html.Div([
        html.Div([
            html.Div([
                html.H3("Total Sales", className="text-info"),
                html.H4(f"${sales_data['Total Sales'].sum():,.2f}", className="text-success", id='kpi-total-sales')
            ], className="card p-3 shadow-sm ")
        ], className="col-md-2"),
        
        html.Div([
            html.Div([
                html.H3("Total Orders", className="text-info"),
                html.H4(f"{sales_data['OrderNumber'].nunique()}", className="text-success", id='kpi-total-orders')
            ], className="card p-3 shadow-sm")
        ], className="col-md-2"),
        
        html.Div([
            html.Div([
                html.H3("Average Discount", className="text-info"),
                html.H4(f"{sales_data['Discount Applied'].mean() * 100:.2f}%", className="text-success", id='kpi-average-discount')
            ], className="card p-3 shadow-sm")
        ], className="col-md-2"),
        
        html.Div([
            html.Div([
                html.H3("Average Unit Price", className="text-info"),
                html.H4(f"${sales_data['Unit Price'].mean():,.2f}", className="text-success", id='kpi-average-unit-price')
            ], className="card p-3 shadow-sm")
        ], className="col-md-2"),
        html.Div([
            html.H3("Avg. Sales per Order", className="text-primary"),
            html.H4(id='kpi-average-sales-per-order', className="text-success")
        ], className="col-md-3 card p-3 shadow-sm"),
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
], className="container-fluid bg-light")


# Callbacks for interactivity
@app.callback(
    [Output('kpi-total-sales', 'children'),
     Output('kpi-total-orders', 'children'),
     Output('kpi-average-discount', 'children'),
     Output('kpi-average-unit-price', 'children'),
     Output('kpi-average-sales-per-order', 'children'),
     Output('sales-over-time', 'figure'),
     Output('sales-by-channel', 'figure'),
     Output('sales-by-warehouse', 'figure'),
     Output('date-range-display', 'children')],
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date'),
     Input('channel-dropdown', 'value'),
     Input('warehouse-dropdown', 'value')]
)
def update_graphs(start_date, end_date, channels, warehouses):
    # check date selected within data range
    if pd.to_datetime(end_date) > sales_data['OrderDate'].max():
        end_date = sales_data['OrderDate'].max()
    if pd.to_datetime(start_date) < sales_data['OrderDate'].min():
        start_date = sales_data['OrderDate'].min()
        
    # Filter data
    filtered_data = sales_data[
        (sales_data['OrderDate'] >= start_date) & (sales_data['OrderDate'] <= end_date)
    ]
    
    # filter based on channels and warehouses if provided
    if channels:
        filtered_data = filtered_data[filtered_data['Sales Channel'].isin(channels)]
    if warehouses:
        filtered_data = filtered_data[filtered_data['WarehouseCode'].isin(warehouses)]
        
    # Recalculate KPIs
    total_sales = f"${filtered_data['Total Sales'].sum():,.2f}"
    total_orders = f"{filtered_data['OrderNumber'].nunique()}"
    average_discount = f"{filtered_data['Discount Applied'].mean() * 100:.2f}%"
    average_unit_price = f"${filtered_data['Unit Price'].mean():,.2f}"
    
    avg_sales_per_order = (
        filtered_data['Total Sales'].sum() / filtered_data['OrderNumber'].nunique()
        if filtered_data['OrderNumber'].nunique() > 0 else 0
    )
    avg_sales_per_order_display = f"${avg_sales_per_order:,.2f}"
    
    # Sales over time figure
    sales_over_time_fig = px.line(
        filtered_data.groupby('OrderDate')['Total Sales'].sum().reset_index(),
        x='OrderDate', y='Total Sales',
        title="Sales Over Time"
    )
    
    # Sales by channel figure
    sales_by_channel_fig = px.pie(
        filtered_data.groupby('Sales Channel')['Total Sales'].sum().reset_index(),
        names='Sales Channel', values='Total Sales',
        title="Sales by Channel"
    )
    
    # Sales by warehouse figure
    sales_by_warehouse_fig = px.bar(
        filtered_data,
        x='WarehouseCode',
        y='Total Sales',
        color='WarehouseCode',  # Add color differentiation by WarehouseCode
        title="Sales by Warehouse",
        labels={'WarehouseCode': 'Warehouse', 'Total Sales': 'Total Sales'},
        text_auto=False # Disable automatic text display on bars
    )
    # Remove x-axis tick labels
    sales_by_warehouse_fig.update_layout(
        xaxis=dict(showticklabels=False)  # Hide the x-axis labels
    )
    
    # udpate date range display based on date filter
    date_range_display = f"{pd.to_datetime(start_date).strftime('%B %d, %Y')} - {pd.to_datetime(end_date).strftime('%B %d, %Y')}"
    
    return total_sales, total_orders, average_discount, average_unit_price, \
           sales_over_time_fig, sales_by_channel_fig, sales_by_warehouse_fig, \
           date_range_display, avg_sales_per_order_display

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
