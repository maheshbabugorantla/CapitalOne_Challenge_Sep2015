import math
import csv
import json
import time
from collections import OrderedDict
from datetime import date
import numpy as np # Used for Calculating the Annual Revenue Prediction.
import pandas as pd # Used to Read the CSV File Columnwise
import scipy.interpolate # USed for the Prediction of customers for 2015

def Subscriber_Classification():

	''' Opening the Files Here '''
	print("\nOpening the CSV Files\n")
	
	read_csv = open('subscription_report.csv','r') 
	#read_csv = open('sample.csv','r')

	name_reader = csv.reader(read_csv, delimiter = ',') # Reading Each row of the csv file. 

	subscription_IDs = set() # Creating a list of IDs of Customers

	start_time = time.time()

	print("\nReading Rows\n")

	# Getting all the Subscription IDs
	for row in name_reader:
		subscription_IDs.add(str(row[1]))

	keys = list(subscription_IDs)

	# Creating a Hash Map with the Available Subscriber IDs
	subscribers = {key:[None,None,'one-off',1] for key in keys}

	read_csv.seek(0)

	for row in name_reader:

		#subscribers[row[1]][4] += 1

		if(subscribers[row[1]][0] == None):
			subscribers[row[1]][0] = str(row[3])
			subscribers[row[1]][1] = str(row[3])

		else:
			subscribers[row[1]][3] += 1

			val1 = subscribers[row[1]][1].split('/')
			val2 = str(row[3]).split('/')
			subscribers[row[1]][1] = str(row[3])
			date1 = date(int(val1[2]),int(val1[0]),int(val1[1])) # Date Object to Calculate the No.of Days 
			date2 = date(int(val2[2]),int(val2[0]),int(val2[1])) # Date Object to Calculate the No.of Days

			if(abs((date1 - date2).days) == 1):
				subscribers[row[1]][2] = 'Daily'

			elif((abs((date1 - date2).days) % 30 == 0) or (abs((date1 - date2).days) % 31 == 0) or (abs((date1 - date2).days) % 28 == 0) or (abs((date1 - date2).days) % 29 == 0)):
				subscribers[row[1]][2] = 'Monthly'

			else:
				subscribers[row[1]][2] = 'Yearly'

	#print("\n" + str(len(subscribers.keys())) + "\n\n")

	print("\nTime taken to classify all the IDs " + str(time.time() - start_time) + "\n")
	
	json_start = time.time()

	with open("SubscribersIDs_Classification.json", 'w') as json_file:
		json.dump(subscribers,json_file)

	print("\nTime to Write to Json File is " + str(time.time() - json_start) + "\n")

	# Writing to a CSV File
	IDs_Rows = [['ID','First Transaction','Last Transaction','Subscription Type','Subscription Period']]

	for key in subscribers:
		val = []
		val.append(key) # Subscriber ID
		val.append(subscribers[key][0]) # First Transaction Date
		val.append(subscribers[key][1]) # Last Transaction Date
		val.append(subscribers[key][2]) # Subscription Type
		val.append(subscribers[key][3]) # Subscription Period
		IDs_Rows.append(val)

	with open('Subscriber_IDs_Classification.csv',"w") as write_csv:
		csv_writer = csv.writer(write_csv) # Creating a CSV Writer Object
		csv_writer.writerows(IDs_Rows)

	print("\nSubscriber Classification is written to Subscriber_IDs_Classification.csv(CSV Format) and SubscribersIDs_Classification.json(JSON Format) files\n\n")

  	print('\n\nClosing the Files\n')

	''' Closing the File Handles '''
	read_csv.close()
	json_file.close()
	write_csv.close()

#	print(subscribers[str(15447)])

	return(subscribers)

