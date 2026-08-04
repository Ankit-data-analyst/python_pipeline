import csv
import json
from datetime import datetime
from logger import log_info,log_error
from config import DEALER_LOCAL_FILE, CLEAN_DEALER_FILE,REJECT_DEALER_FILE, SUMMARY_DEALER_FILE
from config import PRODUCT_LOCAL_FILE, CLEAN_PRODUCT_FILE, REJECT_PRODUCT_FILE, SUMMARY_PRODUCT_FILE
from config import INVENTORY_LOCAL_FILE, CLEAN_INVENTORY_FILE, REJECT_INVENTORY_FILE, SUMMARY_INVENTORY_FILE
from config import SALES_LOCAL_FILE, CLEAN_SALES_LOGS_FILE, REJECT_SALES_LOGS_FILE, SUMMARY_SALES_LOGS_FILE

 

def safe_int(value):
    try:
        return int(value)
    except (TypeError,ValueError):
        return None
    
def get_dealer_product_ids():
    dealer_ids = []
    product_ids = []
    with open(CLEAN_DEALER_FILE,'r') as f_read,open(CLEAN_PRODUCT_FILE,'r') as f:
        dealer_reader = csv.DictReader(f_read)
        product_reader = csv.DictReader(f)
        for row in dealer_reader:
            dealer_ids.append(safe_int(row.get('dealer_id')))
        for row in product_reader:
            product_ids.append(safe_int(row.get('product_id')))
    return dealer_ids,product_ids

def load_csv(path):
    with open(path,'r',newline='') as f:
        data = csv.DictReader(f)
        return list(data),data.fieldnames
    
def normalize_null(str):
    if str is None:
        return None
    
    str = str.strip()
    
    if str.upper() in {'NA','NONE',''}:
        return None
    return str
    
def strip_whitespace(str):
    return str.strip()

def safe_float(value):
    try:
        return float(value)
    except (TypeError,ValueError):
        return None
             
#---------------------------------------------------------------------
#-----------------__DEALER VALIDATION___------------------------------
#---------------------------------------------------------------------
def validate_dealer(row):
    
    def clean_row(row):
        
        clean = row.copy()
        
        dealer_id = clean.get('dealer_id')
        dealer_code = clean.get('dealer_code')
        dealer_name = clean.get('dealer_name')
        city = clean.get('city')
        state = clean.get('state')
        region = clean.get('region')
        dealer_type = clean.get('dealer_type')
        email = clean.get('email')
        credit_terms_days = clean.get('credit_terms_days')
        

        dealer_code = normalize_null(dealer_code)
        dealer_name = normalize_null(dealer_name)
        
        city = strip_whitespace(city)
        state = strip_whitespace(state)
        region = strip_whitespace(region)
        dealer_type = strip_whitespace(dealer_type)
        email = strip_whitespace(email)
        
        dealer_id = safe_int(dealer_id)
        credit_terms_days = safe_int(credit_terms_days)
        
        clean['dealer_name'] = dealer_name
        clean['dealer_code'] = dealer_code
        clean['dealer_id'] = dealer_id
        clean['city'] = city 
        clean['state'] = state
        clean['region'] = region
        clean['dealer_type'] = dealer_type
        clean['email'] = email
        clean['dealer_id'] = dealer_id
        clean['credit_terms_days'] = credit_terms_days
        
        
        return clean

    row = clean_row(row)

    def check_required(row):
        errors = []
        if not row.get('dealer_id'):
            errors.append('EOO1')
            log_error(f'STAGE = TRANSFORM | dealer_id is missing')
        if not row.get('dealer_name'):
            errors.append('EOO2')
            log_error(f'STAGE = TRANSFORM | dealer_name is missing')
        return errors

    def check_range(row):
        errors = []
        credit_terms_days = int(row.get('credit_terms_days'))
        if credit_terms_days<0:
            errors.append('E003')
            log_error(f'STAGE = TRANSFORM | credit terms days should not be less than zero')
        return errors
            
    def check_date(row):
        errors = []
        created_date = row.get('created_date')
        try:
            created_date = row.get('created_date')
            if created_date:
                datetime.strptime(created_date,'%Y-%m-%d')
        except (ValueError):
            errors.append('EOO4')
            log_error(f'STAGE = TRANSFORM | Invalid date format or date')
        return errors
    
    def check_values(row):
        errors = []
        region = row.get('region')
        if(region and region.upper() not in ['NORTH','SOUTH','EAST','WEST']):
            errors.append('E005')
            log_error(f'STAGE = TRANSFORM | Innvalid value for region')
        return errors
    
    errors = []

    errors.extend(check_required(row))
    errors.extend(check_values(row))
    errors.extend(check_date(row))
    errors.extend(check_range(row))

    return row, errors
    
