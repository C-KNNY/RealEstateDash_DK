import os
from bs4 import BeautifulSoup
import pandas
import sys
print(sys.executable)

try:
    from lxml import etree
    print("lxml is installed and working")
except ImportError:
    print("lxml is NOT working")


# for Address, Price, Heating_Type
def get_simple(soup, tag_name, class_name):
    field = soup.find(tag_name, attrs={'class': class_name})
    if field:
        text = field.text.strip()
        return text if text else "N/A"
    else:
        return "N/A"

#for Square_m, Built_Year, Lot, Energy_Label

def get_complex(soup, class_name, value_tag, value_class):
    field_tag = soup.findAll('div', attrs={'class': class_name})
    if field_tag:
        index = field_tag[0].find(value_tag, attrs={'class': value_class})
        if index:
            text = index.text.strip()
            return text if text else "N/A"
    return "N/A"

def get_last_sale_price(soup):
    all_divs = soup.findAll('div')           
    
    for div in all_divs:                     
        text = div.get_text()                
        
        if 'Seneste salgspris' in text and len(text) < 30:  
            
            big_box = div.parent
            
            if big_box:                     
                big_text = big_box.get_text()      
                words = big_text.split()             
                
                for i in range(len(words)): 
                    #words = ["Seneste", "salgspris", "er", "2500000", "kr.", "i", "2024"]
                    word = words[i]                 
                    
                    if 'kr.' in word:   
                        #words = ["kr.", "er", "valutaen"]
                        if i > 0:                   
                            price_number = words[i - 1]    
                            Last_price = price_number + " " + word 
                            
                            if 'null' in Last_price:           
                                return Price                                        
                            if Last_price[0]:          
                                return Last_price                
    
    return Last_price   

def process_Price(Price):
    if Price == "N/A":
        return "N/A"
    if '%' not in Price:
        return Price[0:-4]
    else:
        char_to_find = '-'
        pos_find = Price.find(char_to_find)
        len_of_string = len(Price)
        amount_char_minus = len_of_string - pos_find
        if amount_char_minus == 4:
            return Price[0:-9]
        else:
            return Price[0:-8]
        
def process_Last_price(Last_price):
    if Last_price == Last_price:
        return Last_price
    if '%' not in Last_price:
        return Last_price[0:-4]
    else:
        return Last_price[0:-9]
        

def process_Square_m(Square_m):
    if Square_m == "N/A":
        return "N/A"
    return Square_m[0:-3]
    #x
def process_Lot(Lot):
    if Lot == "N/A":
        return "N/A"
    return Lot[0:-3]

   
        

Folder = "Detailedpages"
All_data = []

# Hent alle filer
Files = os.listdir(Folder)


# Loop gennem hver fil
for file in Files:
    try:
        
        file_path = os.path.join(Folder, file)
        html = open(file_path, 'r', encoding='utf-8').read()
        soup = BeautifulSoup(html, features="lxml")
        
        # Adresse
        Address = get_simple(soup, 'div', 'd-flex flex-column')
        
        # Pris
        Price = get_simple(soup, 'div', 'price')
        Price = process_Price(Price)
        
        #Last Price
        Last_Price = get_last_sale_price(soup)
        Last_Price = process_Last_price(Last_Price)
        
        # Square_m
        Square_m = get_complex(soup,'property-detail d-flex justify-content-between w-100 listing_details.text.size ng-star-inserted','div','value ng-star-inserted')
        Square_m = process_Square_m(Square_m)
        
        
        # Built_Year
        Built_Year = get_complex(soup,'property-detail d-flex justify-content-between w-100 listing_details.text.built_in ng-star-inserted','div','value ng-star-inserted')
        
        # Lot
        Lot = get_complex(soup,'property-detail d-flex justify-content-between w-100 listing_details.text.lot_size ng-star-inserted','div','value ng-star-inserted')
        Lot = process_Lot(Lot)
        
        # Energy_Label
        Energy_Label = get_complex(soup,'property-detail d-flex justify-content-between w-100 listing_details.text.energy_class ng-star-inserted','p','mb-0')
        
        # Heating_type
        Heating_Type = get_simple(soup, 'div', 'text-end value ng-star-inserted')
        
        
        if Address == "N/A":
            print('Adress not found at.', file_path)
        else:
            All_data.append([Address, Price, Last_Price, Square_m, Built_Year, Lot, Energy_Label, Heating_Type])
        
            print("Parsed:", file)
        
    except Exception as e:
        print("Error at " + file + ": " + str(e))

# Lav DataFrame
df = pandas.DataFrame(All_data, columns=['Address', 'Price_(DKK)', 'Last_price_(DKK)', 'Sqm', 'Built_year', 'Lot_size_(sqm)', 'Energy_label', 'Heating_type'])

df.to_csv('house_info.csv', index=False, encoding='utf-8')

print("Done parsing informations")
print("Number of houses:", len(All_data))