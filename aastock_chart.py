import urllib.request
from urllib.parse import urlencode
import re

def validate_stock_number(stock_number):
    """Validate and format the stock number to five digits with .HK suffix."""
    try:
        # Convert to integer to ensure it's a number
        stock_num = int(stock_number)
        # Format to five digits with leading zeros
        formatted_stock = f"{stock_num:05d}.HK"
        return formatted_stock
    except ValueError:
        raise ValueError("Stock number must be a valid integer (e.g., 2883).")

def construct_chart_url(stock_id):
    """Construct the chart image URL for the given stock ID."""
    base_url = "https://charts.aastocks.com/servlet/Charts"
    params = {
        "fontsize": "12",
        "15MinDelay": "T",
        "lang": "1",
        "titlestyle": "1",
        "vol": "1",
        "Indicator": "1",
        "indpara1": "10",
        "indpara2": "20",
        "indpara3": "50",
        "indpara4": "100",
        "indpara5": "150",
        "subChart1": "2",
        "ref1para1": "14",
        "ref1para2": "0",
        "ref1para3": "0",
        "subChart2": "3",
        "ref2para1": "12",
        "ref2para2": "26",
        "ref2para3": "9",
        "subChart3": "12",
        "ref3para1": "0",
        "ref3para2": "0",
        "ref3para3": "0",
        "scheme": "3",
        "com": "100",
        "chartwidth": "870",
        "chartheight": "855",
        "stockid": stock_id,
        "period": "6",
        "type": "1",
        "logoStyle": "1"
    }
    # Encode parameters and construct full URL
    query_string = urlencode(params)
    return f"{base_url}?{query_string}"

def download_chart_image(stock_id, output_filename):
    """Download the chart image for the given stock ID."""
    chart_url = construct_chart_url(stock_id)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        # Create a request with headers
        request = urllib.request.Request(chart_url, headers=headers)
        with urllib.request.urlopen(request) as response:
            if response.getcode() == 200:
                with open(output_filename, 'wb') as f:
                    f.write(response.read())
                print(f"Chart image downloaded as '{output_filename}'")
            else:
                print(f"Failed to download image. HTTP status code: {response.getcode()}")
    except Exception as e:
        print(f"Error downloading chart image: {e}")

def main():
    # Prompt user for stock number
    stock_number = input("Enter the stock number (e.g., 2883): ").strip()
    
    try:
        # Validate and format stock number
        stock_id = validate_stock_number(stock_number)
        # Define output filename
        output_filename = f"stock_chart_{stock_number}.png"
        # Download the chart image
        download_chart_image(stock_id, output_filename)
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
