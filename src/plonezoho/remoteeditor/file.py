
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


class RemoteFileView(RemoteBase):
    pass


class RemoteEditor(RemoteBase):

    def __call__(self):
        file_ = self.context.getFile()
        blob_ = file_.getBlob().open()
        url = remote(
            apikey=self.apikey,
            mode='normaledit',
            documentid=hashlib.sha224(self.context.UID() + self.apikey).hexdigest(),
            saveurl=self.context.absolute_url()+'/@@remotesave',
            content=blob_,
            filename=file_.filename,
            lang=self.language(),
            )
        self.request.response.redirect(url)
        blob_.close()

    def language(self):
        lang = aq_inner(self.context).Language()
        if lang:
            return lang
        portal_state = self.context.unrestrictedTraverse("@@plone_portal_state")
        return portal_state.default_language()


class RemoteSave(RemoteBase):

    def __call__(self):
        doc_id = self.request.get('id')
        if doc_id != hashlib.sha224(self.context.UID() + self.apikey).hexdigest():
            raise 'saving to wrong place'
        self.context.setFile(self.request.get('content'))
        # FIXME: not returning status correctly
