 # -*- coding: utf-8 -*-
from odoo.addons.importexcel.models.model_dict_folder.tool_tao_instance import get_key
from odoo.osv import expression
import datetime
from odoo import  fields
from odoo.exceptions import UserError
from odoo.addons.downloadwizard.models.dl_models.dl_model  import wrap_center_vert_border_style
from odoo.tools.float_utils import float_compare, float_round

def get_or_create_object_has_x2m (self, class_name, 
                                search_dict,
                                write_dict ={},
                                noti_dict=None,
                                inactive_include_search = False,
#                                 x2m_field=False,
                                model_dict = {},
                                exist_val=False,
                                setting= {},
                                check_file = False,
                                is_search = True,
                                is_create = True,
                                is_write = True,
                                sheet_of_copy_wb_para = None
                                 ):
    x2m_fields = model_dict.get('x2m_fields')
    if x2m_fields:
        x2m_field = x2m_fields[0]
        x2m_values = search_dict[x2m_field]
        result = []
        get_or_create = False
        for val in x2m_values:
            search_dict[x2m_field] = val #
            obj, get_or_create_iterator = get_or_create_object_sosanh(self, 
                                    class_name, 
                                    search_dict,
                                    write_dict =write_dict,
                                    noti_dict=noti_dict,
                                    inactive_include_search = inactive_include_search,
                                    model_dict = model_dict,
                                    exist_val=exist_val,
                                    setting = setting,
                                    check_file = check_file,
                                    is_search = is_search,
                                    is_create = is_create,
                                    is_write = is_write,
                                    sheet_of_copy_wb_para = sheet_of_copy_wb_para
                                    )
            result.append(obj.id)
            get_or_create |=get_or_create_iterator
        remove_all_or_just_add_one_x2m = model_dict.get('remove_all_or_just_add_one_x2m', 'add_one')
        if remove_all_or_just_add_one_x2m == 'remove_all':
            obj_id =  [(6,False,result)]
        else:
            obj_id  = list(map(lambda x: (4,x,False), result)) # [(4,result[0],False)] 
    else:
        obj, get_or_create =  get_or_create_object_sosanh(self, class_name, search_dict,
                                    write_dict =write_dict,
                                    noti_dict=noti_dict,
                                    inactive_include_search = inactive_include_search,
                                    model_dict = model_dict,
                                    exist_val=exist_val,
                                    setting = setting,
                                    check_file = check_file,
                                    is_search = is_search,
                                    is_create = is_create,
                                    is_write = is_write,
                                    sheet_of_copy_wb_para = sheet_of_copy_wb_para,
                                    )
        

        if obj != None and  obj != False:
            obj_id = obj.id
        else:
            obj_id = obj
    return obj, obj_id, get_or_create



        

