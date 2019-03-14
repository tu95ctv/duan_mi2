# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.addons.tsbd.models.tool import  request_html
# from odoo.addons.tsbd.models.leech import  detail_match
from odoo.addons.tsbd.models.tool import   get_or_create_object_sosanh

from bs4 import BeautifulSoup

class Period(models.Model):  
    _name = 'tsbd.period' 
    name = fields.Char()
#     cate_id = fields.Many2one('tsbd.cate')
class Cate(models.Model):  
    _name = 'tsbd.cate' 
    name = fields.Char()
    cate_id = fields.Many2one('tsbd.cate')
    match_ids = fields.One2many('tsbd.match', 'cate_id')
    bang_match_ids = fields.One2many('tsbd.match', 'bang_id')
    cate_ids = fields.One2many('tsbd.bxh','cate_id')
    no_match =  fields.Integer(compute='no_match_', store=True)
    large_cate =  fields.Boolean()
    
    bet_bxh_ids = fields.One2many('tsbd.betbxh','cate_id')
    match_number = fields.Integer()
    avg_score1 = fields.Float()
    avg_score2 = fields.Float()
    avg_score = fields.Float()
    
    
#     no_match =  fields.Integer()
    @api.multi
    def avg_button(self):
#         self.env['tsbd.match'].search([('cate_id','=')])
        rs = self.env['tsbd.match'].read_group([('cate_id','=', self.id)],['score1', 'score2'],[])
        rs = rs[0]
        self.match_number = rs['__count']
        self.avg_score1 =rs['score1']/rs['__count']
        self.avg_score2 =rs['score2']/rs['__count']
        self.avg_score = self.avg_score1 + self.avg_score2

#         raise UserError(u'%s'%rs)
    @api.multi
    def name_get(self):

        result = []
        for r in self:
            name = u'%s%s'%(r.name, u'(%s Team)'%r.no_match if r.no_match else '')
            result.append((r.id,name))
        return result
        
        
    @api.depends('cate_ids', 'large_cate')
    def no_match_(self):
        for r in self:
            r.no_match = len(r.cate_ids)
    @api.multi
    def clear_bxh(self):
        self.cate_ids = [(6,0,[])]
    @api.multi
    def trig(self):
        matchs= self.env['tsbd.match'].search([])
        matchs.write({'trig':True})

    
#     
    def gen_bxh_dict(self, cate_teams, domain,for_bet=False):
        rt_home_goal = {}
        read_group_rs = self.env['tsbd.match'].read_group(domain,['team1','score1', 'score2'],['team1'], lazy=False)
        for ateam in read_group_rs:
            ateams = {}
            ateams['home_match_number'] = ateam['__count']
            ateams['score1'] = ateam['score1']
            ateams['score2'] = ateam['score2']
            rt_home_goal[ateam['team1'][0]] = ateams
        rt_away_goal = {}
        read_group_rs = self.env['tsbd.match'].read_group(domain,['team2','score1', 'score2'],['team2'], lazy=False)
        for ateam in read_group_rs:
            ateams = {}
            ateams['away_match_number'] = ateam['__count']
            ateams['score1'] = ateam['score1']
            ateams['score2'] = ateam['score2']
            rt_away_goal[ateam['team2'][0]] = ateams
        if not for_bet:
            str_winner = 'winner'
            str_team1 = 'doi_nha'
        else:
            str_winner = 'handicap_bet_winner'
            str_team1 = 'team1'
            
        if not for_bet:
            str_team2 = 'doi_khach'
        else:
            str_team2 = 'team2'
            
        rt_home_over = {}  
        ad = {'team1':'home','team2':'away'}
        for team1_or_2,home_or_away in ad.items() :
            read_group_rs = self.env['tsbd.match'].read_group(domain, [team1_or_2,'over_or_under'],[team1_or_2, 'over_or_under'], lazy=False)
            for ateam in read_group_rs:
                team_id = ateam[team1_or_2][0]
                ateams = rt_home_over.setdefault(team_id, {})
                if ateam['over_or_under'] == 'over':
                    ateams['%s_over'%home_or_away] = ateam['__count']
                elif  ateam['over_or_under'] == 'under':
                    ateams['%s_under'%home_or_away] = ateam['__count']
                else:
                    ateams['%s_ou_draw'%home_or_away] = ateam['__count']
                
                
                