def transform_dealer():
    
    path = DEALER_LOCAL_FILE
    reader,fieldnames = load_csv(path)
    log_info(f'STAGE = TRANSFORM | CREATING CLEAN AND REJECTED RECORDS FOR DEALER FILE')
    with open(CLEAN_DEALER_FILE, "w", newline="") as f_clean, open(REJECT_DEALER_FILE, "w", newline="") as f_reject, open(SUMMARY_DEALER_FILE,'w') as f_summary:
        
        clean_writer = csv.DictWriter(f_clean,fieldnames)
        clean_writer.writeheader()

        reject_writer = csv.DictWriter(f_reject,fieldnames + ["Errors"])
        reject_writer.writeheader()

        clean_count = 0
        reject_count = 0
        errors = []
        summary = {}
        dealer_ids = []
        log_info(f'STAGE = TRANSFORM | VALIDATING DEALER RECORDS')
        for row in reader:
            clean_row,error = validate_dealer(row)
            
            if len(error)==0:
                clean_writer.writerow(clean_row)
                clean_count+=1
                dealer_ids.append(clean_row['dealer_id'])
            else:
                row['Errors'] = error
                reject_writer.writerow(clean_row)
                reject_count+=1
                errors.extend(error)
        log_info(f'STAGE = TRANSFORM | SUCCESSFULLY VALIDATED DEALER RECORDS')
        summary['Total_Records'] = clean_count+reject_count
        summary['Clean_Records'] = clean_count
        summary['Rejected Records'] = reject_count
        summary['Errors'] = errors
        summary['status'] = "SUCCESS",
        summary['timestamp'] = datetime.now().isoformat()
        json.dump(summary,f_summary,indent = 4)
        log_info(f'STAGE = TRANSFORM | SUCCESSFULLY CREATED CLEAN AND REJECTED RECORDS FOR DEALER FILE')


#---------------------------------------------------------------------
#-----------------__PRODUCT_VALIDATION___------------------------------
#---------------------------------------------------------------------

def validate_product(row):
    
    def clean_row(row):
        
        clean = row.copy()
        
        product_id = clean.get('product_id')
        sku= clean.get('sku')
        product_name= clean.get('product_name')
        category = clean.get('category')
        subcategory = clean.get('subcategory')
        brand = clean.get('brand')
        uom = clean.get('uom')
        

        sku= normalize_null(sku)
        product_name = normalize_null(product_name)
        
        
        category = strip_whitespace(category)
        subcategory = strip_whitespace(subcategory)
        brand = strip_whitespace(brand)
        uom = strip_whitespace(uom)
        
        product_id = safe_int(product_id)
        
        clean['sku'] = sku
        clean['product_name'] = product_name
        clean['category'] = category
        clean['subcategory'] = subcategory
        clean['brand'] = brand
        clean['uom'] = uom
        clean['product_id'] = product_id
        
        
        return clean

    row = clean_row(row)

    def check_required(row):
        errors = []
        if not row.get('product_id'):
            errors.append('EOO6')
            log_error(f'STAGE = TRANSFORM | product_id IS MISSING')
        if not row.get('sku'):
            errors.append('EOO7')
            log_error(f'STAGE = TRANSFORM | sku IS MISSING')
        if not row.get('product_name'):
            errors.append('EOO8')
            log_error(f'STAGE = TRANSFORM | product_name IS MISSING')
        return errors

    def check_range(row):
        errors = []
        required = ['unit_price', 'unit_cost', 'weight_kg']
        
        for value in required:
            raw_val = row.get(value)
            
           
            if raw_val is None:
                errors.append('E009')
                log_error(f'STAGE = TRANSFORM | {raw_val} IS NONE')
                continue
                
           
            clean_val = str(raw_val).strip().upper()
            if clean_val in {'NA', 'NULL', ''}:
                errors.append('E009')
                log_error(f'STAGE = TRANSFORM | {raw_val} IS NOT AVAILABLE')
                continue
                
            
            try:
                if float(clean_val) < 0.0:
                    errors.append('E009')
                    log_error(f'STAGE = TRANSFORM | {raw_val} OUT OF RANGE')
            except ValueError:
                errors.append('E009') 
                log_error(f'STAGE = TRANSFORM | {raw_val} is not float')
        
        return errors

            
    def check_date(row):
        errors = []
        created_date = row.get('created_date')
        try:
            created_date = row.get('created_date')
            if created_date:
                datetime.strptime(created_date,'%Y-%m-%d')
        except (ValueError):
            errors.append('EOO10')
            log_error(f'STAGE = TRANSFORM | Invalid Date format or date')
        return errors
    
    
    errors = []

    errors.extend(check_required(row))
    errors.extend(check_date(row))
    errors.extend(check_range(row))
    return row,errors
    
