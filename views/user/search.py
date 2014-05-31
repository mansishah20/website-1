##
#    Copyright (C) 2014 Jessica Tallon & Matt Molyneaux
#
#    This file is part of Inboxen.
#
#    Inboxen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Inboxen.  If not, see <http://www.gnu.org/licenses/>.
##

from django.db.models import F
from django.views import generic
from django.utils.translation import ugettext as _

from inboxen import models
from website.views import base

from watson import views

__all__ = ["SearchView"]

class SearchView(base.LoginRequiredMixin, base.CommonContextMixin,
                                    views.SearchMixin, generic.ListView):
    """A specialised search view that splits results by model"""
    headline = _("Search")
    template_name = "user/search.html"

    def get_models(self):
        ## Use F expressions here because these are actually subqueries
        ## https://github.com/disqus/django-bitfield/issues/31
        inboxes = models.Inbox.objects.filter(flags=F("flags").bitand(~models.Inbox.flags.deleted), user=self.request.user)
        emails = models.Email.objects.filter(
                                        flags=F("flags").bitand(~models.Email.flags.deleted),
                                        inbox__flags=F("inbox__flags").bitand(~models.Inbox.flags.deleted),
                                        inbox__user=self.request.user,
                                        )
        return (inboxes, emails)

    def get_query(self, request):
        get_query = super(SearchView, self).get_query(request)
        kwarg_query = self.kwargs.get(self.get_query_param(), "").strip()
        return kwarg_query or get_query