def get_or_create_object_sosanh(self, class_name,
                                search_dict,
                                write_dict ={},
                                noti_dict=None,
                                inactive_include_search = False,
                                model_dict = {},
                                exist_val=False,
                                setting = {},
                                check_file=False,
                                is_search = True,
                                is_create = True,
                                is_write = True,
                                sheet_of_copy_wb_para = None
                                ):
    search_dict_new = {}
    write_dict_new = {}
    if noti_dict !=None:
        this_model_noti_dict = noti_dict.setdefault(class_name,{})
   
    if is_search:
        this_model_noti_dict['search'] = this_model_noti_dict.get('search',0) + 1
        search_func = model_dict.get('search_func')
        
        if search_func:
            searched_object = search_func(self, model_dict, setting)
            if not searched_object and is_create:
                
                for f_name in search_dict:
                    field_attr = model_dict['fields'][f_name]
                    val =  search_dict[f_name]
                    f_name = get_key(field_attr, 'transfer_name') or f_name
                    search_dict_new[f_name] =  val
        else:
            if search_dict :
                pass
            else:
                raise UserError(u'Không có Key search dict, model_name%s----MD%s'%(class_name, model_dict))
            if inactive_include_search:
                domain_not_active = ['|',('active','=',True),('active','=',False)]
            else:
                domain_not_active = []
                
            domain = []
            break_condition = False
           
            
            for f_name in search_dict:
                field_attr = model_dict['fields'][f_name]
                val =  search_dict[f_name]
                if val == None:
                    if check_file:
                        searched_object, get_or_create =  None, False
                        break_condition = True
                        break
                    else:
                        raise UserError(u'val không thể bằng None')
                f_name = get_key(field_attr, 'transfer_name') or f_name
                operator_search = field_attr.get('operator_search','=')
                tuple_in = (f_name, operator_search, val)
                domain.append(tuple_in)
                if is_create:
                    search_dict_new[f_name] =  val
            
            if not break_condition:
                domain = expression.AND([domain_not_active, domain])
                searched_object  = self.env[class_name].search(domain)
            
        return_obj = searched_object 
        get_or_create = bool(searched_object)
        if get_or_create:
            this_model_noti_dict['search_yes'] = this_model_noti_dict.get('search_yes',0) + 1
        else:
            this_model_noti_dict['search_no'] = this_model_noti_dict.get('search_no',0) + 1
    else:
        return_obj = None 
        get_or_create = None
    
    if is_create:
        if not searched_object  :#create
            only_get = get_key(model_dict,'only_get')
            if only_get:
                raise UserError(u'Model %s này chỉ được get chứ không được tạo'%class_name)
            for f_name,val in write_dict.items():
                field_attr = model_dict['fields'][f_name]
                f_name = get_key(field_attr, 'transfer_name') or f_name
                search_dict_new[f_name]=val
            created_object = self.env[class_name].create(search_dict_new)

            this_model_noti_dict['create'] = this_model_noti_dict.get('create', 0) + 1
           
            
            return_obj =  created_object
            return return_obj,get_or_create
    allow_write_all_field = setting['allow_write']
    if is_write or check_file :  
        if exist_val:
            searched_object = exist_val
        if searched_object :# write
            if len(searched_object) > 1:
                raise UserError (u' exist_val: %s len(searched_object) > 1, searched_object: %s'%(exist_val,searched_object))
            
            for f_name, val in write_dict.items():
                field_MD= model_dict['fields'][f_name]
                if check_file and  field_MD.get('offset_write_xl') ==None:
                    continue
                if not check_file and (field_attr.get('val_goc') ==False and not field_attr.get('write_false')):
                    continue
                    
                f_name = get_key(field_attr, 'transfer_name') or f_name
                if check_file:
                    is_write_this_field = False
                else:
                    is_write_this_field = field_attr.get('write_field')
                    is_write_this_field = allow_write_all_field if is_write_this_field == None else is_write_this_field
                if not check_file and not is_write_this_field :
                    continue
                orm_field_val = getattr(searched_object, f_name)
                diff = check_diff_write_val_with_exist_obj(orm_field_val, val, field_attr)
                if diff:
                    if is_write_this_field:
                        write_dict_new[f_name] = val
                    if check_file:
                        diff_show = 'Khac orm:%s-dict:%s'%(orm_field_val, val)
                else:
                    if check_file:
                        diff_show = 'Giong orm:%s-dict:%s'%(orm_field_val, val)
                if check_file:
                    sheet_of_copy_wb = sheet_of_copy_wb_para['sheet_of_copy_wb']
                    sheet_of_copy_wb.write(sheet_of_copy_wb_para['row'], sheet_of_copy_wb_para['sheet'].ncols + field_MD.get('offset_write_xl'), diff_show, wrap_center_vert_border_style)
            if write_dict_new:
                searched_object.write(write_dict_new)
                this_model_noti_dict['update'] = this_model_noti_dict.get('update',0) + 1
            else:#'not update'
                this_model_noti_dict['skipupdate'] = this_model_noti_dict.get('skipupdate',0) + 1
        
    return return_obj, get_or_create# bool(searched_object)

def check_diff_write_val_with_exist_obj(orm_field_val, field_dict_val, field_attr):
    is_write = False
    
    if isinstance(orm_field_val, datetime.date):
        converted_orm_val_to_dict_val = fields.Date.from_string(orm_field_val)
    elif isinstance(orm_field_val, datetime.datetime):
        converted_orm_val_to_dict_val = fields.Datetime.from_string(orm_field_val)
    else:
        try:
            converted_orm_val_to_dict_val = getattr(orm_field_val, 'id', orm_field_val)
            if converted_orm_val_to_dict_val == None: #recorderset.id ==None when recorder set = ()
                converted_orm_val_to_dict_val = False
        except:
            converted_orm_val_to_dict_val = orm_field_val
    if field_attr.get('field_type')=='float':
        is_write = float_compare(orm_field_val, field_dict_val, precision_rounding=0.01)
    else:
        if converted_orm_val_to_dict_val != field_dict_val:
            is_write = True
    return is_write
    
                
                

