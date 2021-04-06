# Import packages
import pandas as pd
import matplotlib.pyplot as plt

# import dataset
df = pd.read_csv("https://raw.githubusercontent.com/holtzy/data_to_viz/master/Example_dataset/5_OneCatSevNumOrdered.csv")

# filter data
df = df.loc[(df.name=="Ashley") | (df.name=="Amanda")]
df = df.loc[(df.sex=="F") & (df.year>1970)]
df = pd.pivot_table(df, values='n', index=['year'], columns=['name'])

# set the figure size
plt.figure(figsize=(10, 10))

# plot the connected scatterplot
plt.plot(df.Amanda, df.Ashley, '-', marker='o')

# add annotations in every 3 data points with a loop
for line in range(0, df.shape[0], 3):
  plt.annotate(
    df.index[line], 
    (df.Amanda.iloc[line], df.Ashley.iloc[line]+300 ) ,
    va='bottom',
    ha='center'
  )

# x axis label
plt.xlabel('Amanda')

# y axis label
plt.ylabel('Ashley')

# show the graph
plt.show()