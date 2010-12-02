
import hashlib

from zohoapi import remote
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from Acquisition import aq_inner
from Products.Five.browser import BrowserView


class RemoteBase(BrowserView):

    def __init__(self, context, request):
        super(RemoteEditor, self).__init__(context, request)
        registry = getUtility(IRegistry)
        self.apikey =  registry.get('plonezoho.remoteapi.apikey')
        self.skey = registry.get('plonezoho.remoteapi.skey')

    @property
    def language(self):
        lang = aq_inner(self.context).Language()
        if lang:
            return lang
        portal_state = self.context.unrestrictedTraverse("@@plone_portal_state")
        return portal_state.default_language()

    @property
    def documentid(self):
        return hashlib.sha224(self.context.UID() + self.apikey).hexdigest(),


class RemoteFileView(RemoteBase):
    pass


class RemoteEditor(RemoteBase):

    def __call__(self):
        file_ = self.context.getFile()
        blob_ = file_.getBlob().open()
        url = remote(
            mode='collabedit',
            apikey=self.apikey,
            documentid=self.documentid,
            lang=self.language,
            saveurl=self.context.absolute_url()+'/@@remote-save',
            content=blob_,
            filename=file_.filename,
            )
        self.request.response.redirect(url)
        blob_.close()

class RemoteFileView(RemoteBase):

    def __call__(self):
        if self.documentid != self.request.get('id'):
            # TODO: how should error be returned
            raise 'saving to wrong place'
        self.context.setFile(self.request.get('content'))
        # FIXME: not returning status correctly
