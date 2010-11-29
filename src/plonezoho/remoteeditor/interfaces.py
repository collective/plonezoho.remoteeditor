
import zope.schema
import zope.interface

from plonezoho.remoteeditor import MessageFactory as _


class IRemoteAPI(zope.interface.Interface):

    apikey = zope.schema.TextLine(
        title=_(u"API key"),
        description=_("TODO: needs description from where to get apikey!"))

    skey = zope.schema.TextLine(
        title=_("Secret Key"),
        description=_("TODO: needs description what skey does"))
