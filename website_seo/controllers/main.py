# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, an open source suite of business apps
# This module copyright (C) 2015 bloopark systems (<http://bloopark.de>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.website.controllers.main import Website


class Website(Website):

    @http.route(['/<path:seo_url>'], type='http', auth="public", website=True)
    def path_page(self, seo_url, **kwargs):
        """Handle SEO urls for ir.ui.views.

        ToDo: Add additional check for field seo_url_parent. Otherwise it is
        possible to use invalid url structures. For example: if you have two
        pages 'study-1' and 'study-2' with the same seo_url_level and different
        seo_url_parent you can use '/ecommerce/study-1/how-to-do-it-right' and
        '/ecommerce/study-2/how-to-do-it-right' to call the page
        'how-to-do-it-right'.
        """
        env = request.env(context=request.context)
        seo_url_parts = [s.encode('utf8') for s in seo_url.split('/')
                         if s != '']
        views = env['ir.ui.view'].search([('seo_url', 'in', seo_url_parts)],
                                         order='seo_url_level ASC')
        page = 'website.404'
        if len(seo_url_parts) == len(views):
            seo_url_check = [v.seo_url.encode('utf8') for v in views]
            current_view = views[-1]
            if (seo_url_parts == seo_url_check
                    and (current_view.seo_url_level + 1) == len(views)):
                page = current_view.xml_id

        if page == 'website.404':
            url = self.look_for_redirect_url(seo_url, **kwargs)
            if url:
                return request.redirect(url, code=301)

        if page == 'website.404' and request.website.is_publisher():
            page = 'website.page_404'

        return request.render(page, {})

    def look_for_redirect_url(self, seo_url, **kwargs):
        domain = ['|', ('seo_url_redirect', '!=', False), ('seo_url', '=', seo_url)]
        for view in request.env['ir.ui.view'].search(domain):
            if not seo_url.startswith('/'):
                seo_url = '/%s' % seo_url
            if not view.seo_url_redirect or (seo_url in view.seo_url_redirect.split(',')):
                return view.get_seo_path()[0]
        return False

    @http.route()
    def page(self, page, **opt):
        try:
            view = request.website.get_template(page)
            if view.seo_url:
                return request.redirect(view.get_seo_path()[0], code=301)
        except:
            pass
        return super(Website, self).page(page, **opt)
