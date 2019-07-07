 # -*- coding: utf-8 -*-
import re
import xlrd
from odoo.exceptions import UserError
import base64
from copy import deepcopy
from xlutils.copy import copy
from odoo.addons.importexcel.models.model_dict_folder.tool_tao_instance import read_excel_cho_field, check_is_string_depend_python_version, empty_string_to_False, get_key#,get_width,header_bold_style,VERSION_INFO
from odoo.addons.downloadwizard.models.dl_models.dl_model  import wrap_center_vert_border_style
from odoo.addons.importexcel.models.model_dict_folder.get_or_create_func import get_or_create_object_has_x2m
from odoo.addons.importexcel.models.model_dict_folder.recursive_func import export_all_no_pass_dict_para,rut_gon_key,ordereddict_fields, check_xem_att_co_nam_ngoai_khong, add_model_n_type_n_required_to_fields,define_col_index,check_col_index_match_xl_title,write_get_or_create_title, convert_dict_to_order_dict_string, export_some_key_value_cua_fields_MD 

def before_ci(self, field_attr, setting, check_file, needdata):
    func_map_database_existence = setting.get('st_allow_func_map_database_existence') and field_attr.get('func_map_database_existence')
    if func_map_database_existence:
        exist_val = func_map_database_existence(needdata,self) 
    else:
        exist_val = False
    if exist_val:
        st_is_allow_write_existence = setting['st_is_allow_write_existence']
        func_check_if_excel_is_same_existence =   setting.get('st_allow_check_if_excel_is_same_existence') and  field_attr.get('func_check_if_excel_is_same_existence') 
    
    is_go_loop_fields = not exist_val or (exist_val and (func_check_if_excel_is_same_existence or st_is_allow_write_existence)) or check_file
    if is_go_loop_fields:
        if check_file:
            is_search = True
            is_create = False
            is_write = False
        else:
            if exist_val:
                if st_is_allow_write_existence:
                    is_create = False
                    is_write = True
                else:
                    is_create = False
                    is_write = False
                if func_check_if_excel_is_same_existence:
                    is_search = True
                else:
                    is_search = False
                
                    
            else:
                is_create = True
                is_write = True
                is_search =True
    return is_create, is_write, is_search, exist_val, is_go_loop_fields
                
def after_ci(setting, exist_val, field_attr, check_file, sheet_of_copy_wb, row, sheet, get_or_create, obj, noti_dict):
    if exist_val:
        func_check_if_excel_is_same_existence =   setting.get('st_allow_check_if_excel_is_same_existence') and  field_attr.get('func_check_if_excel_is_same_existence')
        if  func_check_if_excel_is_same_existence:# and not get_or_create:,not st_is_allow_write_existence and
            func_check_if_excel_is_same_existence(get_or_create, obj, exist_val)
        val= exist_val.id
        obj = exist_val
        get_or_create = True
        this_model_notice = noti_dict.setdefault(field_attr.get('model'),{})
        this_model_notice['exist_val'] = this_model_notice.get('exist_val',0) + 1
    field_attr['get_or_create'] = get_or_create
    
    if check_file:
#             if val ==False or val ==None:
#                 val = None
        offset_write_xl = get_key(field_attr, 'offset_write_xl')
        if offset_write_xl !=None:
            if get_or_create:
                get_or_create_display = u'Đã Có' 
            else:
                if field_attr['fields']['name']['val'] !=False:
                    get_or_create_display = u'Chưa'
                else:
                    get_or_create_display = u'empty cell'
            sheet_of_copy_wb.write(row, sheet.ncols + offset_write_xl, get_or_create_display, wrap_center_vert_border_style)
                
def gen_first_last_row(self, MD, row_title_index,nrows, dong_test_in_MD):
            off_set_row = get_key(MD, 'begin_data_row_offset_with_title_row', 1)
            min_row = row_title_index + off_set_row
            first_row = min_row + getattr(self,'begin_row',0)
            print ('first_row','min_row',first_row,min_row)
            dong_test = getattr(self,'dong_test',None) or dong_test_in_MD
            if not dong_test:
                last_row = nrows
            else:
                last_row = first_row + dong_test
            if last_row > nrows:
                last_row =  nrows
            if first_row >  last_row :
                raise UserError(u'first_row >  last_row')
            return first_row,last_row

