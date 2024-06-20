from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List
import yfinance as yf
import instructor

company = input("Enter the Company Name :")

class StockInfo(BaseModel):
    company: str = Field(..., description="Name of the company")
    ticker: str = Field(..., description="Ticker symbol of the company")

client = instructor.patch(
    OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="mistral",
    ),
    mode=instructor.Mode.JSON,
)

resp = client.chat.completions.create(
    model="llama2",
    messages=[
        {
            "role": "user",
            "content": f"Return the company name and the ticker symbol of the {company}."
        }
    ],
    response_model=StockInfo,
    max_retries=30
)
print(resp.model_dump_json(indent=2))
stock = yf.Ticker(resp.ticker)
hist = stock.history(period="1d")
stock_price = hist['Close'].iloc[-1]
print(f"The stock price of the {resp.company} is {stock_price}. USD")


import requests
import json
import sys
import yfinance as yf

company_name = company

schema = {
    "company": {
        "type": "string",
        "description": "Name of the company"
    },
    "ticker": {
        "type": "string",
        "description": "Ticker symbol of the company"
    }
}

payload = {
    "model": "llama2",
    "messages": [
        {
            "role": "system",
            "content": f"You are a helpful AI assistant. The user will enter a company name and the assistant will return the ticker symbol and current stock price of the company. Output in JSON using the schema defined here: {json.dumps(schema)}."
        },
        {"role": "user", "content": "Apple"},
        {"role": "assistant", "content": json.dumps({"company": "Apple", "ticker": "AAPL"})},  # Example static data
        {"role": "user", "content": company_name}
    ],
    "format": "json",
    "stream": False
}

response = requests.post("http://localhost:11434/api/chat", json=payload)
company_info = json.loads(response.json()["message"]["content"])

ticker_symbol = company_info['ticker']
stock = yf.Ticker(ticker_symbol)
hist = stock.history(period="1d")
try:
    stock_price = hist['Close'].iloc[-1]
except IndexError:
    stock_price = None 

print(f"The current stock price of {company_info['company']} ({ticker_symbol}) is USD {stock_price}.")
 