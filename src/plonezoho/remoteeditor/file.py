
from StringIO import StringIO

from zohoapi import remote
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
#from Products.CMFCore.utils import getToolByName


class RemoteEditor(BrowserView):
    """
    """

    def __init__(self, context, request):
        super(RemoteEditor, self).__init__(context, request)

        registry = getUtility(IRegistry)
        self.apikey =  registry.get('plonezoho.remoteapi.apikey')
        self.skey = registry.get('plonezoho.remoteapi.skey')

    def __call__(self):
        blob = self.context.getFile()
        blob_content = StringIO()
        blob_content.write(blob.data)
        url = remote(
            apikey=self.apikey,
            skey=self.skey,
            mode='normaledit',
            documentid=self.context.UID(),
            saveurl=self.context.absolute_url()+'@@remoteeditor/save',
            content=blob_content,
            filename=blob.filename,
            lang=self.language(),
            )
        self.request.response.redirect(url)
        blob_content.close()

    def language(self):
        lang = aq_inner(self.context).Language()
        if lang:
            return lang
        portal_state = self.context.unrestrictedTraverse("@@plone_portal_state")
        return portal_state.default_language()

    def save(self):
        import ipdb; ipdb.set_trace()
