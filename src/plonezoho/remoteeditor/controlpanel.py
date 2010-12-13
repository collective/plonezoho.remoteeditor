
from plone.z3cform.layout import wrap_form
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm

from plonezoho.remoteeditor.interfaces import IRemoteAPI


class RemoteControlPanelForm(RegistryEditForm):

    schema = IRemoteAPI
    prefix = 'plonezoho.remoteapi'


RemoteControlPanelView = wrap_form(
        RemoteControlPanelForm,
        ControlPanelFormWrapper)