def transform_product():
    path = PRODUCT_LOCAL_FILE
    reader,fieldnames = load_csv(path)
    log_info(f'STAGE = TRANSFORM | CREATING CLEAN AND REJECTED RECORDS FOR PRODUCT FILE')
    with open(CLEAN_PRODUCT_FILE, "w", newline="") as f_clean, open(REJECT_PRODUCT_FILE, "w", newline="") as f_reject, open(SUMMARY_PRODUCT_FILE,'w') as f_summary:
        
        clean_writer = csv.DictWriter(f_clean,fieldnames)
        clean_writer.writeheader()

        reject_writer = csv.DictWriter(f_reject,fieldnames + ["Errors"])
        reject_writer.writeheader()

        clean_count = 0
        reject_count = 0
        errors = []
        summary = {}
        product_ids = []
        log_info(f'STAGE = TRANSFORM | VALIDATING PRODUCT RECORDS')
        for row in reader:
            clean_row,error = validate_product(row)
            
            if len(error)==0:
                clean_writer.writerow(clean_row)
                clean_count+=1
                product_ids.append(clean_row['product_id'])
            else:
                row['Errors'] = error
                reject_writer.writerow(clean_row)
                reject_count+=1
                errors.extend(error)
        log_info(f'STAGE = TRANSFORM | SUCCESSFULLY VALIDATED PRODUCT RECORDS')
        summary['Total_Records'] = clean_count+reject_count
        summary['Clean_Records'] = clean_count
        summary['Rejected Records'] = reject_count
        summary['Errors'] = errors
        summary['status'] = "SUCCESS",
        summary['timestamp'] = datetime.now().isoformat()
        json.dump(summary,f_summary,indent = 4)
        log_info(f'STAGE = TRANSFORM | SUCCESSFULLY CLEAN AND REJECTED RECORDS FOR PRODUCT FILE')


#---------------------------------------------------------------------
#-----------------__INVENTORY_VALIDATION___------------------------------
#---------------------------------------------------------------------
# inventory_id,snapshot_date,dealer_id,product_id,on_hand_qty,on_order_qty,reorder_point,reorder_qty,last_restock_date,last_sale_date

def validate_inventory(row):
    
    def clean_row(row):
        
        clean = row.copy()
        
        inventory_id = clean.get('inventory_id')
        dealer_id = clean.get('dealer_id')
        product_id = clean.get('product_id')
       
        

        inventory_id= normalize_null(inventory_id)

        dealer_id = safe_int(dealer_id)
        product_id = safe_int(product_id)
        
        clean['dealer_id'] = dealer_id
        clean['product_id'] = product_id
        clean['inventory_id'] = inventory_id
        
        
        return clean

    row = clean_row(row)


    def check_required(row):
        errors = []
        if not row.get('product_id'):
            errors.append('EOO11')
            log_error(f'STAGE = TRANSFORM | product_id IS MISSING')
        if not row.get('dealer_id'):
            errors.append('EO12')
            log_error(f'STAGE = TRANSFORM | dealer_id IS MISSING')
        if not row.get('inventory_id'):
            errors.append('EO13')
            log_error(f'STAGE = TRANSFORM | inventory_id IS MISSING')
        return errors

    def check_range(row):
        errors = []

        raw_val = row.get("on_hand_qty")

        if raw_val is None:
            return errors

        clean_val = str(raw_val).strip().upper()

        if clean_val in {"NA", "NULL", ""}:
            return errors

        try:
            qty = int(float(clean_val))

            if qty < 0 or qty > 10000:
                errors.append("E014")
                log_error(f"STAGE = TRANSFORM | INVALID RANGE FOR {qty}")

        except ValueError:
            errors.append("E014")
            log_error(f"STAGE = TRANSFORM | INVALID VALUE FOR on_hand_qty: {raw_val}")

        return errors
            
    def check_date(row):
        errors = []
        try:
            snapshot_date = row.get('snapshot_date')
            last_restock_date = row.get('last_restock_date')
            last_sale_date = row.get('last_sale_date')
            if snapshot_date:
                datetime.strptime(snapshot_date,'%d-%m-%Y')
            if last_restock_date:
                datetime.strptime(last_restock_date,'%d-%m-%Y')
            if last_sale_date:
                datetime.strptime(last_sale_date,'%d-%m-%Y')
        except (ValueError):
            errors.append('EOO15')
            log_error(f'STAGE = TRANSFORM | Invalid date format or date')
        return errors
    
    def check_fk(row):
        errors = []
        dealer_ids,product_ids = get_dealer_product_ids()
        dealer = row.get("dealer_id")
        if dealer not in dealer_ids:
            errors.append('EOO16')
            log_error(f'STAGE = TRANSFORM | dealer_id is missing in DEALER Table')
        
        product = row.get("product_id")
        if product not in product_ids:
            errors.append("E0017")
            log_error(f'STAGE = TRANSFORM | product_id is missing in PRODUCTS Table')
        
        return errors
    
    errors = []

    errors.extend(check_required(row))
    errors.extend(check_date(row))
    errors.extend(check_range(row))
    errors.extend(check_fk(row))
    return row,errors
    
