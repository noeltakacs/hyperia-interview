# Indent space is set to 2 spaces (hope it's okay)

import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime


class LeafletParser:
  WEB_URL = 'https://www.prospektmaschine.de/hypermarkte/'

  def __init__(self):
    self.session = requests.Session() # Initialize a session for making requests

  def fetch_data(self):
    data = self.session.get(self.WEB_URL) # Fetch data from the website

    if data.status_code != 200:
      print(f'Failed to fetch data: {data.status_code}') # Print the status code if the request fails
      return

    print('Data fetched successfully')

    return BeautifulSoup(data.text, 'html.parser') # Parse the HTML data using BeautifulSoup

  def parse_data(self, data):
    leaflets = []

    parsed_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get current time (not sure if this is the correct meaning of parsed_time used in the example in the google doc)

    for leaflet in data.select('.grid-item'): # Iterate over all the leaflets in the HTML data with the class 'grid-item'
      try:
        title = leaflet.select_one('.grid-item-content').text # Extract the title of the leaflet
        
        thumbnail = leaflet.select_one('.img-container img')
        thumbnail = thumbnail.get('src') or thumbnail.get('data-src') # Extract the thumbnail of the leaflet from the src or data-src attribute (some images have the src attribute and some have the data-src attribute)
        
        shop_name = ''

        for i in leaflet.select_one('.lazyloadLogo')['alt'].split(' ')[1:]: # Extract the shop name from the alt attribute and remove the first word (which is 'Logo')
          shop_name += i + ' ' # Keep adding the words to the shop_name variable until the loop ends (if the name is more than one word)

        shop_name = shop_name[:-1] # Remove the last space from the shop_name variable

        valid_from, valid_to = self.format_date((leaflet.select_one('.hidden-sm').text)) # Extract the valid_from and valid_to dates from the HTML data and format them
        
        # Append the extracted data to the leaflets list
        leaflets.append(
          {
            'title': title,
            'thumbnail': thumbnail,
            'shop_name': shop_name,
            'valid_from': valid_from,
            'valid_to': valid_to,
            'parsed_time': parsed_time,
          }
        )
      except Exception as e:
        print(f'Failed to parse leaflet: {e}') # Print the error if the parsing fails

    return leaflets

  def format_date(self, date):
    if ' - ' not in date: # Check if the date is a range or not (one leaflet contains 'von Dienstag 15.11.2022' which is not a range)
      valid_from = ''
      valid_to = ''

      for i in date.split(' '): # Split the string by space and find the dates by checking if there is a '.' in the string
        if '.' in i and not valid_from: # If '.' is in the string and valid_from is empty, then it's the valid_from date
          valid_from = datetime.strptime(i, '%d.%m.%Y').strftime('%Y-%m-%d')
        elif '.' in i and valid_from: # If '.' is in the string and valid_from is not empty, then it's the valid_to date
          valid_to = datetime.strptime(i, '%d.%m.%Y').strftime('%Y-%m-%d')

      return valid_from, valid_to

    date = date.split(' - ') # Split the date by ' - '

    valid_from = datetime.strptime(date[0], '%d.%m.%Y').strftime('%Y-%m-%d') # Format the date from 'dd.mm.yyyy' to 'yyyy-mm-dd'
    valid_to = datetime.strptime(date[1], '%d.%m.%Y').strftime('%Y-%m-%d')

    return valid_from, valid_to

  def data_to_json(self, leaflets, filename):
    with open(filename, 'w', encoding='utf-8') as file: # Open the file in write mode
      json.dump(leaflets, file, ensure_ascii=False, indent=4) # Write the leaflets data to the file in JSON format

  def run_parser(self):
    try:
      data = self.fetch_data() # Fetch the data from the website
      leaflets = self.parse_data(data) # Parse the data
      self.data_to_json(leaflets, 'leaflets.json') # Save the data to a JSON file
      print('Leaflets parsed successfully')
    except Exception as e:
      print(f'Failed to run parser: {e}') # Print the error if the parser fails


if __name__ == '__main__':
  parser = LeafletParser()
  parser.run_parser() # Run the parser
