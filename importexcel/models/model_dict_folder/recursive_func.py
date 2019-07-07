 # -*- coding: utf-8 -*-
from odoo.addons.importexcel.models.model_dict_folder.tool_tao_instance import get_key,get_width,VERSION_INFO
from odoo.addons.downloadwizard.models.dl_models.dl_model  import header_bold_style
from collections import  OrderedDict
from odoo.exceptions import UserError
import re
import operator
from odoo import _
   

ATT_TYPE_LIST ={
  'default_val':[],
  'begin_data_row_offset_with_title_row': ['int'],
  'break_condition_func_for_main_instance': ['NoneType', 'function'],
  'bypass_this_field_if_value_equal_False': ['bool'],
  'inactive_include_search': ['bool'],
  'st_is_x2m_field': ['bool'],
  'remove_all_or_just_add_one_x2m': ['bool','str'],
  'bypass_this_field_if_value_equal_False_default': ['bool'],
  'st_write_false':['bool'], 
  'write_false':['bool'], 
  'col_index': ['int', 'NoneType'],
  'empty_val': ['list', 'NoneType'],
  'for_excel_readonly': ['bool'],
  'func': ['function', 'NoneType'],
  'func_check_if_excel_is_same_existence': ['function'],
  'func_map_database_existence': ['function'],
  'func_pre_func': ['NoneType'],
  'karg': ['dict'],
  'key': ['bool', 'str'],
  'key_allow': ['bool'],
  'last_import_function': ['NoneType', 'function'],
  'last_record_function': ['NoneType', 'function'],
  'model': ['str'],
  'offset_write_xl': ['int'],
  'only_get': ['bool'],
  'operator_search': ['str'],
#   'prepare_func': ['function'],
  'print_if_write': ['bool'],
  'print_write_dict_new': ['bool'],
  'raise_if_False': ['bool'],
  'raise_if_diff': ['bool'],
  'replace_string': ['list'],
  'replace_val': ['dict'],
  'required': ['bool'],
  'required_force': ['bool'],
  'required_when_check_file': ['bool'],
  'requried': ['bool'],
  'search_func': ['function'],
  'set_is_largest_map_row_choosing': ['bool'],
  'set_val': ['str', 'function', 'int', 'NoneType'],
  'setting': ['dict'],
  'setting2': ['dict'],
  'sheet_allow_this_field_not_has_exel_col': ['list'],
  'sheet_names': ['function','list'],
  'skip_field_if_not_found_column_in_some_sheet': ['bool', 'NoneType'],
  'skip_this_field': ['bool'],
  'string': ['str'],
  'title_rows': ['range', 'list'],
  'title_rows_some_sheets': ['dict'],
  'transfer_name': ['str'],
  'type_allow': ['list'],
  'valid_field_func': ['function', 'NoneType'],
  'write_field': ['bool', 'NoneType'],
  'xl_title': ['list', 'NoneType', 'str']
}

#R0  



def export_all_no_pass_dict_para(MD,out_dict={},type_out_dict={}):
    key_allow = MD.get('key_allow')
    export_all_keyval_by_key_tram(MD, out_dict = out_dict, type_out_dict = type_out_dict , key_allow= key_allow)
    type_out_dict = convert_dict_to_order_dict_string(type_out_dict)
    return out_dict, type_out_dict

  
def export_all_keyval_by_key_tram(MD, out_dict = {}, type_out_dict = {} , key_allow= False):
    for key,val in MD.items():
        if key != 'fields':
            if isinstance(val,dict) and key_allow:
                for key_tram,v in val.items():
                    append_val_type_n_val_of_key (out_dict, type_out_dict,key, v)
            else:
                append_val_type_n_val_of_key (out_dict, type_out_dict,key, val)
        elif val !=None:
            for fname, field_MD in val:
                export_all_keyval_by_key_tram(field_MD, out_dict = out_dict, type_out_dict=type_out_dict, key_allow=key_allow)
def convert_name_class_to_string(val):
    type_of_val = str(type(val))
    rs = re.search("<class '(\w*)'>",type_of_val)
    if rs:
        type_of_val = rs.group(1)
    else:
        print ('type_of_val **', type_of_val)
        raise UserError(type_of_val)
    return type_of_val