#             rt_home_over[] = ateams
#         raise UserError(u'%s'%len(rt_home_over))   

            
            
            
        rt_home_win= {}
        read_group_rs = self.env['tsbd.match'].read_group(domain, ['team1',str_winner,'score1', 'score2','handicap_wl1','handicap_wl_amount1'],['team1', str_winner], lazy=False)
        for ateam in read_group_rs:
            if ateam[str_winner] == str_team1:
                ateams = {}
                if not for_bet:
                    ateams['home_win_count'] = ateam['__count']
                else:
                    ateams['home_win_count'] = ateam['handicap_wl1']
                    ateams['home_win_amount'] = ateam['handicap_wl_amount1']
                rt_home_win[ateam['team1'][0]] = ateams
                
                
        rt_home_lose= {}
        read_group_rs = self.env['tsbd.match'].read_group(domain, ['team1',str_winner,'score1', 'score2','handicap_wl1', 'handicap_wl_amount1'],['team1', str_winner], lazy=False)
        for ateam in read_group_rs:
            if ateam[str_winner] == str_team2:
                ateams = {}
                if not for_bet:
                    ateams['home_lose_count'] = ateam['__count']
                else:
                    ateams['home_lose_count'] = ateam['handicap_wl1']
                    ateams['home_lose_amount'] = ateam['handicap_wl_amount1']
                rt_home_lose[ateam['team1'][0]] = ateams
                
                
        
        
        rt_away_win= {}
        read_group_rs = self.env['tsbd.match'].read_group(domain,['team2',str_winner, 'score1', 'score2','handicap_wl2', 'handicap_wl_amount2'],['team2', str_winner], lazy=False)
        for ateam in read_group_rs:
            if ateam[str_winner] == str_team2:
                ateams = {}
                if not for_bet:
                    ateams['away_win_count'] = ateam['__count']
                else:
                    ateams['away_win_count'] = ateam['handicap_wl2']
                    ateams['away_win_amount'] = ateam['handicap_wl_amount2']
                rt_away_win[ateam['team2'][0]] = ateams
                
        rt_away_lose= {}
        read_group_rs = self.env['tsbd.match'].read_group(domain,['team2',str_winner, 'score1', 'score2','handicap_wl2', 'handicap_wl_amount2'],['team2', str_winner], lazy=False)
        for ateam in read_group_rs:
            if ateam[str_winner] == str_team1:
                ateams = {}
                if not for_bet:
                    ateams['away_lose_count'] = ateam['__count']
                else:
                    ateams['away_lose_count'] = ateam['handicap_wl2']
                    ateams['away_lose_amount'] = ateam['handicap_wl_amount2']
                rt_away_lose[ateam['team2'][0]] = ateams
                
                
        #san nhà
        if not for_bet:
            str_loser = 'loser'
        else:
            str_loser = 'handicap_bet_loser'
       
        rt_home_draw = {}
        read_group_rs = self.env['tsbd.match'].read_group(domain + ['|','|','|',(str_winner,'=', False),(str_loser,'=', False),(str_winner,'=', 'hoa'),(str_loser,'=', 'hoa')],['team1','score1', 'score2'],['team1'], lazy=False)
        for ateam in read_group_rs:
            ateams = {}
            ateams['home_draw_count'] = ateam['__count']
            rt_home_draw[ateam['team1'][0]] = ateams
            
            
    
        #san khach
        rt_away_draw = {}
        read_group_rs = self.env['tsbd.match'].read_group(domain + ['|','|','|',(str_winner,'=', False),(str_loser,'=', False),(str_winner,'=', 'hoa'),(str_loser,'=', 'hoa')],['team2','score1', 'score2'],['team2'], lazy=False)
        for ateam in read_group_rs:
            ateams = {}
            ateams['away_draw_count'] = ateam['__count']
            rt_away_draw[ateam['team2'][0]] = ateams
        bxh_dict = {}
        for team in cate_teams:
            home_t =  rt_home_win.get(team, {}).get('home_win_count',0)
            away_t  = rt_away_win.get(team, {}).get('away_win_count',0)
            home_h = rt_home_draw.get(team, {}).get('home_draw_count',0)
            away_h =  rt_away_draw.get(team, {}).get('away_draw_count',0)
            home_tg =  rt_home_goal.get(team, {}).get('score1',0)
            home_th = rt_home_goal.get(team, {}).get('score2',0)
            home_match_number =  rt_home_goal.get(team, {}).get('home_match_number',0)
            away_match_number =  rt_away_goal.get(team, {}).get('away_match_number',0)
            away_tg = rt_away_goal.get(team, {}).get('score2',0)
            away_th =  rt_away_goal.get(team, {}).get('score1',0)
            score_sum = home_tg + away_tg
            lost_score_sum = home_th + away_th
            home_b = rt_home_lose.get(team, {}).get('home_lose_count',0)
            away_b = rt_away_lose.get(team, {}).get('away_lose_count',0)
            adict = {}
            if not for_bet:
                diem = (home_t + away_t ) *3 + (home_h + away_h)
                money = False
            else:
                diem = (home_t + away_t )  +   home_b + away_b
                home_win_amount =  rt_home_win.get(team, {}).get('home_win_amount',0)
                away_win_amount  = rt_away_win.get(team, {}).get('away_win_amount',0)
                home_lose_amount =  rt_home_lose.get(team, {}).get('home_lose_amount',0)
                away_lose_amount  = rt_away_lose.get(team, {}).get('away_lose_amount',0)
                money = home_win_amount + away_win_amount + home_lose_amount + away_lose_amount
                adict ['money'] =  money
            
            hsbt = score_sum - lost_score_sum
            rt_home_over_of_ateam = rt_home_over.get(team,{})
            adict.update(rt_home_over_of_ateam)
            update_dict = {'home_t':home_t,
                               'away_t': away_t,
                              'home_h': home_h,
                              'away_h':away_h,
                              'home_tg':home_tg,
                              'away_tg':away_tg,
                              'home_th':home_th,
                              'away_th':away_th,
                              'home_b':home_b,
                              'away_b':away_b,
                              'home_match_number':home_match_number,
                               'away_match_number': away_match_number,
                              'score_sum':score_sum,
                              'lost_score_sum':lost_score_sum,
                              'diem':diem,
                              'hsbt':hsbt,
                               }
            adict.update(update_dict)
            bxh_dict[team] =adict
            
