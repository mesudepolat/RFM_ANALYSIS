# 1.Data Understanding
import pandas as pd
import datetime as dt
pd.set_option('display.max_rows', 10)
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)
df_ = pd.read_excel("datasets/online_retail_II.xlsx",
                    sheet_name="Year 2010-2011")
df = df_.copy()
df.isnull().sum()
df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False)
df = df[~df["Invoice"].str.contains("C", na=False)]
df["TotalPrice"] = df["Quantity"] * df["Price"]
df.sort_values("Price", ascending=False)
df.groupby("Country").agg({"TotalPrice": "sum"}).sort_values("TotalPrice", ascending=False)


# 2.Data Preparation
df.isnull().sum()
df.dropna(inplace=True)
df.describe([0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]).T


# 3.Calculating RFM Metrics
df["InvoiceDate"].max()

today_date = dt.datetime(2011, 12, 10)

rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,
                                     'Invoice': lambda num: len(num),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})
rfm.columns = ['Recency', 'Frequency', 'Monetary']
rfm = rfm[(rfm["Monetary"] > 0) & (rfm["Frequency"] > 0)]


# 4.Calculating RFM Scores
rfm["RecencyScore"] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
rfm["FrequencyScore"] = pd.qcut(rfm['Frequency'], 5, labels=[1, 2, 3, 4, 5])
rfm["MonetaryScore"] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm["RFM_SCORE"] = (rfm['RecencyScore'].astype(str) +
                    rfm['FrequencyScore'].astype(str) +
                    rfm['MonetaryScore'].astype(str))


# 5.Naming & Analysing RFM Segments
seg_map = {
    r'[1-2][1-2]': 'Hibernating',
    r'[1-2][3-4]': 'At_Risk',
    r'[1-2]5': 'Cant_Loose',
    r'3[1-2]': 'About_to_Sleep',
    r'33': 'Need_Attention',
    r'[3-4][4-5]': 'Loyal_Customers',
    r'41': 'Promising',
    r'51': 'New_Customers',
    r'[4-5][2-3]': 'Potential_Loyalists',
    r'5[4-5]': 'Champions'
}

rfm['Segment'] = rfm['RecencyScore'].astype(str) + rfm['FrequencyScore'].astype(str)
rfm['Segment'] = rfm['Segment'].replace(seg_map, regex=True)

rfm[["Segment", "Recency", "Frequency", "Monetary"]].groupby("Segment").agg({"mean", "count"})