def xac_dinh_title_rows(self,MD,set_is_largest_map_row_choosing, nrows, sheet_name):
            range_1 = getattr(self, 'range_1',None)
            range_2 = getattr(self, 'range_2',None)
            
            if range_1 or range_2:
                title_rows = range(range_1,range_2)
            else:
            
                if set_is_largest_map_row_choosing:
                    title_rows = range(0,nrows)
                else:
                    title_rows_some_sheets = MD.get('title_rows_some_sheets',{})
                    if title_rows_some_sheets:
                        title_rows_some_sheets=title_rows_some_sheets.get(sheet_name)
                    if title_rows_some_sheets:
                        title_rows = title_rows_some_sheets
                    else:
                        title_rows = get_key(MD, 'title_rows')  # MODEL_DICT['title_rows']
            return title_rows
        
def gen_sheet_names(self,MD, xl_workbook, gen_model_dict_kargs):
        sheet_names = get_key(MD, 'sheet_names')
        if callable(sheet_names):
            try:
                sheet_names = sheet_names(self)
            except TypeError as e:
                if 'required positional argument' in u'%s'%e:
                    try:
                        sheet_names = sheet_names(self,xl_workbook)
                    except TypeError as e:
                        if 'required positional argument' in u'%s'%e:
                            sheet_names = sheet_names(self,xl_workbook, gen_model_dict_kargs )
                        else:
                            raise UserError(u'có 1 lỗi ở hàm sheet_names: %s '%e)
                else:
                        raise UserError(u'có 1 lỗi ở hàm sheet_names: %s '%e)    
        return sheet_names
# from odoo.addons.importexcel.models.model_dict_folder.recursive_func import tim_type_cua_attr
def importexcel_func(odoo_or_self_of_wizard, key=False, key_tram=False, check_file = False, gen_model_dict_kargs= {}):
    self = odoo_or_self_of_wizard
    key_tram =  getattr(self,'key_tram',False) or key_tram
    new_dict = self.env['importexcel.importexcel'].gen_model_dict()
    key = key or self.type_choose
    MD = new_dict[key]
    
#     if 'cach_tim_location_goc' not in gen_model_dict_kargs:
    cach_tim_location_goc = getattr(self, 'cach_tim_location_goc', 'find_origin_location_by_key_tram' )
    if cach_tim_location_goc:
        gen_model_dict_kargs['cach_tim_location_goc'] = cach_tim_location_goc

    if callable(MD):
        MD = MD(self=self, key_tram=key_tram, gen_model_dict_kargs=gen_model_dict_kargs)
    key_allow = MD.get('key_allow',False)
    key_tram = key_allow and key_tram
    if key_allow and not key_tram:
        raise UserError(u'ban phai chon key_tram')
    
    
#     rs = self.env['importexcel.importexcel'].gen_model_dict()
#     out_dict = {}
#     type_out_dict = {}
#     for k,MD_test in rs.items():
#     #R0
#         if callable(MD_test):
#             MD_test = MD_test(self=self, key_tram=key_tram, gen_model_dict_kargs=gen_model_dict_kargs)
#         key_allow = MD_test.get('key_allow',False)
#         export_all_no_pass_dict_para(MD_test, out_dict=out_dict, type_out_dict=type_out_dict)
#     raise UserError(u'%s%s%s'%(str(out_dict), '***'*8, str(type_out_dict)))




    if not self.file:
        raise UserError(u'Bạn phải upload file để import')
    file_content = base64.decodestring(self.file)
    if '.xlsx' in self.filename:
        formatting_info = False
    else:
        formatting_info = True
    xl_workbook = xlrd.open_workbook(file_contents = file_content, formatting_info=formatting_info)
    
    noti_dict = {}
    
    #R1
    rut_gon_key(MD,key_tram)
    print ('***MD***',MD)
    
    #R2
    ordereddict_fields( MD)
    #R2A
    check_xem_att_co_nam_ngoai_khong(MD)
    
    setting = MD.get('setting',{})
    setting.setdefault('allow_write',MD.get('allow_write', True))
