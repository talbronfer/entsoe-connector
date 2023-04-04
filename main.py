import logging
import pandas as pd
from entsoe import EntsoePandasClient
from datetime import datetime, timedelta
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# Set up logging
logging.basicConfig(filename='entsoe_connector.log', level=logging.INFO)

# Initialize EntsoePandasClient
api_key = "<API_KEY>"
client = EntsoePandasClient(api_key=api_key)

def plot_hourly_electricity_rates(data, country_code):
    # Extract timestamps and values from the data
    timestamps = [datetime.strptime(item["from"], '%d/%m/%Y %H:%M') for item in data]
    values = [item["value"] for item in data]

    # Create the plot
    fig, ax = plt.subplots()
    ax.plot(timestamps, values, marker='o', linestyle='-')
    
    # Set the x-axis to display only hours
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    
    # Set labels and title
    ax.set_xlabel('Time (Hourly Intervals)')
    ax.set_ylabel('Price (EUR per kWh)')
    ax.set_title(f'Hourly Electricity Rates for {country_code}')

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    
    # Adjust plot layout
    fig.tight_layout()

    # Save the plot as an image
    plt.savefig(f'hourly_electricity_rates_{country_code}.png')


def get_hourly_electricity_rates(country_code, start):
    try:
        # Get start and end timestamps for tomorrow
        ##start = pd.Timestamp(datetime.now().date() + timedelta(days=1), tz='Europe/Brussels')
        end = start + timedelta(days=1)

        # Request hourly electricity rates
        hourly_rates = client.query_day_ahead_prices(country_code, start=start, end=end)

        # Convert hourly rates to JSON format
        rates_list = []
        for i, rate in enumerate(hourly_rates):
            rate_kwh = round(rate / 1000, 2)  # Convert from EUR per MWh to EUR per kWh and round to two decimal places
            from_timestamp = (start + timedelta(hours=i)).strftime('%d/%m/%Y %H:%M')
            rates_list.append({"from": from_timestamp, "duration": 60, "value": rate_kwh})
        
        hourly_rates_json = json.dumps(rates_list)

        # Save hourly rates to a JSON file
        with open(f'hourly_electricity_rates_{country_code}.json', 'w') as f:
            f.write(hourly_rates_json)

        logging.info(f'Successfully fetched and saved hourly electricity rates for {country_code}.')

    except Exception as e:
        logging.error(f'Error fetching hourly electricity rates for {country_code}: {str(e)}')

if __name__ == "__main__":
    country_codes = ['AT']
    for country_code in country_codes:
        get_hourly_electricity_rates(country_code, pd.Timestamp(datetime.now().date() - timedelta(days=1), tz='Europe/Brussels'))
        with open(f'hourly_electricity_rates_{country_code}.json', 'r') as f:
            data = json.load(f)
        
        # Plot hourly electricity rates
        plot_hourly_electricity_rates(data, country_code)
