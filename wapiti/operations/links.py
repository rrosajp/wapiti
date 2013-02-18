# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from base import QueryOperation, SingleParam, MultiParam, StaticParam
from models import PageIdentifier, LanguageLink, InterwikiLink, ExternalLink


class GetBacklinks(QueryOperation):
    field_prefix = 'bl'
    query_field = SingleParam('title', required=True)
    fields = [StaticParam('list', 'backlinks')]

    def extract_results(self, query_resp):
        ret = []
        for pid_dict in query_resp.get('backlinks', []):
            try:
                page_ident = PageIdentifier.from_query(pid_dict, self.source)
            except ValueError:
                continue
            ret.append(page_ident)
        return ret


class GetExternalLinks(QueryOperation):
    field_prefix = 'el'
    query_field = MultiParam('titles', key_prefix=False, required=True)
    fields = [StaticParam('prop', 'extlinks')]

    def extract_results(self, query_resp):
        ret = []
        for pid_dict in query_resp.get('pages', {}).values():
            try:
                page_ident = PageIdentifier.from_query(pid_dict, self.source)
            except ValueError:
                continue
            for el in pid_dict.get('extlinks', []):
                link = ExternalLink(el.get('*'),
                                    page_ident)
                ret.append(link)
        return ret

    def get_cont_str(self, resp, params):
        #todo? fuzzy walker thing to walk down to self.field_prefix+'continue'?
        qc_val = resp.results.get('query-continue')
        if not qc_val:
            return None
        return qc_val['extlinks']['eloffset']

    def prepare_params(self, **kw):
        params = super(GetExternalLinks, self).prepare_params(**kw)
        if params.get('elcontinue'):
            params['eloffset'] = params.pop('elcontinue')
        return params


class GetLanguageLinks(QueryOperation):
    field_prefix = 'll'
    query_field = MultiParam('titles', key_prefix=False, required=True)
    fields = [StaticParam('prop', 'langlinks'),
              SingleParam('url', True)]

    def extract_results(self, query_resp):
        ret = []
        for pid_dict in query_resp.get('pages', {}).values():
            try:
                page_ident = PageIdentifier.from_query(pid_dict, self.source)
            except ValueError:
                continue
            for ld in pid_dict.get('langlinks', []):
                link = LanguageLink(ld.get('url'),
                                    ld.get('lang'),
                                    page_ident)
                ret.append(link)
        return ret


class GetInterwikiLinks(QueryOperation):
    field_prefix = 'iw'
    query_field = MultiParam('titles', key_prefix=False, required=True)
    fields = [StaticParam('prop', 'iwlinks'),
              SingleParam('url', True)]

    def extract_results(self, query_resp):
        ret = []
        for pid_dict in query_resp.get('pages', {}).values():
            try:
                page_ident = PageIdentifier.from_query(pid_dict, self.source)
            except ValueError:
                continue
            for iwd in pid_dict.get('iwlinks', []):
                link = InterwikiLink(iwd.get('url'),
                                     iwd.get('prefix'),
                                     page_ident)
                ret.append(link)
        return ret
