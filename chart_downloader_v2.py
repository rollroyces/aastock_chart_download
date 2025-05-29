from flask import Flask, request, send_file, render_template_string, flash, redirect, url_for
import urllib.request
from urllib.parse import urlencode
import os
import re

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for flash messages

def validate_stock_number(stock_number):
    """Validate and format the stock number to five digits with .HK suffix."""
    try:
        stock_num = int(stock_number)
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
    query_string = urlencode(params)
    return f"{base_url}?{query_string}"

def download_chart_image(stock_id, output_dir="/output"):
    """Download the chart image for the given stock ID."""
    chart_url = construct_chart_url(stock_id)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    stock_number = stock_id.split('.')[0].lstrip('0')
    output_filename = os.path.join(output_dir, f"stock_chart_{stock_number}.png")
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        request = urllib.request.Request(chart_url, headers=headers)
        with urllib.request.urlopen(request) as response:
            if response.getcode() == 200:
                with open(output_filename, 'wb') as f:
                    f.write(response.read())
                return output_filename, None
            else:
                return None, f"Failed to download image. HTTP status code: {response.getcode()}"
    except Exception as e:
        return None, f"Error downloading chart image: {str(e)}"

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Stock Chart Downloader</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }
        h1 { color: #333; }
        .form-container { max-width: 400px; margin: 20px 0; }
        input[type=text] { padding: 10px; width: 200px; margin-right: 10px; }
        input[type=submit] { padding: 10px 20px; background-color: #1E88E5; color: white; border: none; cursor: pointer; }
        input[type=submit]:hover { background-color: #1565C0; }
        .error { color: red; margin-top: 10px; }
        .success { color: green; margin-top: 10px; }
        img { max-width: 100%; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>Stock Chart Downloader</h1>
    <div class="form-container">
        <form method="POST" action="{{ url_for('download') }}">
            <input type="text" name="stock_number" placeholder="Enter stock number (e.g., 2883)" required>
            <input type="submit" value="Get Chart">
        </form>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <p class="{{ category }}">{{ message }}</p>
                {% endfor %}
            {% endif %}
        {% endwith %}
        {% if image_filename %}
            <h2>Chart for Stock {{ stock_number }}</h2>
            <img src="{{ url_for('serve_image', filename=image_filename) }}" alt="Stock Chart">
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template_string(HTML_TEMPLATE, image_filename=None, stock_number=None)

@app.route('/download', methods=['POST'])
def download():
    stock_number = request.form.get('stock_number')
    try:
        stock_id = validate_stock_number(stock_number)
        image_path, error = download_chart_image(stock_id)
        if image_path:
            image_filename = os.path.basename(image_path)  # Extract filename
            flash(f"Chart downloaded as '{image_filename}'", "success")
            return render_template_string(HTML_TEMPLATE, image_filename=image_filename, stock_number=stock_number)
        else:
            flash(error, "error")
            return redirect(url_for('index'))
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", "error")
        return redirect(url_for('index'))

@app.route('/output/<filename>')
def serve_image(filename):
    return send_file(os.path.join('/output', filename), mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