#     setting['bypass_this_field_if_value_equal_False_default'] =  MD.get('bypass_this_field_if_value_equal_False_default',False)

    setting.setdefault('st_write_false', False)
    setting['st_write_false'] =  MD.get('st_write_false')
    setting2 = MD.get('setting2',{})
    if setting2:
        setting.update(setting2)
    self.setting = convert_dict_to_order_dict_string(setting)
    
    
    #R3
    add_model_n_type_n_required_to_fields(self, MD, setting = setting)
   
    imported_model = self.env[MD.get('model')]
    rs = imported_model.default_get([])#imported_model._fields)
    
    
    
    
    
    a,b = export_some_key_value_cua_fields_MD(MD, attr_muon_xuats = ['partern_empty_val'], ghom_dac_tinh = {})
    
    
    
#     raise UserError(u'%s-%s'%(a,b))
    
    needdata = {}
    needdata['self'] = self
    
    
    sheet_names=gen_sheet_names(self,MD, xl_workbook, gen_model_dict_kargs)
    needdata['sheet_names'] = sheet_names
    needdata['key_tram'] = key_tram
    


    

    
    
    
#     prepare_func = MD.get('prepare_func')
#     if prepare_func:
#         prepare_func(needdata,self)
#     
    
    sh_names = xl_workbook.sheet_names()
    if check_file:
        workbook_copy = copy(xl_workbook)
    for sheet_name in sheet_names:
#         print ('**sheet_name',sheet_name)
        COPIED_MD = deepcopy(MD)
        needdata['vof_dict'] = COPIED_MD.get('fields') 
        needdata['sheet_name'] = sheet_name

        sheet = xl_workbook.sheet_by_name(sheet_name)
        
        
        set_is_largest_map_row_choosing = MD.get( 'set_is_largest_map_row_choosing')#set_is_largest_map_row_choosing  is boolean
        nrows = sheet.nrows
        title_rows = xac_dinh_title_rows(self,MD,set_is_largest_map_row_choosing, nrows, sheet_name)
        
                    
                    
        #R4
        row_title_index,largest_map_row = define_col_index(title_rows, sheet, COPIED_MD)
        if set_is_largest_map_row_choosing:
            row_title_index = largest_map_row

        #R5
        check_col_index_match_xl_title(self, COPIED_MD, needdata)
        
        
        #tim kiem first_row,last_row
        
        dong_test_in_MD = MD.get('dong_test')
        first_row,last_row = gen_first_last_row(self, MD, row_title_index,nrows, dong_test_in_MD)
        
        if check_file:
            index = sh_names.index(sheet_name)
#             sheet_of_copy_wb = workbook_copy.get_sheet(0)
            sheet_of_copy_wb = workbook_copy.get_sheet(index)
            write_get_or_create_title(MD,sheet,sheet_of_copy_wb, row_title_index)
#             is_search = True
#             is_create = False
#             is_write = False
        else:
#             is_search = True
#             is_create = True
#             is_write = True
            workbook_copy = None
            sheet_of_copy_wb = None
        
        merge_tuple_list =  sheet.merged_cells
        for number_row_count,row in enumerate(range(first_row, last_row)):
            print ('sheet_name*******',sheet_name,'row',row)
            create_instance (self, COPIED_MD, 
                                              sheet, 
                                              row, 
                                              merge_tuple_list, 
                                              needdata, 
                                              noti_dict,
#                                               main_call_create_instance_model=True,
#                                               key_tram=key_tram,
                                              check_file = check_file,
                                              sheet_of_copy_wb = sheet_of_copy_wb,
                                              setting=setting,
#                                               is_search = is_search,
#                                               is_create = is_create,
#                                               is_write = is_write,
                               )
        
    if number_row_count:
        self.imported_number_of_row = number_row_count + 1
    
    
#     last_import_function  = get_key(MD,'last_import_function')
#     if last_import_function:
#         last_import_function(needdata,self)
    self.log= noti_dict
    return workbook_copy
    
            
