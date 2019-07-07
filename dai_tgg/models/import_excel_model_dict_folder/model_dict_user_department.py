 # -*- coding: utf-8 -*-
from odoo.exceptions import UserError
import datetime
from odoo.addons.tutool.mytools import convert_vn_datetime_to_utc_datetime

def convert_vn_str_datetime_to_utc_str_datetime(v):
    if v:
        dt_v = datetime.datetime.strptime(v,'%d/%m/%Y %H:%M:%S')
        utc_v =  convert_vn_datetime_to_utc_datetime(dt_v)
        utc_str = utc_v.strftime('%d/%m/%Y %H:%M:%S')
        return utc_str
    return v
def cd_children_ids_(v,n,self):
    print ('val *** in ',v)
    v2 = []
    if v:
        for login in v:
            user = self.env['res.users'].search([('login','=',login)])
            if user:
                v2.append(user.id)
            else:
                raise UserError(u'Không có user là %s'%login)
        return v2
    return v
def gen_user_department_model_dict():
    user_model_dict = {
        u'Partner': {
                'title_rows' : [1], 
                'begin_data_row_offset_with_title_row' :1,
                'sheet_names': [u'Partner'],
                'model':'res.partner',
                'fields' : [
                         ('stt',{'func':None,'xl_title':u'stt','key':False,'required':True,'for_excel_readonly':True}),
                         ('name',{'func':None,'xl_title':u'Tên','key':False,'required':True}),
                        ('parent_id',{
                            'fields':[
                                                ('name',{'xl_title':u'Đơn vị','key':True,'required':True}),
                                                ('company_type',{'key':False, 'required': False, 'set_val':'company'}),
                                                       ]
                                            }
                         ),
                                               ('phone',{'func':None,'xl_title':u'phone','key':False, 'func': lambda v,n: str(int(v)) if isinstance(v,float) else v}),
                                               ( 'email',{'func':None,'xl_title':u'email','key':True ,'required_force':True}),
                                                
                                                ('job_id',{'key':False,'required':False,
                                       'fields':[
                                                ('name',{'xl_title':u'Chức vụ',  'key':True, 'required':True, 'func':lambda v,n: u'Nhân Viên' if v==False else v }),
                                                ]
                                       }),  
 
                      ]
                },            
        u'Department': {
        'title_rows' : [1], 
        'begin_data_row_offset_with_title_row' :1,
        'sheet_names': [u'Công Ty'],
        'model':'hr.department',
        'fields' : [
                ('name',{'func':None,'xl_title':u'công ty','key':True,'required':True}),
                ('report_name',{'func':None,'xl_title':u'report_name','key':False,'required':False}),
                ('short_name',{'func':None,'xl_title':u'short_name','key':False,'required':False}),
                ('parent_id',{'fields':[
                                              ('name',{'xl_title':u'parent_id','key':True,'required':True}),
                                               ]
                                    }
                 ),
                ('cong_ty_type',{'fields':[('name',{'xl_title':u'cong_ty_type','key':True,'required':True}),
                                               ]
                                    }
                 ),

                ('partner_id',{'key':False,'required':False,
                                   'fields':[
                                            ('name',{'xl_title':None,  'key':True, 'required': True, 'func':lambda val,needdata: needdata['vof_dict']['name']['val']}),
                                            ('company_type',{'xl_title':None,  'key':False, 'required': False, 'set_val':'company'}),
                                            ('parent_id',{'key':False,'required':False,
                                                               'fields':[
                                                                        ('name',{'xl_title':None,  'key':True, 'required_force': True, 'func':lambda val,needdata: needdata['vof_dict']['parent_id']['fields']['name']['val'] }),
                                                                        ('company_type',{'xl_title':None,  'key':False, 'required': False, 'set_val':'company'}),
                                                                        ]
                                   }),  
                 
                ]}),
                ('default_location_id',{'fields':[
                    ('name',{'xl_title':u'default_location_id','func':None,'key':True,'required':True}),
                    ('location_id',{'fields':[
                        ('stock_type',{'set_val':'dai'}),
                        ('name',{'key':True,'set_val':u'Đài HCM dự phòng'}),
                        ('stock_type',{'key':True,'set_val':u'dai'}),
                        ]}),
                    ('partner_id_of_stock_for_report',{'fields':[('name',{'func': lambda v,n:n['vof_dict']['name']['val'], 'key':True,'required':True}),
                                               ]
                                    }),
                    ('is_kho_cha',{'set_val':True}),
                    ('usage',{'xl_title':u'usage','func':None,'key':False,'required':False}),
                    ('stock_type',{'set_val':'tram'}),
                    ('department_id',
                         {'fields':[
                             ('name',{'func':lambda v,needdata:needdata['vof_dict']['name']['val'],'key':True,'required':True}),
                                    ]
                          }),
                                                                        ]
                                                            }
                 ),
                ('default_location_running_id',{'model':'stock.location','fields':[
                        ('name',{'xl_title':u'default_location_id_running','func':None,'key':True,'required':True}),
                        ('location_id',{'fields':[
                            ('stock_type',{'set_val':'dai'}),
                            ('name',{'key':True,'set_val':u'Đài HCM Đang chạy'}),
                            ('stock_type',{'key':True,'set_val':u'dai'}),
                            ]}),
                        ('usage',{'xl_title':u'usage','func':None,'key':False,'required':False}),
                        ('is_kho_cha',{'set_val':True}),
                        ('stock_type',{'set_val':'tram'}),
                        ('partner_id_of_stock_for_report',{'model':'res.partner','fields':[('name',{'func': lambda v,n:n['vof_dict']['name']['val'], 'key':True,'required':True}),
                                                   ]} ),
                        ('department_id',
                                             {'model':'hr.department','fields':[
                                                 ('name',{'func':lambda v,needdata:needdata['vof_dict']['name']['val'],'key':True,'required':True}),
                                                        ]
                                              }),
#                         ('location_id',{'model':'stock.location', 'fields':[('name',{'xl_title':u'location_id','key':True,'required':True}),]}), 
                                                                                ]
                                                                    }),
                ('kho_tam_id',{'inactive_include_search':True,'model':'stock.location','fields':[
                        ('name',{'xl_title':u'kho_tam','func':None,'key':True,'required':True}),
                        ('usage',{'xl_title':u'usage','func':None,'key':False,'required':False}),
                        ('active',{'set_val':True,'key':False,'required':False}),
                        ('is_kho_cha',{'set_val':True}),
                        ('stock_type',{'set_val':'tram'}),
                        ('location_id',{'func':lambda v,needdata:needdata['vof_dict']['default_location_id']['val'] }),
                        ('partner_id_of_stock_for_report',{'model':'res.partner','func':lambda v,needdata:needdata['vof_dict']['partner_id']['val']}),
                        ('department_id',
                                             {'model':'hr.department','fields':[
                                                 ('name',{'func':lambda v,needdata:needdata['vof_dict']['name']['val'],'key':True,'required':True}),
                                                        ]
                                              }),
                                                                                ]
                                                                    }),
                    
                       
                    
                    
                    
            
              ]
                },#End department
     u'User': {
        'title_rows' : [1], 
        'begin_data_row_offset_with_title_row' :2,
        'sheet_names': ['Sheet1'],
        'model':'res.users',
        'fields' : [
                ('name', {'func':None,'xl_title':u'Họ và Tên','key':True,'required':True}),
                ('login',{'func':None,'xl_title':u'Địa chỉ email','key':True ,'required':True}),
                ('password',{'func':None,'required':True,'set_val':'123456'}),
#                 ('lang',{'set_val':'vi_VN'}),
                ('phone',{'func':None,'xl_title':u'Số điện thoại','key':False}),
                ('cac_sep_ids',{'key':False,'required':False,'only_get':True,
                                        'fields':[
                                                 ('login',{'xl_title':u'Cấp trên',  'key':True, 'required':True, 'st_is_x2m_field':True}),
                                                 ]
                }),  
                ('groups_id',{'key':False,
                                    'required':False ,
                                    'bypass_this_field_if_value_equal_False':True,
                                    'remove_all_or_just_add_one_x2m': 'add_one',
                                    'fields':[
                                             ('name',{'xl_title':u'groups_id',  'key':True, 'required': True,'st_is_x2m_field':True}),     
                                              ]
                                    }
                 ),  
                 ('job_id',{'key':False,'required':False,
                                   'fields':[
                                                ('name',{'xl_title':u'Chức vụ',  'key':True, 'required':True, 'func':lambda v,n: u'Nhân viên' if v==False else v }),
                                               ]
                }),  
                ('department_id',{'key':False,'required':True,'raise_if_False':True,
                                           'fields':[
                                                    ('name',{'xl_title':u'Bộ Phận',  'key':True, 'required': True}),
                                                    ]
                                                 }),  
                ('partner_id',{'key':False,'required':False,
                               'fields':[
                                            ('name',{'xl_title':None,  'key':True, 'required': True, 'func':lambda val,needdata: needdata['vof_dict']['name']['val']}),
                                            ('email',{'xl_title':None,  'key':True, 'required': True, 'func':lambda val,needdata: needdata['vof_dict']['login']['val']}),
                                            ('department_id',{'xl_title':None,  'key':False, 'required': True, 'func':lambda val,needdata: needdata['vof_dict']['department_id']['val']}),
                                            ('parent_id',{'key':False,'required':False,
                                                        'fields':[
                                                                 ('name',{'xl_title':None,  'key':True, 'required': True, 'func':lambda val,needdata: needdata['vof_dict']['department_id']['fields']['name']['val'] }),
                                                                  
                                                                 ]
                                            }),  
                                             
                                        ]
                                    }
                 ),  
                      ]
                },#End users'
  
    u'cvi': {
                'title_rows' : [0], 
                'begin_data_row_offset_with_title_row' :1,
                'set_is_largest_map_row_choosing':True,
                'sheet_names': lambda self,wb: [wb.sheet_names()[0]],
                'model':'cvi',
                'fields' : [
                    
                     ('user_id',{'key':True,'set_val': lambda self: self.env.uid}),
                      ('department_id',{'fields':[
                          ('name',{'key':True,'required':True,'xl_title':u'Đơn vị tạo','skip_field_if_not_found_column_in_some_sheet':True ,})
                          ]}),
                      ('loai_record',{'required':True, 'key':True, 'xl_title':u'Loại Record','skip_field_if_not_found_column_in_some_sheet':True,'replace_val':{'all':[(False,u'Công Việc')]}}),
                      ('categ_id',{'fields':[
                          ('name',{'key':True,'required':True,'xl_title':u'Nhóm','skip_field_if_not_found_column_in_some_sheet':True ,})
                          ]}
                       ),
                      ('thiet_bi_id',{'fields':[
                          ('name',{'required':True,'xl_title':u'Thiết bị','skip_field_if_not_found_column_in_some_sheet':True})
                          ]}),
                      ('tvcv_id',{'key':True,'only_get':True,'fields':[
                          ('name',{'key':True,'required':True,'xl_title':[u'TVCV/ Loại sự cố/ Loại sự vụ',u'Thư Viện Công Việc']})
                          ]}
                       ),
                      ('noi_dung',{'xl_title':u'Nội dung'}),
                      ('gio_bat_dau',{'key':True,'xl_title':u'Giờ bắt đầu','bypass_check_type':True,'func':convert_vn_str_datetime_to_utc_str_datetime}),
                      ('gio_ket_thuc',{'key':True,'xl_title':u'Giờ Kết Thúc','bypass_check_type':True,'func':convert_vn_str_datetime_to_utc_str_datetime}),
                      ('slncl',{'xl_title':u'Số lượng người chia điểm'}),
                      ('ti_le_chia_diem',{'xl_title':u'Tỉ lệ chia điểm'}),
                       ('cd_children_ids',{'fields':[
                            ('user_id',{'xl_title':u'Các CV Chia Điểm Con','func':cd_children_ids_,'key':True,'st_is_x2m_field':True,'required':True }),
                            ('loai_record',{'set_val':u'Công Việc','key':True})     ,
                            ('gio_bat_dau',{'key':True,'bypass_check_type':True,'func':lambda v,n: n['vof_dict']['gio_bat_dau']['val']}),
                            ('gio_ket_thuc',{'key':True,'bypass_check_type':True,'func':lambda v,n: n['vof_dict']['gio_ket_thuc']['val']}),
                            ('tvcv_id',{'key':True,'func':lambda v,n: n['vof_dict']['tvcv_id']['val']}),
                                                     ]})
                            
                            
                            
                      ]
                },#location partner            
        u'thuebaoline': {
                'title_rows' : [0], 
                'begin_data_row_offset_with_title_row' :1,
                'set_is_largest_map_row_choosing':True,
                'sheet_names': [u'BCN'],
                'dong_test':10,
                'model':'dai_tgg.thuebaoline',
                'fields' : [
                      ('thuebao_id',{'fields':[
                          ('date',{'key':True,'required':True,'set_val':datetime.date.today()})
                          ]}),
                      ('msc',{'required':True, 'key':True, 'xl_title':u'MSC-VLR'}),
                      ]
                },#location partner     
                       
        u'bds.poster': {
                'title_rows' : [0], 
                'begin_data_row_offset_with_title_row' :1,
                'set_is_largest_map_row_choosing':True,
                'sheet_names': [u'Sheet 1'],
                'model':'bds.poster',
                'fields' : [
                      ('name',{'key':True,'xl_title':u'Name'}),
                      ('ghi_chu_import',{'key':False,'xl_title':u'Quan'}),
                      ]
                },#location par  
                              
                   }
                   
    return user_model_dict
    
def stt_thuebaoline_(v,n):
    stt  = n['vof_dict'].setdefault('stt',{})
    val = stt.setdefault('val',0)
    val +=1
    return val
                