def append_val_type_n_val_of_key (out_dict, type_out_dict,key, val):
    list_of_val = out_dict.setdefault(key,[])
    list_of_val.append(val)
    type_of_val = str(type(val))
    rs = re.search("<class '(.*)'>",type_of_val)
    if rs:
        type_of_val = rs.group(1)
    else:
        print ('type_of_val', type_of_val)
        raise UserError('search theo partern khong ra %s'%type_of_val)
    list_of_type_of_val = type_out_dict.setdefault(key,[])
    if type_of_val not in list_of_type_of_val:
        list_of_type_of_val.append(type_of_val)
def convert_dict_to_order_dict_string(x):
    sorted_x = sorted(x.items(), key=lambda kv: kv[0])
    new = map(lambda kv:u"'%s':%s"%(kv[0],kv[1]),sorted_x)
    new = u', '.join(new)
    new = '{%s}'%new
    return new

###########!R0###############



# R1


def rut_gon_key(MD, key_tram): 
    for key, val in MD.items():
        if key != 'fields':
            val = convert_val_depend_key_tram(val, key_tram)
            MD[key] = val
        else :
            fields = MD['fields']
            if isinstance(fields, dict):
                fields_depend_tram = convert_val_depend_key_tram(MD, 'fields', key_tram)
                val =fields_depend_tram
                MD['fields'] = val
            field_tuple_lists = val
            if field_tuple_lists != None: # xem lại có khi nào bằng None không
                for fname, field_MD in field_tuple_lists: 
                    rut_gon_key(field_MD, key_tram)
                    
def convert_val_depend_key_tram(value, key_tram):
    if isinstance(value, dict) and key_tram:
        value =  value.get(key_tram) if key_tram in value else value.get('all_key_tram')
    return value

                    
###R2
def ordereddict_fields(MD):
    field_tuple_lists = MD['fields']
    for fname, field_MD in field_tuple_lists:
        if field_MD.get('fields'):
            new_ordered_dict = ordereddict_fields (field_MD)
    MD['fields']=OrderedDict(field_tuple_lists)
    
#R2A             
def check_xem_att_co_nam_ngoai_khong(MD):
    for attr, val in MD.items():
        if attr != 'fields':
            if not check_set_val_is_true_type(attr, val):
                raise UserError (u'attr %s val %s không thỏa hàm check_set_val_is_true_type'%(attr,val))
        elif attr =='fields' and val!=None : 
            for fname, field_MD in val.items():
                check_xem_att_co_nam_ngoai_khong(field_MD)
#R2A1
STRING_TYPE_DICT = {str:'str' ,bool:'bool', list:'list',dict:'dict',int:'int', }       
def check_set_val_is_true_type(attr, val):
    allow_type_list = ATT_TYPE_LIST.get(attr)
    if  allow_type_list==None:
        raise UserError(u'attr:%s chưa có liệt kê  trong ATT_TYPE_LIST'%attr)
    if allow_type_list ==[]:
        return True
    if  callable(val):
        str_val_type = 'function'
    elif val == None :
        return True
    else:
        str_val_type =convert_name_class_to_string(val)
    if str_val_type not in allow_type_list:
        raise UserError (u'attr %s val %s, type:%s, không đúng dữ liệu %s'%(attr,val, str_val_type, allow_type_list))
        return False
    else:
        return True    
#R3
def add_model_n_type_n_required_to_fields(self, MD, field_stt = 0, setting={}):# add x2m_fields
    model_name = get_key(MD, 'model')
    OBJ = self.env[model_name]
    fields= OBJ._fields
    default_dict = OBJ.default_get(fields)
    
    
    for f_name, field_MD in MD.get('fields').items():
        field_stt +=1
        f_name = get_key(field_MD, 'transfer_name') or  f_name
        skip_this_field = get_key(field_MD, 'skip_this_field',False)
        if not skip_this_field:
            if f_name not in fields and not field_MD.get('for_excel_readonly'):
                raise UserError(u'f_name:"%s" không nằm trong fields, phải thêm thược tính for_excel_readonly-field_attr:%s'%(f_name, field_MD))
            
