import requests

url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=TSLA&apikey=PJXZ8C7APWZ5VBLO' #use random ticker in order to constantly update end date to be latest date 
response = requests.get(url)
data = response.json()
end_date = data['Meta Data']['3. Last Refreshed']
print(end_date)