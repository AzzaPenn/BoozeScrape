import json
import requests
import csv
import os
import shutil
import datetime

#setup and creation
print("Accessing json file...") 
scraped_data = requests.get("https://www.boozebud.com/a/products?pagesize=5000")
data = json.loads(scraped_data.text)
#open & read json
results = (data["results"])
#get all items from json since in a listed form
json_items = len(results)
print("json loaded...")



def write_to_JSON(data, name):
	json_fpath = name + '.json'
	with open(json_fpath, 'w') as fp:
		json.dump(data, fp)

#generate intial file for first time run 
#should make this into a class
def gen_basic_data():
	with open('data.csv', 'w+', newline='') as csv_file:
		fieldnames = ["sku", "Name", "Brand", "Type", "Style", "Quantity", "URL"]
		writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
		writer.writeheader()
		for item in range(json_items):
			#going through the tiers of the json to pull correct data
			t_1 = (results[item])
			t_2 = (t_1["variants"])
			len_2 = len(t_2)
			brand = (t_1["brandName"])
			name = (t_1["name"])
			type = (t_1["beverageTypeInfo"]["displayName"])
			url =  ("https://www.boozebud.com" + t_1["url"])
			try:
				style = (t_1["style"])
			except KeyError:
				style = "Misc"
			for item in range(len_2):
				size = (t_1["variants"][item]["prefix"])
				quantity = (str(t_1["variants"][item]["qty"]))
				price = (float(t_1["variants"][item]["price"]))
				sku = (t_1["variants"][item]["sku"])
				writer.writerow({"sku":sku, "Name":name, "Brand":brand, "Type":type,
				 "Style":style, "Quantity":quantity, "URL":url})
	print("data.csv has been generated")

#gen original price JSON
def gen_price_data():
	data = {}
	for item in range(json_items):
		t_1 = (results[item])
		t_2 = (t_1["variants"])
		len_2 = len(t_2)
		for item in range(len_2):
			price = (float(t_1["variants"][item]["price"]))
			sku = (t_1["variants"][item]["sku"])
			data[sku] = [price]
	write_to_JSON(data, 'price_data')  ###need to change this to float from string
#compares stored price data and updates it if changes occured since last run
def edit_json():
	new_data = {}
	for item in range(json_items):
		t_1 = (results[item])
		t_2 = (t_1["variants"])
		len_2 = len(t_2)
		for item in range(len_2):
			price = (str(t_1["variants"][item]["price"]))
			sku = (t_1["variants"][item]["sku"])
			new_data[sku] = [price]
	with open ('price_data.json') as og_json_data:
		old_data = json.load(og_json_data)
	common_keys = set(new_data) & set(old_data)
	for key in common_keys:
		if float(new_data[key][-1]) != float(old_data[key][-1]):
			print(new_data[key][-1])
			old_data[key].append(float(new_data[key][-1]))
	write_to_JSON(old_data, 'price_data')
	

def find_new_entries():
	new_data = {}
	for item in range(json_items):
		t_1 = (results[item])
		t_2 = (t_1["variants"])
		len_2 = len(t_2)
		for item in range(len_2):
			price = (str(t_1["variants"][item]["price"]))
			sku = (t_1["variants"][item]["sku"])
			new_data[sku] = [price]
	with open ('price_data.json') as og_json_data:
		old_data = json.load(og_json_data)
	diff = set(new_data) - set(old_data)
	if len(diff) == 0:
		print("No changes detected")
	else:
		print(diff)
		for item in diff:
			old_data[item] = [0]
		print("New SKU's Added")
		write_to_JSON(old_data, 'price_data')

def backup():
	path = os.getcwd()
	try:
		os.mkdir("backups")
	except(FileExistsError):
		print("Folder already exists")
	now = (str(datetime.datetime.now())[:19]).replace(":","").replace(" ","")
	scrfile = (path + "\price_data.json")
	dstfile = (path + "\\backups" + "\price_data" + now + ".json")
	shutil.copy(scrfile, dstfile)

		
print("Finding Any New Entries.....")
find_new_entries()
print("Updating Price Data......")
edit_json()
print("Backing Up......")
backup()
print("Done!")
#gen_price_data()


