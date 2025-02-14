import pandas as pd
from scipy import stats
import seaborn as sns
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import kagglehub
from sklearn import linear_model

# Options
pd.set_option("display.max_columns", 999)
pd.set_option("display.max_rows", 999)
# Load database

path = kagglehub.dataset_download("olistbr/brazilian-ecommerce")

print("Path to dataset files:", path)

customers = pd.read_csv('C:/Users/felip/.cache/kagglehub/datasets/olistbr/brazilian-ecommerce/versions/2/olist_customers_dataset.csv')
geolocation = pd.read_csv('C:/Users/felip/.cache/kagglehub/datasets/olistbr/brazilian-ecommerce/versions/2/olist_geolocation_dataset.csv')
items = pd.read_csv('C:/Users/felip/.cache/kagglehub/datasets/olistbr/brazilian-ecommerce/versions/2/olist_order_items_dataset.csv')
payments = pd.read_csv('C:/Users/felip/.cache/kagglehub/datasets/olistbr/brazilian-ecommerce/versions/2/olist_order_payments_dataset.csv')
reviews = pd.read_csv('C:/Users/felip/.cache/kagglehub/datasets/olistbr/brazilian-ecommerce/versions/2/olist_order_reviews_dataset.csv')
orders = pd.read_csv('C:/Users/felip/.cache/kagglehub/datasets/olistbr/brazilian-ecommerce/versions/2/olist_orders_dataset.csv')
products = pd.read_csv('C:/Users/felip/.cache/kagglehub/datasets/olistbr/brazilian-ecommerce/versions/2/olist_products_dataset.csv')
sellers = pd.read_csv('C:/Users/felip/.cache/kagglehub/datasets/olistbr/brazilian-ecommerce/versions/2/olist_sellers_dataset.csv')
category = pd.read_csv('C:/Users/felip/.cache/kagglehub/datasets/olistbr/brazilian-ecommerce/versions/2/product_category_name_translation.csv')

dfs_list = [customers, geolocation, items, payments, reviews, orders, products, sellers, category]

print('customers',customers.columns, '\n',
'geolocation', geolocation.columns, '\n',
'items', items.columns, '\n',
'payments', payments.columns, '\n',
'reviews',reviews.columns, '\n',
'orders',orders.columns, '\n',
'products',products.columns, '\n',
'sellers',sellers.columns, '\n',
'category',category.columns)

income_UF = pd.read_excel('Tabela 5436.xlsx', header=0, names=['UF','mean_income'], skiprows=4, skipfooter=1)
UF_dic = {'Rondônia':'RO', 'Acre':'AC', 'Amazonas':'AM', 'Roraima':'RR','Pará':'PA', \
    'Amapá':'AP', 'Tocantins' :'TO',
    'Maranhão':'MA', 'Piauí':'PI', 'Ceará':'CE', 
    'Rio Grande do Norte':'RN', 'Paraíba':'PB', 'Pernambuco':'PE', 'Alagoas':'AL', 
    'Sergipe':'SE', 'Bahia':'BA', 'Minas Gerais':'MG', 
    'Espírito Santo':'ES', 'Rio de Janeiro':'RJ', 
    'São Paulo':'SP', 'Paraná':'PR', 'Santa Catarina':'SC', 'Rio Grande do Sul':'RS', 
    'Mato Grosso do Sul':'MS', 'Mato Grosso':'MT', 'Goiás':'GO', 'Distrito Federal':'DF'}

income_UF['short_UF'] = income_UF['UF'].map(UF_dic)


# Joinning dataframes

df = pd.merge(right=customers, left=orders, on='customer_id', suffixes=(None,'_r'))
df = pd.merge(left=df, right=orders, on='order_id', suffixes=(None,'_r'))
df = pd.merge(left=df, right=payments, on='order_id', suffixes=(None,'_r'))
df = pd.merge(left=df, right=items , on='order_id', suffixes=(None,'_r'))
df = pd.merge(left=df, right=products, on='product_id', suffixes=(None,'_r'))
df = pd.merge(left=df, right=income_UF, left_on='customer_state',\
     right_on='short_UF', suffixes=(None,'_r'))



print(df.columns)
print(df.shape)

# Filtering
df.drop(columns=df.filter(regex='_r', axis=1).columns, inplace=True)
df.set_index('customer_id', inplace=True)

# Analysing correlation (all orders)
correlation_temp = df[['payment_value', 'price', 'freight_value',
       'product_weight_g', 'product_length_cm', 
       'product_height_cm', 'product_width_cm', 'mean_income']].corr(numeric_only=True)

