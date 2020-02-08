from flask import Flask, render_template
import requests, json
app = Flask(__name__)

def write_to_JSON(data, name):
	json_fpath = name + '.json'
	with open(json_fpath, 'w') as fp:
		json.dump(data, fp)

products = {}
pro_names = []
name_url = {}
def start_up():
	print("Starting Up!/Refreshing!")
	scraped_data = requests.get("https://www.boozebud.com/a/products?pagesize=5000")
	data = json.loads(scraped_data.text)
	results = (data["results"])
	json_items = len(results)
	for item in range(json_items):
				t_1 = (results[item])
				t_2 = (t_1["variants"])
				len_2 = len(t_2)
				brand = (t_1["brandName"])
				name = (t_1["name"])
				image = (t_1["smallImage"])
				largeimg = (t_1["largeImage"])
				_type = (t_1["beverageTypeInfo"]["displayName"])
				url =  ("https://www.boozebud.com" + t_1["url"])
				url_end = t_1["url"]
				try:
					style = (t_1["style"])
				except KeyError:
					style = "Misc"
				for item in range(len_2):
					size = (t_1["variants"][item]["prefix"])
					quantity = (str(t_1["variants"][item]["qty"]))
					price = (float(t_1["variants"][item]["price"]))
					sku = (t_1["variants"][item]["sku"])
					prefix = (t_1["variants"][item]["prefix"])
					products[sku]=(brand, name, _type, size, quantity, url, image, (url_end), prefix, largeimg)
					pro_names.append(brand)

	namelist = set(pro_names)
	for item in namelist:
		name_url[item] = item.replace(" ", "_").replace("&", "_").replace("'", "_").replace(".","_")
	print("Detecting Changes!")
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
		print("No Changes Detected!")
	else:
		print(diff)
		for item in diff:
			old_data[item] = [0]
		print("New SKU's Added")
		write_to_JSON(old_data, 'price_data')

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

start_up()
with open ('price_data.json') as raw_price_data:
		price_data = json.load(raw_price_data)

def write_to_JSON(data, name):
	json_fpath = name + '.json'
	with open(json_fpath, 'w') as fp:
		json.dump(data, fp)

@app.route("/")
def home_page():
    return render_template('home.html', title = 'Home', products = products, price_data = price_data)

@app.route("/search")
def search_page():
    return render_template('search.html', title = 'Search', products = products, names = name_url)

@app.route("/<product_name>",  methods = ['GET', 'POST'])
def product_details(product_name):
	return render_template('products.html', title = product_name, product_name = product_name, products = products, price_data = price_data )

@app.route("/<product_name>/<deat>/<end_url>",  methods = ['GET', 'POST'])
def product_detailed(product_name, deat, end_url):
	return render_template('detailed.html', title = product_name, product_name = product_name, products = products, price_data = price_data, deat = deat, end_url = end_url)

@app.route("/update_price")
def update_data():
	start_up()
	return home_page()

if __name__ == '__main__':
	app.jinja_env.add_extension('jinja2.ext.do')
	app.run(debug=True, host= '0.0.0.0')
