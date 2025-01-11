import tkinter as tk
from tkinter import messagebox, scrolledtext
import yfinance as yf
import requests
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np

class StockDetailsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Analyzer with Prediction")
        self.root.geometry("800x700")
        self.root.resizable(False, False)

        # Title Label
        title_label = tk.Label(self.root, text="STOCK'S ANALYZER", font=("Arial", 24, "bold"), fg="gold")
        title_label.pack(pady=10)

        # Stock Symbol Entry
        self.stock_entry = tk.Entry(self.root, font=("Arial", 14), width=40)
        self.stock_entry.insert(0, "Enter company name")
        self.stock_entry.bind("<FocusIn>", lambda event: self.clear_placeholder())
        self.stock_entry.pack(pady=10)

        # Search Button
        search_button = tk.Button(self.root, text="Search", font=("Arial", 14, "bold"), bg="blue", fg="white",
                                  command=self.get_stock_details)
        search_button.pack(pady=10)

        # Predict Button
        predict_button = tk.Button(self.root, text="Predict Future Price", font=("Arial", 14, "bold"), bg="green", fg="white",
                                    command=self.predict_stock_price)
        predict_button.pack(pady=10)

        # Results Section
        self.result_box = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=("Arial", 14), height=20, width=70)
        self.result_box.pack(pady=10)
        self.result_box.config(state=tk.DISABLED)

        # Signature
        signature_label = tk.Label(self.root, text="[ .P.N. ]", font=("Arial", 10, "italic"), fg="gray")
        signature_label.pack(pady=5)

    def clear_placeholder(self):
        if self.stock_entry.get() == "Enter company name":
            self.stock_entry.delete(0, tk.END)

    def get_stock_details(self):
        stock_name = self.stock_entry.get().strip()
        if not stock_name or stock_name == "Enter company name":
            messagebox.showerror("Error", "Please enter a valid company name.")
            return

        stock_name = stock_name.replace(" ", "-") + ".NS"  # Append ".NS" for NSE
        details = self.fetch_stock_details(stock_name)
        self.display_stock_details(details)

    def fetch_stock_details(self, stock_name):
        try:
            # Check internet connection
            response = requests.get("https://google.com")
            if response.status_code != 200:
                return "Error: Unable to connect to the internet. Please check your connection."

            # Fetching stock data
            stock = yf.Ticker(stock_name)
            if not stock:
                return "Stock not found. Please enter a valid company name."

            # Getting fundamental details
            info = stock.info
            company_name = info['longName']
            market_cap = '{:,.2f}'.format(info.get('marketCap', 0)) + " INR"
            pe_ratio = info.get('forwardPE', 0)
            eps = info.get('forwardEps', 0)
            dividend_yield = info.get('dividendYield', 0)
            sector = info.get('sector', 'N/A')
            ev_to_ebitda = info.get('enterpriseToEbitda', 0)
            profit_margin = info.get('profitMargins', 0)
            roe = info.get('returnOnEquity', 0)
            debt_to_equity = info.get('debtToEquity', 0)

            # Constructing details string
            details = (
                f"Company: {company_name}\n"
                f"Market Cap: {market_cap}\n"
                f"P/E Ratio: {pe_ratio}\n"
                f"EPS: {eps}\n"
                f"Dividend Yield: {dividend_yield}\n"
                f"Sector: {sector}\n"
                f"EV/EBITDA: {ev_to_ebitda}\n"
                f"Profit Margin: {profit_margin}\n"
                f"Return on Equity: {roe}\n"
                f"Debt-to-Equity: {debt_to_equity}\n"
            )

            return details
        except requests.exceptions.RequestException as e:
            return f"Error: {str(e)}"

    def display_stock_details(self, details):
        self.result_box.config(state=tk.NORMAL)
        self.result_box.delete(1.0, tk.END)
        self.result_box.insert(tk.END, details)
        self.result_box.config(state=tk.DISABLED)

    def predict_stock_price(self):
        stock_name = self.stock_entry.get().strip()
        if not stock_name or stock_name == "Enter company name":
            messagebox.showerror("Error", "Please enter a valid company name.")
            return

        stock_name = stock_name.replace(" ", "-") + ".NS"
        try:
            stock = yf.Ticker(stock_name)
            hist = stock.history(period="1y")  # Fetch historical data for the last year

            if hist.empty:
                messagebox.showerror("Error", "Unable to fetch stock data for prediction.")
                return

            # Prepare data for training
            hist['Date'] = hist.index
            hist['Days'] = (hist['Date'] - hist['Date'].min()).dt.days
            X = hist[['Days']].values  # Independent variable (Days)
            y = hist['Close'].values  # Dependent variable (Closing price)

            # Train-test split
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Train the model
            model = LinearRegression()
            model.fit(X_train, y_train)

            # Predict the next day's price
            next_day = np.array([[X.max() + 1]])
            predicted_price = model.predict(next_day)[0]

            # Display the prediction
            self.result_box.config(state=tk.NORMAL)
            self.result_box.insert(tk.END, f"\nPredicted Price for the Next Day: {predicted_price:.2f} INR\n")
            self.result_box.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during prediction: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = StockDetailsApp(root)
    root.mainloop()