# Plot
fig, ax = plt.subplots()
ax.set_title('Correlation')
sns.heatmap(correlation_temp, cmap=sns.color_palette("YlOrBr", as_cmap=True),  \
linecolor='white', linewidths=0.5)
plt.show()



# Customers analysis
# Grouping by costumers Id

df_cust_group = df[['customer_unique_id','payment_value','freight_value']].\
    groupby(by='customer_unique_id').\
    agg(payment_value_sum=('payment_value','sum'),
    payment_value_mean = ('payment_value','mean'),
    freight_value_sum=('freight_value','sum'),
    freight_value_mean=('freight_value','mean')).reset_index()

# add other information about the customers
df_cust_group = df_cust_group.merge(right=customers[['customer_unique_id', \
    'customer_state']],
    on='customer_unique_id', how='left')

df_cust_group.duplicated().value_counts()

df_cust_group = df_cust_group.merge(right=income_UF, \
    left_on='customer_state', right_on='short_UF', how='left')

df_cust_group.duplicated().value_counts()


# Dataset analysis
## duplicated
df_cust_group.duplicated().value_counts()
df_cust_group.drop_duplicates(inplace=True)
df_cust_group.duplicated().value_counts()

df_cust_group['customer_unique_id'].duplicated().value_counts() # os duplicados são porque mudaram de UF
df_cust_group['Id_geral']=np.arange(1, df_cust_group.shape[0]+1, step=1)

#  orders analysis by customers
# Histogram
# Payment value (mean)
f, ax = plt.subplots()
sns.histplot(df_cust_group['payment_value_mean'], \
    stat='probability', log_scale=True)
ax.set_xlabel('Valor médio dos pedidos por consumidor')
plt.show()

# Payment value (sum)
f, ax = plt.subplots()
sns.histplot(df_cust_group['payment_value_sum'], \
    stat='probability', log_scale=True)
ax.set_xlabel('Valor total dos pedidos por por consumidor')
plt.show()

# Freight value (sum)
f, ax = plt.subplots()
sns.histplot(df_cust_group['freight_value_sum'], \
    stat='probability', log_scale=True)
ax.set_xlabel('Valor total frete por por consumidor')
plt.show()

# Freight value (mean)
f, ax = plt.subplots()
sns.histplot(df_cust_group['freight_value_mean'], \
    stat='probability')
ax.set_xlabel('Valor médio do frete por consumidor')
plt.show()


# Counts 
# Customers by UF
f, ax = plt.subplots()
sns.countplot(data=df_cust_group['short_UF'], \
    order=df_cust_group['short_UF'].value_counts().index, stat='proportion')
ax.set_xlabel('Proporção')
ax.set_title('Proporção dos consumidores por UF')
plt.show()

# Boxplots
# Payment (mean)
f, ax = plt.subplots()
sns.boxplot(data=df_cust_group, x='payment_value_mean', y='short_UF', log_scale=True)
ax.set_xlabel('UF')
ax.set_title('Distribuição do pagamento médio por UF')
plt.show()

# Payment (sum)
f, ax = plt.subplots()
sns.boxplot(data=df_cust_group, x='payment_value_sum', y='short_UF', log_scale=True)
ax.set_xlabel('UF')
ax.set_title('Distribuição do pagamento total por UF')
plt.show()


# Analysing correlation (by customers)
correlation_temp = df_cust_group[['payment_value_sum', 'payment_value_mean',
       'freight_value_sum', 'freight_value_mean', 'customer_state', 'UF',
       'mean_income']].corr(numeric_only=True)

# Correlation
fig, ax = plt.subplots()
fig.subtitle('Correlation')
sns.heatmap(correlation_temp, cmap=sns.color_palette("YlOrBr", as_cmap=True),  \
linecolor='white', linewidths=0.5)
plt.show()

# Order analysis
# Volume de vendas
df_ts_gp = df.copy()
df_ts_gp['order_purchase_timestamp'] = df_ts_gp['order_purchase_timestamp'].str.slice(0,10,1)
df_ts_gp = df_ts_gp.groupby(['order_status','order_purchase_timestamp']).sum(numeric_only=True)




f, ax = plt.subplots()
sns.lineplot(data=df_ts_gp, x = 'order_purchase_timestamp', y = 'payment_value', hue = 'order_status')
plt.show()


# Data Science
# Linear Regression analysis
# Drop outliers and high leverage


reg = linear_model.LinearRegression()