def AnnualRevenue_Loss_Profit():

	print("\nOpening the CSV Files\n")
	
	read_csv = open('subscription_report.csv','r') 
	#read_csv = open('sample.csv','r')

	year_reader = csv.reader(read_csv,delimiter=',') # Reading Each row of the csv file. 

	Annual_Revenue = OrderedDict() # This is used to find the Annual Revenue For Each Year  

	start_time = time.time()

	print("\nReading Rows\n")

	start_read = time.time()

	years_keys = range(1966,2015)
		
	Annual_Revenue = {year:[None,None] for year in years_keys}

	for row in year_reader:

		# This is used to skip the first row of the .csv file 
		if(row[3] == 'Transaction Date'):
			pass

		else:
			date = row[3].split('/')
			year = float(date[2]) # This Extracts the Year in the Date.

			if ((Annual_Revenue[year][0] == None) and Annual_Revenue[year][1] == None):
				#Annual_Revenue.update({year:[float(row[2]),1]})
				Annual_Revenue[year][0] = float(row[2])
				Annual_Revenue[year][1] = 1

			else:
				Annual_Revenue[year][0] = Annual_Revenue[year][0] + float(row[2])
				#print(Annual_Revenue[year])
				#print("Year: " + str(year) + " Annual Revenue " + str(Annual_Revenue[year][0]) + "Type : " + str(type(Annual_Revenue[year])))
				Annual_Revenue[year][1] = Annual_Revenue[year][1] + 1 # This is used to count the transactions

	print("\nTime to Calculate the Annual Revenue is " + str(time.time() - start_time) + "\n")

	Revenue_Year = []
	Revenue_Year.append(['Year','Revenue','No. of Customers','No. of Transactions'])

	count_time = time.time()

	# Now Counting Customers Annually 
	read_csv.seek(0)

	Annual_Customers = {year: None for year in years_keys}

	for row in year_reader:

		if(row[3] == 'Transaction Date'):
			pass

		else:	
			year = float(row[3].split('/')[2])

			if(Annual_Customers[year] == None):
				#Annual_Customers[year] = [row[1]] # Getting the first Subscriber ID
				Annual_Customers[year] = set([row[1]])

			else:
					Annual_Customers[year].add(row[1])

	print("Time to Count the Customers is " + str(time.time() - count_time))

	for val in Annual_Revenue.keys():
		perYear = [val,Annual_Revenue[val][0],len(Annual_Customers[val]),Annual_Revenue[val][1]]
		Revenue_Year.append(perYear) 

	Profit_Loss = [] # This is Used Calculate the Profit and Loss % for each year.

	loss = 0  
	profit = 0
	min_year = 0
	max_year = 0

	loss_profit_time = time.time()

	# Calculating the Year with Max Profit and Max loss
	for val in range(2, len(Annual_Revenue.keys()) + 1):
		loss_profit = (float(float(Revenue_Year[val][1]) - float(Revenue_Year[val - 1][1])) / float(Revenue_Year[val][1]))*100
		Profit_Loss.append([Revenue_Year[val][0], loss_profit])
		
		if(loss > loss_profit):
			loss = loss_profit
			min_year = Revenue_Year[val][0]

		if(profit < loss_profit):
			profit = loss_profit
			max_year = Revenue_Year[val][0]

		#print("\n Max Year: " + str(max_year) + "Min Year: " + str(min_year) + " Loss: " + str(loss) + " Profit: " + str(profit) + " Profit_Loss: " + str(loss_profit) +"\n") 

	print("\nYear with Max Profit is " + str(max_year) +" and Year with Max Loss is " + str(min_year)+ "\n") 

	print("Time to Calculate the Years with Maximum Profit and Loss " + str(time.time() - loss_profit_time))

	with open('Annual_Revenue.csv',"w") as write_csv:
		csv_writer = csv.writer(write_csv) # Creating a CSV Writer Object
		csv_writer.writerows(Revenue_Year)

	# Closing the Files
	read_csv.close()
	write_csv.close()

	return(Revenue_Year)