def transform_inventory():
    path = INVENTORY_LOCAL_FILE
    reader,fieldnames = load_csv(path)
    log_info(f'STAGE = TRANSFORM | CREATING CLEAN AND REJECTED RECORDS FOR INVENTORY')
    with open(CLEAN_INVENTORY_FILE, "w", newline="") as f_clean, open(REJECT_INVENTORY_FILE, "w", newline="") as f_reject, open(SUMMARY_INVENTORY_FILE,'w') as f_summary:
        
        clean_writer = csv.DictWriter(f_clean,fieldnames)
        clean_writer.writeheader()

        reject_writer = csv.DictWriter(f_reject,fieldnames + ["Errors"])
        reject_writer.writeheader()

        clean_count = 0
        reject_count = 0
        errors = []
        summary = {}
        log_info(f'STAGE = TRANSFORM | VALIDATING INVENTORY RECORDS')
        for row in reader:
                
            clean_row,error = validate_inventory(row)
            
            if len(error)==0:
                clean_writer.writerow(clean_row)
                clean_count+=1
            else:
                row['Errors'] = error
                reject_writer.writerow(clean_row)
                reject_count+=1
                errors.extend(error)
        log_info(f'STAGE = TRANSFORM | VALIDATION COMPLETED FOR INVENTORY RECORDS')
        summary['Total_Records'] = clean_count+reject_count
        summary['Clean_Records'] = clean_count
        summary['Rejected Records'] = reject_count
        summary['Errors'] = errors
        summary['status'] = "SUCCESS",
        summary['timestamp'] = datetime.now().isoformat()
        json.dump(summary,f_summary,indent = 4)
        log_info(f'STAGE = TRANSFORM | SUCCESSFULLY CREATED CLEAN AND REJECTED RECORDS FOR INVENTORY')
        
#---------------------------------------------------------------------
#-----------------__SALES_LOGS_VALIDATION___------------------------------
#---------------------------------------------------------------------
class DataValidationError(Exception):
    pass

def validate_record(record):
    if not record.get("product_id"):
        raise DataValidationError("Missing product_id")
    if not record.get("dealer_id"):
        raise DataValidationError("Missing dealer_id")
    
def transform_sales_logs():
    
    processed = 0
    malformed_json = 0
    validation_failed = 0
    line_number = 0
    summary = {}
    log_info(f'STAGE = TRANSFORM | CREATING CLEAN AND REJECTED LOGS FOR SALES LOGS')
    with open(SALES_LOCAL_FILE, newline="") as f, open(CLEAN_SALES_LOGS_FILE,'w') as f_clean,open(REJECT_SALES_LOGS_FILE,'w') as f_reject,open(SUMMARY_SALES_LOGS_FILE,'w') as f_summary:
        
        for line in f:
            line_number+=1
            try:
                record = json.loads(line)

            except json.JSONDecodeError as e:
                malformed_json += 1
                log_error(f"[JSON ERROR] Line {line_number}: {e}")
                continue

            try:
                validate_record(record)
                f_clean.write(json.dumps(record)+'\n')

            except DataValidationError as e:
                validation_failed += 1
                f_reject.write(json.dumps(record)+'\n')
                log_error(f"[VALIDATION ERROR] Line {line_number}: {e}")
                continue

            processed += 1
        summary['Processed_Records'] = processed
        summary['Malformed JSON'] = malformed_json
        summary['Validation_Failures'] = validation_failed
        summary['status'] = "SUCCESS",
        summary['timestamp'] = datetime.now().isoformat()
        json.dump(summary,f_summary)
        log_info(f'STAGE = TRANSFORM | SUCCESSFULLY CREATED CLEAN AND REJECTED SALES LOGS')

# if __name__ == '__main__':
#     transform_dealer()
#     transform_product()
#     transform_inventory()
#     transform_sales_logs()
    