#         raise UserError(u'%s'%bxh_dict)
        return bxh_dict
    
    
    @api.multi
    def bxh(self):
        for_bet = self._context.get('for_bet')
        if for_bet:
            cate_id = 'bet_cate_id'
            model = 'tsbd.betbxh'
        else:
            model ='tsbd.bxh'
            
        
        if u'ảng' not in self.name:
            cate_id = 'cate_id'
        else:
            cate_id = 'bang_id'
            
        domain = [(cate_id,'=', self.id),('state','!=', u'Chưa bắt đầu')]
        match_ids = self.env['tsbd.match'].search(domain)
        home_teams = match_ids.mapped('team1.id')
        away_teams = match_ids.mapped('team2.id')
        cate_teams = home_teams + away_teams
        
        
        bxh_dict = self.gen_bxh_dict(cate_teams, domain,for_bet=for_bet)
        for team,ateam_bxh_dict in bxh_dict.items():
#             new_ateam = {}
#             new_ateam['home_t'] =ateam_bxh_dict['home_t']
#             new_ateam['away_t'] = ateam_bxh_dict['away_t']
#             new_ateam['home_b'] =ateam_bxh_dict['home_b']
#             new_ateam['away_b'] = ateam_bxh_dict['away_b']
#             
#             new_ateam['home_h'] = ateam_bxh_dict['home_h']
#             new_ateam['away_h'] = ateam_bxh_dict['away_h']
#             new_ateam['home_tg'] = ateam_bxh_dict['home_tg']
#             new_ateam['home_th'] =  ateam_bxh_dict['home_th']
#             new_ateam['diem'] = ateam_bxh_dict['diem']
#             new_ateam['away_tg'] = ateam_bxh_dict['away_tg']
#             new_ateam['away_th'] = ateam_bxh_dict['away_th']
#             new_ateam['home_match_number'] = ateam_bxh_dict['home_match_number']
#             new_ateam['away_match_number'] = ateam_bxh_dict['away_match_number']
#             
            
            ateam_bxh_dict['cate_id'] = self.id
            
            get_or_create_object_sosanh(self,model, {'team_id':team, 'cate_id':self.id
                                                          }, ateam_bxh_dict, is_must_update = True)
        
        
        if not for_bet:
            rg_rs = self.env['tsbd.bxh'].read_group([('cate_id','=', self.id)],['team_id','diem'],['diem'],lazy=False)
            rg_rs =  list(filter(lambda i: i['__count']>1,rg_rs))
            for ateam_rg in rg_rs:
                diem = ateam_rg['diem']
                team_ids = self.env['tsbd.bxh'].search([('diem','=', diem),('cate_id','=',self.id)]).mapped('team_id.id')
                domain = [(cate_id,'=', self.id),('state','!=', u'Chưa bắt đầu'),('team1','in',team_ids),('team2','in',team_ids)]
                doi_dau_bxh_dict = self.gen_bxh_dict(team_ids, domain)
                for team, ex_team_bxh_dict in doi_dau_bxh_dict.items():
                    ex_search_dict = {'team_id':team, 'cate_id':self.id}
                    ex_update_dict = {'diem_dd':ex_team_bxh_dict['diem']}
                    get_or_create_object_sosanh(self,'tsbd.bxh', ex_search_dict,  ex_update_dict, is_must_update = True)
            bxh_ids = self.env['tsbd.bxh'].search([('cate_id','=',self.id)],order='diem desc, hsbt desc, score_sum desc')
        else:
            bxh_ids = self.env['tsbd.betbxh'].search([('cate_id','=',self.id)],order='diem desc')
        for stt,r in enumerate(bxh_ids) :
            r.stt = stt +1
