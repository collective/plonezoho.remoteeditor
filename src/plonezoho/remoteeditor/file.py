
import hashlib

import zohoapi
import zope.component
import plone.registry
import plone.memoize.view

from Acquisition import aq_inner
from Products.Five.browser import BrowserView


class RemoteBase(BrowserView):

    def __init__(self, context, request):
        super(RemoteBase, self).__init__(context, request)
        registry = zope.component.getUtility(plone.registry.interfaces.IRegistry)
        self.remoteapi = zohoapi.Remote(
                registry.get('plonezoho.remoteapi.apikey'),
                registry.get('plonezoho.remoteapi.skey'),
                )

    @property
    def language(self):
        lang = aq_inner(self.context).Language()
        if lang:
            return lang
        portal_state = self.context.unrestrictedTraverse("@@plone_portal_state")
        return portal_state.default_language()

    @property
    def documentid(self):
        return 'e2e696359ed3e3bda266dfd07ad3fbccdebf17855dc5f624'
        # TODO: should also look at annotation
        return hashlib.sha224(self.context.UID() + self.remoteapi.apikey).hexdigest()

    @property
    def format(self):
        return self.context.getFile().filename.split('.')[-1]

    @property
    def doctype(self):
        return self.remoteapi.doctype(self.format)

    @property
    def status(self):
        return self._status()

    @plone.memoize.view.memoize
    def _status(self):
        status = self.remoteapi.status(self.doctype, self.documentid)
        #import ipdb; ipdb.set_trace()
        return status


class RemoteFileView(RemoteBase):
    pass


class RemoteEditor(RemoteBase):

    def __call__(self):
        file_ = self.context.getFile()
        blob_ = file_.getBlob().open()
        response = self.remoteapi.collab_edit(
                documentid=self.documentid,
                filename=file_.filename,
                content=blob_,
                format=self.format,
                lang=self.language,
                )
        import ipdb; ipdb.set_trace()
        self.request.response.redirect(response.url)
        blob_.close()

class RemoteSave(RemoteBase):

    def __call__(self):
        if self.documentid != self.request.get('id'):
            # TODO: how should error be returned
            raise 'saving to wrong place'
        self.context.setFile(self.request.get('content'))
        # FIXME: not returning status correctly
