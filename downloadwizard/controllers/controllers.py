# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.importexcel.models.model_dict_folder.tao_instance_new import importexcel_func
from odoo.addons.downloadwizard.download_tool import  download_all_model_by_url

# class DownloadTonkho(http.Controller):
#     @http.route('/web/binary/download_model/importexcel',type='http', auth="public")
#     def download_all_model_controller(self,**kw):
#         response = download_all_model_by_url(kw)
#         return response
