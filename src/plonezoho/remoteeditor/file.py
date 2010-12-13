
import zohoapi
import zope.component
import plone.registry
import plone.memoize.view
import zope.annotation

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName


PLONEZOHO_REMOTEEDITOR = 'plonezoho.remoteeditor'


class RemoteBase(BrowserView):
    """
    """

    DOCID = PLONEZOHO_REMOTEEDITOR+ '-file'

    def __init__(self, context, request):
        super(RemoteBase, self).__init__(context, request)
        registry = zope.component.getUtility(plone.registry.interfaces.IRegistry)
        apikey = registry.get('plonezoho.remoteapi.apikey')
        skey = registry.get('plonezoho.remoteapi.skey')
        if not skey:
            skey = None
        self.remoteapi = zohoapi.Remote(
                apikey=apikey,
                saveurl='%s/@@remote-save?id=%s' % (
                    self.context.absolute_url(),
                    self.context.UID(),
                    ),
                skey=skey,
                )
        self.annotations = zope.annotation.interfaces.IAnnotations(self.context)
        self.membership = getToolByName(self.context, 'portal_membership')

    @property
    def user(self):
        if self.membership.isAnonymousUser(): # the user has not logged in
            return None
        else:
            member = self.membership.getAuthenticatedMember()
            fullname = member.getProperty('fullname', None)
            username = member.getUserName()
            if fullname:
                return fullname + ' (' + username + ')'
            return username

    @property
    def language(self):
        lang = aq_inner(self.context).Language()
        if lang:
            return lang
        portal_state = self.context.unrestrictedTraverse("@@plone_portal_state")
        return portal_state.default_language()

    def get_docid(self):
        docid = None
        if self.DOCID in self.annotations.keys():
            docid = self.annotations[self.DOCID]
        return [self.context.UID(), docid]
    def set_docid(self, value):
        self.annotations[self.DOCID] = value
    documentid = property(get_docid, set_docid)

    @property
    def format(self):
        return self.context.getFile().filename.split('.')[-1]

    @property
    def doctype(self):
        return self.remoteapi.doctype(self.format)

    @property
    def status(self):
        if self.documentid[1] is None:
            return None
        return self._status()

    @plone.memoize.view.memoize
    def _status(self):
        status = self.remoteapi.status(self.doctype, self.documentid)
        # remove documentid from annotation only if:
        #  - status request was OK,
        #   - nobody is working on document and
        #   - documentid alredady exists
        if getattr(status, 'result', True) and \
           getattr(status, 'collaboratorsCount', 0) == 0 and \
           self.documentid[1] is not None:
            del self.annotations[self.DOCID]
        return status

    def collab(self):
        file_ = self.context.getFile()
        blob_ = file_.getBlob().open()
        response = self.remoteapi_call(
                filename=file_.filename,
                content=blob_,
                format=self.format,
                lang=self.language,
                username=self.user,
                documentid=self.documentid,
                )
        if not getattr(response, 'url', None):
            # TODO: handle errors gracefully
            raise Exception(str(response))
        self.documentid = response.documentid
        self.request.response.redirect(response.url)
        blob_.close()

    @property
    def remoteapi_call(self):
        _call = getattr(self, '_remoteapi_call', None)
        if _call:
            return getattr(self.remoteapi, _call)
        raise NotImplemented


class RemoteViewer(RemoteBase):
    _remoteapi_call = 'collab_view'
    __call__ = RemoteBase.collab


class RemoteEditor(RemoteBase):
    _remoteapi_call = 'collab_edit'
    __call__ = RemoteBase.collab


class RemoteSave(RemoteBase):

    def __call__(self):
        if self.request.get('id', None)[0] != self.documentid[0]:
            # TODO: how should error be returned
            raise Exception('saving to wrong place')

        # FIXME: not returning status correctly
        self.context.setFile(self.request.get('content'))


class RemoteFileView(RemoteBase):
    pass