################# CREATE INSTANCE
def create_instance (self,
                    MD,
                    sheet,
                    row,
                    merge_tuple_list,
                    needdata,
                    noti_dict, 
#                     main_call_create_instance_model = False,
                    check_file = False,
                    sheet_of_copy_wb = False,
                    setting={},
#                     exist_val = False,
#                     is_search = True,
#                     is_create = True,
#                     is_write = True,
                    ):
        
    key_search_dict = {}
    update_dict = {}
    model_name = MD.get( 'model')
    collection_dict = {}
    is_create, is_write, is_search, exist_val, is_go_loop_fields = before_ci(self,MD, setting, check_file, needdata)
    if is_go_loop_fields:
        for field_name,field_attr  in MD['fields'].items():
            a_field_code = get_a_field_val(self,
                                           field_name,
                                           field_attr,
                                           needdata,
                                           row,
                                           sheet,
                                           check_file,
                                           sheet_of_copy_wb,
                                           merge_tuple_list,
                                           model_name,
                                           noti_dict,
                                           key_search_dict,
                                           update_dict,
                                           collection_dict,
                                           setting)
            if a_field_code =='break_out_a_row_because_a_required':
                if field_attr.get('raise_if_False') and not check_file:
                    raise UserError('raise_if_False field: %s'%field_name)
                break
        if a_field_code =='break_out_a_row_because_a_required':
#             if main_call_create_instance_model:
            break_condition_func_for_main_instance  = get_key(MD, 'break_condition_func_for_main_instance')
            if break_condition_func_for_main_instance:
                break_condition_func_for_main_instance(needdata)
            obj = False
            obj_val = False
            get_or_create = None
        elif collection_dict.get('instance_false'):# có 1 field = false and required ==> instance đó = False
            obj, obj_val, get_or_create =  False, False, None
        
        else:
            obj, obj_val, get_or_create  = get_or_create_instance_from_key_search_and_update_dict(
                                                    self,
                                                    model_name,
                                                    key_search_dict,
                                                    update_dict,
                                                    check_file,
                                                    noti_dict,
                                                    MD,
                                                    exist_val=exist_val,
                                                    setting=setting,
                                                    is_search = is_search,
                                                    is_create = is_create,
                                                    is_write = is_write,
                                                       )
    
    
#     after_ci(exist_val,func_check_if_excel_is_same_existence, field_attr, check_file, sheet_of_copy_wb, row, sheet, get_or_create, obj, noti_dict)


    if exist_val:
        func_check_if_excel_is_same_existence =   setting.get('st_allow_check_if_excel_is_same_existence') and  MD.get('func_check_if_excel_is_same_existence')
        if  func_check_if_excel_is_same_existence:# and not get_or_create:,not st_is_allow_write_existence and
            func_check_if_excel_is_same_existence(get_or_create, obj, exist_val)
        obj_val= exist_val.id
        obj = exist_val
        get_or_create = True
        this_model_notice = noti_dict.setdefault(MD.get('model'),{})
        this_model_notice['exist_val'] = this_model_notice.get('exist_val',0) + 1
    MD['get_or_create'] = get_or_create
    if check_file:
#             if val ==False or val ==None:
#                 val = None
        offset_write_xl = get_key(MD, 'offset_write_xl')
        if offset_write_xl !=None:
            if get_or_create:
                get_or_create_display = u'Đã Có' 
            elif get_or_create == None:
                get_or_create_display = u'None'
                
            else:
                if 'name' not in MD['fields']:
                    get_or_create_display = u'Chưa'
                else:
                    if MD['fields']['name']['val'] !=False:
                        get_or_create_display = u'Chưa'
                    else:
                        get_or_create_display = u'empty cell'
            sheet_of_copy_wb.write(row, sheet.ncols + offset_write_xl, get_or_create_display, wrap_center_vert_border_style)
    #     if check_file:
    #         if obj_val == False:
    #             obj_val = None
#     last_record_function = get_key(MD, 'last_record_function')
#     if last_record_function:
#         last_record_function(needdata, self)
    return obj, obj_val, get_or_create 



