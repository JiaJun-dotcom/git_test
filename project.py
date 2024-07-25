from project import Flask, jsonify, request
import pandas as pd

app = Flask(__name__)

# Read Nasdaq listed symbols file into a DataFrame
nasdaq_file = "nasdaqlisted.txt"
nasdaq_df = pd.read_csv(nasdaq_file, delimiter="|")

# Read Other listed symbols file into a DataFrame
other_file = "otherlisted.txt"
other_df = pd.read_csv(other_file, delimiter="|")

# Extract symbols from the dataframes
nasdaq_symbols = nasdaq_df["Symbol"].tolist()
other_symbols = other_df["ACT Symbol"].tolist()  
stock_symbols = pd.concat([nasdaq_symbols, other_symbols], ignore_index=True)

@app.route('/analyze', methods=['GET'])
def analyze():
    stock_symbol = request.args.get('stock-symbol')
    if stock_symbol in stock_symbols:
        # Implement your analysis logic here(here must have code from your AI MODEL that returns results of the predictive modelling done by your AI model to predict upcoming closing prices or buy/sell signals!)
        #should return an 'analysis' column or something so ur data in json format in your scripts.js can extract these analysis data
        analysis_result = f"Analysis result for {stock_symbol}" 
#Example analysis format: Upcoming price likely to rise/fall to a predicted closing price of ..., advise to buy/sell/hold/depend on investor.
        return jsonify({'analysis': analysis_result})
    else:
        return jsonify({'analysis': 'Stock symbol not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)