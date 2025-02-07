import pandas as pd
from scipy import stats
import seaborn as sns
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
fig.subtitle('Correlation')
sns.heatmap(correlation_temp, cmap=sns.color_palette("YlOrBr", as_cmap=True),  \
linecolor='white', linewidths=0.5)
plt.show()

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
f, ax = plt.subplots()
sns.histplot(df_cust_group['payment_value_mean'], \
    stat='probability', log_scale=True)
ax.set_xlabel('Valor médio dos pedidos por consumidor')
plt.show()

f, ax = plt.subplots()
sns.histplot(df_cust_group['payment_value_sum'], \
    stat='probability', log_scale=True)
ax.set_xlabel('Valor total dos pedidos por por consumidor')
plt.show()

# Counts
f, ax = plt.subplots()
sns.countplot(data=df_cust_group['short_UF'], \
    order=df_cust_group['short_UF'].value_counts().index, stat='proportion')
ax.set_xlabel('Número de consumidores')
plt.show()



# Analysing correlation (by customers)
correlation_temp = df_cust_group[['payment_value_sum', 'payment_value_mean',
       'freight_value_sum', 'freight_value_mean', 'customer_state', 'UF',
       'mean_income']].corr(numeric_only=True)

# Plots
fig, ax = plt.subplots()
fig.subtitle('Correlation')
sns.heatmap(correlation_temp, cmap=sns.color_palette("YlOrBr", as_cmap=True),  \
linecolor='white', linewidths=0.5)
plt.show()



# Linear Regression analysis
# Drop outliers and high leverage


reg = linear_model.LinearRegression()