#F1 
def get_a_field_val(self,
                                   field_name,
                                   field_attr,
                                   needdata,
                                   row,
                                   sheet,
                                   check_file,
                                   sheet_of_copy_wb,
                                   merge_tuple_list,
                                   model_name,
                                   noti_dict,
                                   key_search_dict,
                                   update_dict,
#                                    x2m_fields,
                                   collection_dict,
                                   setting,
                                   
                           ):
    skip_this_field = get_key(field_attr, 'skip_this_field', False)
    if callable(skip_this_field):
            skip_this_field = skip_this_field(self)
    if skip_this_field:
            return 'continue'
    col_index = get_key(field_attr, 'col_index')
    func = get_key( field_attr,'func')
    #F11
    obj,val = read_val_for_ci(self,
                    field_attr,
                    check_file,
                    needdata,
                    noti_dict,
                    setting,
                    excel_para = {'col_index':col_index,'sheet':sheet, 'row':row,'merge_tuple_list':merge_tuple_list,'sheet_of_copy_wb': sheet_of_copy_wb },
                    for_print_para= {'model_name':model_name, 'field_name':field_name}
                    )

    field_attr['before_func_val'] = val
    # func
    karg = get_key( field_attr,'karg',{})
    if karg ==None:
        karg ={}
    func_pre_func = field_attr.get('func_pre_func')
    if func_pre_func:
        val = func_pre_func(val, needdata,self)
    if func:
        try:
            val = func(val, needdata,**karg)
        except TypeError:
            try:
                val = func(val, needdata,self,**karg)
            except TypeError:
                val = func(val,**karg)
#         print ('func read model_name:%s field_name:%s'%(model_name,field_name),'val',val)
    
    val = replace_val_for_ci (field_attr,val,needdata)
    field_attr['val_goc'] = val
    if val == False:
        default_val = field_attr.get('default_val')
        if  default_val!=None:
            val = default_val
            
        
        
    
    field_attr['val'] = val
    field_attr['obj'] = obj
    if check_file:     
        required_when_normal  = get_key(field_attr, 'required', False)   
        required   = get_key(field_attr, 'required_when_check_file', required_when_normal) 
        if (required_when_normal and val==False) and required ==False:
            collection_dict['instance_false'] = True
    else:
        required = get_key(field_attr, 'required', False)  

   
    key_or_not = field_attr.get('key')
    if '2many' in field_attr.get('field_type','' ) and val == False:
        a_field_code = 'continue'
        return a_field_code
    if required and (val==False and isinstance(val, bool)):# val ==False <==> val ==0, val ==0 <==> val =False
        this_model_notice = noti_dict.setdefault(model_name,{})
        skip_because_required = this_model_notice.setdefault('skip_because_required',0)
        this_model_notice['skip_because_required'] = skip_because_required + 1
        a_field_code = 'break_out_a_row_because_a_required' 
        return  a_field_code#sua 5
    elif not field_attr.get('for_excel_readonly'):
        if key_or_not==True:
            key_search_dict [field_name] = val
        elif key_or_not == 'Both':
            key_search_dict [field_name] = val
            update_dict [field_name] = val
        else:
            update_dict [field_name] = val
    valid_field_func = field_attr.get('valid_field_func')
    if valid_field_func:
        valid_field_func(val,obj,needdata,self)
    print ("row: ", row,'model_name: ',model_name,'-field: ', field_name, '-val: ', val)
    check_type_of_val(field_attr, val, field_name, model_name)
    a_field_code = False
    return a_field_code        
#F2
def read_val_for_ci(self,
                    field_attr,
                    check_file,
                    needdata,
                    noti_dict,
                    setting,
                    excel_para = {},
                    for_print_para= {}
                    ):  
    col_index =excel_para['col_index'] 
    sheet =excel_para['sheet'] 
    row =excel_para['row'] 
    merge_tuple_list =excel_para['merge_tuple_list'] 
    sheet_of_copy_wb =excel_para['sheet_of_copy_wb'] 
    val = False
    obj = False
    set_val = get_key( field_attr,'set_val')
    if set_val != None:
        val = set_val

    elif col_index !=None: # đọc file exc
        xl_val = read_excel_cho_field(sheet, row, col_index, merge_tuple_list)
        xl_val = empty_string_to_False(xl_val)
        field_attr['excel_val'] = xl_val
        val = empty_string_to_False(xl_val)
        if field_attr.get('partern_empty_val'):
            val = empty_string_to_False(val, pt = field_attr.get('partern_empty_val'))
        
        if val != False and field_attr.get('is_x2m_field'):
            val = val.split(',')
            val = list(map(lambda i: empty_string_to_False(i.strip()),val))
            if False in val:
                    raise UserError(u'Không được có phần tử = False')
        print ('excel read model_name:%s field_name:%s'%(for_print_para['model_name'],for_print_para['field_name']),'xl_val',xl_val,'val',xl_val)
    
    elif field_attr.get('fields') :