#             bypass_this_field_if_value_equal_False = field_MD.get('bypass_this_field_if_value_equal_False',False)
#             key = field_MD.get('key', False)
#             if key and bypass_this_field_if_value_equal_False:
#                 raise UserError(u'key and bypass_this_field_if_value_equal_False')
            st_write_false = setting['st_write_false']
            write_false = field_MD['write_false'] if 'write_false' in field_MD else st_write_false
            field_MD['write_false'] = write_false
            field_MD['field_stt'] = field_stt
            
            if not field_MD.get('for_excel_readonly') :# and not skip_this_field
                try:
                    field = fields[f_name]
                except:
                    raise UserError(u'field %s không có trong  danh sách fields của model %s'%(f_name,model_name))
                field_MD['field_type'] = field.type
                if field.comodel_name:
                    field_MD['model'] = field.comodel_name
                
                if 'required' not in field_MD:
                    required_from_model = field.required
                    required_force = field_MD.get('required_force',None)
                    required = required_force or required_from_model
                    field_MD['required']= required
            default_val = field_MD.get('default_val')
            
            if f_name in default_dict and default_val ==None:
                default_val = default_dict[f_name]
                field_MD['default_val']=  default_val
            if field_MD.get('empty_val'):
                partern_empty_val =  '^('+  '|'.join(field_MD.get('empty_val')) +')$'
                field_MD['partern_empty_val'] = partern_empty_val
            if field_MD.get('fields'):
                    field_stt = add_model_n_type_n_required_to_fields(self,field_MD, field_stt =  field_stt, setting=setting)
            
            if 'st_is_x2m_field' in field_MD:
                x2m_fields = MD.setdefault('x2m_fields',[])
                x2m_fields.append(f_name)
            
            
    return field_stt
 # R4                
def define_col_index(title_rows, sheet, COPY_MODEL_DICT):
    row_title_index =None
    number_map_dict = {}
    for row in title_rows:
        if row >= sheet.nrows:
            break
        for col in range(0,sheet.ncols):
            if VERSION_INFO ==2:
                read_excel_value_may_be_title = unicode(sheet.cell_value(row,col))
            else:
                read_excel_value_may_be_title = str(sheet.cell_value(row,col))
            is_map_xl_title = add_col_index( COPY_MODEL_DICT, read_excel_value_may_be_title, col)
            if is_map_xl_title:
                row_title_index = row
                number_map_dict[row] =number_map_dict.get(row,0) + 1
    if not number_map_dict:
        raise UserError(u'number_map_dict rỗng')
    largest_map_row = max(number_map_dict.items(), key=operator.itemgetter(1))[0]
    return row_title_index,largest_map_row
# R4-1
def add_col_index(MD, read_excel_value_may_be_title,col):
    is_map_xl_title = False
    for fname, field_MD in MD.get('fields').items():
        is_real_xl_match_with_xl_excel = False
        xl_title = get_key(field_MD, 'xl_title')
        if get_key(field_MD, 'set_val') != None:
            continue
        if xl_title ==None and get_key(field_MD, 'col_index') !=None:
            continue# cos col_index
        elif field_MD.get('fields'):
            is_real_xl_match_with_xl_excel = add_col_index(field_MD, read_excel_value_may_be_title, col)
        elif xl_title:
            if isinstance(xl_title, list):
                xl_title_s = xl_title
            else:
                xl_title_s = [xl_title]
            for xl_title in xl_title_s:
                xl_title_partern = u'^%s$'%xl_title
                xl_title_partern = xl_title_partern.replace('\\','\\\\').replace('(','\(').replace(')','\)')
                is_map = re.search(xl_title_partern,read_excel_value_may_be_title,re.IGNORECASE)
                is_map = is_map or (xl_title==read_excel_value_may_be_title)
                if is_map:
                    field_MD['col_index'] = col
                    is_real_xl_match_with_xl_excel = True        
        is_map_xl_title = is_map_xl_title or is_real_xl_match_with_xl_excel
    return is_map_xl_title #or is_map_xl_title_foreinkey