def Customers_Transactions_Prediction():

	years = range(1966,2015)

	# Building Hash Map.
	Annual_Revenue = {str(year):[None,None,None] for year in years}

	csv_read = open('Annual_Revenue.csv','r')

	read_rows = csv.reader(csv_read,delimiter=',') # Reading Each row of the csv file.

	# Building Whole Dictionary for Analysis
	for row in read_rows:

		if(row[0] != 'Year'):
			Annual_Revenue[row[0]][0] = float(row[1]) # Annual Revenue
			Annual_Revenue[row[0]][1] = int(row[2]) # Annual Customers
			Annual_Revenue[row[0]][2] = int(row[3]) # Annual Transactions

		else:
			pass

	customer_trend = []
	transaction_trend = []
	#revenue_trend = []

	# Getting the Previous 10 Years Customers and Transactions Retention
	for val in range(2004,2014):
		customer_trend.append(Annual_Revenue[str(val + 1)][1] - Annual_Revenue[str(val)][1])
		transaction_trend.append(Annual_Revenue[str(val + 1)][2] - Annual_Revenue[str(val)][2])
		#revenue_trend.append(Annual_Revenue[str(val + 1)][0] - Annual_Revenue[str(val)][0])

	# Doing Linear Regression to get the Customer Count Prediction
	x_cus = np.arange(0,len(customer_trend))
	y_cus = np.array(customer_trend)
	z_cus = np.polyfit(x_cus,y_cus,1)

	# Doing Linear Regression to get the Transaction Count Prediction
	x_trans = np.arange(0,len(transaction_trend))
	y_trans = np.array(transaction_trend)
	z_trans = np.polyfit(x_trans,y_trans,1)

	df = pd.read_csv('Annual_Revenue.csv')

	x_revenue_cus = np.array(df['No. of Customers'].values.tolist())
	x_revenue_trans = np.array(df['No. of Transactions'].values.tolist())
	revenue_annual = np.array(df['Revenue'].values.tolist())

	z_rev_cus = np.polyfit(x_revenue_cus,revenue_annual,2)
	z_rev_trans = np.polyfit(x_revenue_trans,revenue_annual,2)

	cus_2015 = math.ceil(Annual_Revenue['2014'][1] + (z_cus[0]*11 + z_cus[1]))
	trans_2015 = math.ceil(Annual_Revenue['2014'][2] + (z_trans[0]*11 + z_trans[1]))

	print("\nCustomer number prediction for 2015 is " + str(cus_2015) + "\n\n")

	print("Transactions Number prediction for 2015 is " + str(trans_2015) + "\n\n")	

	#print(z_rev_trans[0])

	print("Revenue Prediction based on Transactions " + str(z_rev_trans[0]*(trans_2015*trans_2015) + z_rev_trans[1]*trans_2015 + z_rev_trans[2]))

	print("Revenue Prediction based on Customers " + str(z_rev_cus[0]*(cus_2015*cus_2015) + z_rev_cus[1]*cus_2015 + z_rev_cus[2]))

	''' Closing the Files '''
	csv_read.close()

	return([cus_2015,trans_2015])

# '''def Predict_Annual_Revenue():

# 	''' Predicting the Annual Revenue for the 2015 '''

# 	df = pd.read_csv('Annual_Revenue.csv')
# 	years = df['Year']
# 	revenue = df['Revenue']
# 	no_customers = df['No. of Customers']

# 	years = np.array(df['Year'].values.tolist())
# 	x = np.array(df['No. of Customers'].values.tolist())
# 	y = np.array(df['Revenue'].values.tolist())

# 	''' Predicting 2015 Customers '''

# 	Customers_Transactions = Customers_Transactions_Prediction()

# 	# interpolate to approximate a continuous version of customer retention over time
# 	f = scipy.interpolate.interp1d(y, x, kind='quadratic')

# 	# approximate the first and second derivatives near the last point (2015)
# 	dx = 0.01
# 	x0 = y[-1] - 2*dx
# 	first = scipy.misc.derivative(f, x0, dx=dx, n=1)
# 	second = scipy.misc.derivative(f, x0, dx=dx, n=2)

# 	# taylor series approximation near x[-1]
# 	forecast = lambda x_new: np.poly1d([second/2, first, f(years[-1])])(x_new - years[-1])

# 	xs = np.arange(2015,2020)
# 	ys = forecast(xs)

# 	''' Here is a best-fit polynomial equation for Predicting annual revenue '''
# 	z = np.polyfit(x, y, 3)
	
# 	print("z: " + str(z))
# 	print("ys: " + str(ys))	
# '''

def main():

	start_time = time.time()

	print("\n\n********** Now Classifying all IDs to Monthly, Yearly, Daily or one-off *********** \n\n")

	''' This uses 'subscription_report.csv' and writes the dictionary to a .json file '''
	subscribers = Subscriber_Classification()

	print("\n\n*********** Now Calculating the Annual Revenue between 1966 and 2014 and years with Max. Profit and Max. Loss *********** \n\n")

	''' This uses 'subscription_report.csv' and writes the Annual Revenue to 'Annual_Revenue.csv' '''
	Revenue_Year = AnnualRevenue_Loss_Profit()

	#Predict_Annual_Revenue()

	Customers_Transactions_Prediction()

	print("\nTotal time taken for the whole analysis is " + str(time.time() - start_time) + " seconds \n")

if __name__=='__main__':
	main()