#         before_ci()
        obj,val, get_or_create  = create_instance (self,
                                                                field_attr,
                                                                sheet, 
                                                                row, 
                                                                merge_tuple_list,
                                                                needdata, 
                                                                noti_dict,
                                                                check_file = check_file ,
                                                                sheet_of_copy_wb = sheet_of_copy_wb,
#                                                                 exist_val = exist_val,
                                                                setting=setting,
#                                                                 is_search = is_search,
#                                                                 is_create = is_create,
#                                                                 is_write = is_write,
                                                               )
#         after_ci()
        
    return obj, val      

def get_or_create_instance_from_key_search_and_update_dict(self,
                           model_name,
                           key_search_dict,
                           update_dict,
                           check_file,
                           noti_dict,
                           MODEL_DICT,
                           exist_val = False,
                           setting={},
                           is_search = True,
                           is_create = True,
                           is_write = True,#                            collection_dict={}
                           ):
    
    obj,obj_val, get_or_create = get_or_create_object_has_x2m(self, model_name,
                                                                    key_search_dict, 
                                                                    update_dict,
                                                                    noti_dict = noti_dict,
                                                                    inactive_include_search  = MODEL_DICT.get('inactive_include_search',False), 
                                                                    model_dict=MODEL_DICT,
                                                                    exist_val=exist_val,
                                                                    setting=setting,
                                                                    check_file=check_file,
                                                                    is_search = is_search,
                                                                    is_create = is_create,
                                                                    is_write = is_write,
                                
                                )
    return obj,obj_val, get_or_create 
    

            
def replace_val_for_ci(field_attr, val, needdata):
    
    #### deal replace string ####
    replace_string = get_key( field_attr,'replace_string')
    if  replace_string and check_is_string_depend_python_version(val):
        for pattern,repl in replace_string:
            pattern = pattern.replace('(','\(').replace(')','\)')
            val = re.sub(pattern, repl, val)
    #### end  deal replace string ####
    
    
    
    #### deal empty val ###
    empty_val = get_key( field_attr,'empty_val')
     
    if empty_val and val in empty_val:
        val = False   
    #### !!!deal empty val ###
    
    
    
    
    #### deal  replace val#####
    replace_val = get_key( field_attr,'replace_val')
    if replace_val:
        replace_val_tuple = replace_val.get(needdata['sheet_name']) or replace_val.get('all')
        if replace_val_tuple:
            for k,v in replace_val_tuple:
                if val ==k:
                    val = v
                    break
    #### !!!deal  replace val#####
                
    ### deal defautl ###
    
    
    ### !!!!deal defautl ###SS
    return val


def check_notice_dict_co_create_or_get(model_name,noti_dict,check_file):
    adict = noti_dict.get(model_name,{})
    if not adict.get('create') and not adict.get('update') and not check_file :
        raise UserError(u'các row bị bỏ qua hết không có dòng nào được tạo hoặc được update')
    
MAP_TYPE = {
                      'integer':[int,float],
                      'float':float, 
                      'many2one':int,
                      'char':str,
                      'selection':str,
                      'text':str, 
                      'boolean':bool,
                      'many2many':list,
                      'one2many':list,
                      
                      
                      }
def check_type_of_val(field_attr, val, field_name, model_name):        
    if field_attr.get('bypass_check_type'):
        return True
    field_type = field_attr.get('field_type')
    if field_type:
        type_allow = field_attr.get('type_allow',[])
        if val != False and val != None:
            try:
                type_tuong_ung_voi_char_field_type = MAP_TYPE[field_type]
            except:
                return True
                raise UserError(u'không có field_type:%s này'%field_type)
            if field_attr.get('is_x2m_field'):
                type_tuong_ung_voi_char_field_type = list
            if isinstance( type_tuong_ung_voi_char_field_type,list):
                type_allow.extend(type_tuong_ung_voi_char_field_type)
            else:
                type_allow.append(type_tuong_ung_voi_char_field_type)
            pass_type_check = False
            for a_type_allow in type_allow:
                if isinstance(val, a_type_allow):
                    pass_type_check = True
                    continue
            if not pass_type_check:
                raise UserError(u'model: %s- field:%s có giá trị: %s, đáng lẽ là field_type:%s nhưng lại có type %s'%(model_name, field_name,val,field_type,type(val)))
            