#R5           
def check_col_index_match_xl_title(self, MD, needdata):
    for fname, field_MD in MD.get('fields').items():
        skip_this_field = get_key(field_MD, 'skip_this_field', False)
        if not skip_this_field: 
            col_index = get_key(field_MD, 'col_index', None)
            xl_title = get_key(field_MD, 'xl_title')#moi them , moi bo field_attr.get('xl_title')
            set_val = get_key( field_MD,'set_val')
            func = field_MD.get('func')
            check_col_index_match_xl_title_for_a_field( field_MD, xl_title, col_index, set_val, needdata, fname, func)
            if field_MD.get('fields'):
                check_col_index_match_xl_title(self, field_MD, needdata)
#R51
def check_col_index_match_xl_title_for_a_field(field_attr, xl_title, col_index, set_val, needdata, field_name, func):
#         if col_index or set_val or func:
#             pass
        if xl_title and set_val:
            raise UserError("xl_title and set_val")
        if set_val==None:
            if col_index==None:
                if xl_title : # không match
                    sheet_allow_this_field_not_has_exel_col = get_key( field_attr,'sheet_allow_this_field_not_has_exel_col')
                    skip_field_if_not_found_column_in_some_sheet = get_key(field_attr,'skip_field_if_not_found_column_in_some_sheet')
                    
                    skip_if_not_match =  skip_field_if_not_found_column_in_some_sheet or (sheet_allow_this_field_not_has_exel_col and needdata['sheet_name'] in sheet_allow_this_field_not_has_exel_col)
                    if not skip_if_not_match:
                        raise UserError(_(u'Excel not has column one in %s of %s, please change column name match with them') %(xl_title,field_name))
                else:
                    
                    if  field_attr.get('model'):
                        if not func and not field_attr.get('fields'):
                            raise UserError(u'model thì phải có ít nhất func và fields')
                    else:
                        if not func:
                            raise UserError (u' sao khong có col_index và  không có func luôn field %s attrs %s'%(field_name,u'%s'%field_attr))
#R5A
def write_get_or_create_title(MD, sheet, sheet_of_copy_wb, title_row):
    fields = MD['fields']
    for fname, field_MD in fields.items():
        offset_write_xl = get_key(field_MD, 'offset_write_xl')
        if offset_write_xl !=None:
            col =  sheet.ncols + offset_write_xl 
            title = field_MD.get('string', fname)  + u' sẵn hay tạo'
            sheet_of_copy_wb.col(col).width =  get_width(len(title))
            sheet_of_copy_wb.write(title_row, col, title, header_bold_style)
        if field_MD.get('fields'):
            write_get_or_create_title(field_MD, sheet,sheet_of_copy_wb,title_row)
        


#R7        
def export_some_key_value_cua_fields_MD(MD, attr_muon_xuats = ['field_type'], ghom_dac_tinh = {}):
    fields = MD['fields']
    output_field_dicts = {}
    for field, field_MD in fields.items():
        new_field_MD = {}
        for exported_key in attr_muon_xuats:
            if exported_key in field_MD:
                val = field_MD.get(exported_key)
                new_field_MD[exported_key] = val
                alist = ghom_dac_tinh.setdefault( exported_key, [])
                if val not in alist:
                    alist.append(val)
        if 'fields' in field_MD and field_MD.get('fields') != None :
            child_dict,ghom_dac_tinh  = export_some_key_value_cua_fields_MD(field_MD, attr_muon_xuats, ghom_dac_tinh)
            new_field_MD['fields'] = child_dict
        output_field_dicts[field] = new_field_MD 
    return output_field_dicts, ghom_dac_tinh
# 
# 
# 
# #R8
# def export_all_key_value_cua_fields_MD(MD, dac_tinhs = {}):
#     fields = MD['fields']
#     for fname, field_MD in fields.items():
#         for key,val in field_MD.items():
#             a_dt_list = dac_tinhs.setdefault(key,[])
#             if val not in a_dt_list :
#                 a_dt_list.append(val)
#         if 'fields' in field_MD:
#             export_all_key_value_cua_fields_MD(field_MD, dac_tinhs)






                   
                   



                

            
            
            

                
                        
            
            







                    
                    
                    



            

                                    
    
        
        











                

    

                
                




