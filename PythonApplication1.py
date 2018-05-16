import urllib3
import requests
import shutil
import json
import os
import errno

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
#get data
output = open("Output.txt", "w")
output.write("product_code, category_a, category_b, category_c, product_name, size_count, size_unit, weight, price, image, description, is_for_adult, status, created_at, updated_at\n")
lines = []
query = []
with open('queries.txt') as f:
	lines = [line.rstrip('\n') for line in open('queries.txt')]
for line in lines:
	print(line)
	http = urllib3.PoolManager()
	parseline = line.replace(' ', '%20')
	parseline = parseline.replace('&', '%26')
	query = 'https://dev.tescolabs.com/grocery/products/?query=%s&offset=0&limit=15' % (parseline)
	req = http.request('GET', query, headers={"Ocp-Apim-Subscription-Key" : "9bcac9d5169e4ca8a8c429212719d1dc"})
	jsonData = json.loads(req.data.decode('utf-8'))

	loop = 1
	for result in jsonData['uk']['ghs']['products']['results']:
		try:
			#print(result['name'])
			#construct description from array
			description = ''
			try:
				description = ''.join(result['description'])
				description = description.replace("\"", "\\\"")
			except Exception as e:
				e=e
			sizeunit = 'Pack'
			if result['name'][-1] == "L":
				sizeunit = 'Bottle'
			if result['name'][-1] == "l":
				sizeunit = 'Bottle'
			#download image
			url = result['image']
			url = url.replace("90x90", "225x225")
			folder = url.replace("http://img.tesco.com/Groceries/pi", "C:\\Users\\Alex Taberner\\source\\repos\\PythonApplication1\\PythonApplication1\\images")
			sqlurl = url.replace("http://img.tesco.com/Groceries/pi/", "")
			folder = folder.replace("/", "\\")
			r = requests.get(url, stream=True, headers={'User-agent': 'Mozilla/5.0'})
			if r.status_code == 200:
				if not os.path.exists(os.path.dirname(folder)):
					try:
						os.makedirs(os.path.dirname(folder))
					except OSError as exc: # Guard against race condition
						if exc.errno != errno.EEXIST:
							raise
				with open(folder, 'wb') as f:
					r.raw.decode_content = True
					shutil.copyfileobj(r.raw, f)
			#parse into query 
			querysql = """%s",183,0,0,"%s",1,"%s",%s,%s,"%s","%s",0,1,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP\n""" % (result['tpnb'], result['name'], sizeunit, result['AverageSellingUnitWeight'], result['price'], sqlurl, description)
			print(loop)
			loop = loop+1
			output.write(querysql)
		except Exception as error:
			error=error
output.close()
