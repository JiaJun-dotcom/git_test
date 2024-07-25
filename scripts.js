// Function to get URL parameters(in order to retrieve your stock symbol from the list of stock symbols provided in the URL)
function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

// Function to fetch analysis from the server(need to connect to Flask as endpoint)
async function fetchStockAnalysis(symbol) {
    try {
        const response = await fetch(`/analyze?stock-symbol=${symbol}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        document.getElementById('stock-analysis').textContent = data.analysis;
    } catch (error) {
        document.getElementById('stock-analysis').textContent = 'Error fetching analysis: ' + error;
    }
}


// Display the stock symbol and fetch the analysis result
document.addEventListener('DOMContentLoaded', () => {
    const stockSymbol = getUrlParameter('stock-symbol');
    if (stockSymbol) {
        document.getElementById('stock-symbol').textContent = stockSymbol;
        fetchStockAnalysis(stockSymbol);
    }
});
