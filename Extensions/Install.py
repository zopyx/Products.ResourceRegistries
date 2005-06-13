from StringIO import StringIO
from Products.Archetypes.Extensions.utils import install_subskin
from Products.ResourceRegistries.config import *
from Products.CMFCore.utils import getToolByName


def install(self):
    out = StringIO()

    install_subskin(self, out, GLOBALS)

    # check for plone >= 2.1
    migrationtool = getToolByName(self, 'portal_migration')
    plone_version = migrationtool.getInstanceVersion()
    if not plone_version.startswith('2.0'):
        print >> out, "Removing 2.0.x skin compatibility."
        skinstool = getToolByName(self, 'portal_skins')
        for name,layers in skinstool.getSkinPaths():
            layers = layers.split(',')
            layers = [x for x in layers if x != 'ResourceRegistries_20compatibility']
            layers = ','.join(layers)
            skinstool.addSkinSelection(name, layers)

    # Install the CSSRegistry
    if CSSTOOLNAME not in self.objectIds():
        factory = self.manage_addProduct['ResourceRegistries']
        factory.manage_addTool(CSSTOOLTYPE)
        print >> out, 'Added CSSRegistry'
    else:
        print >> out, 'CSSRegistry already exists.'

    # Install the JSRegistry
    if JSTOOLNAME not in self.objectIds():
        factory = self.manage_addProduct['ResourceRegistries']
        factory.manage_addTool(JSTOOLTYPE)
        print >> out, 'Added JSRegistry'
    else:
        print >> out, 'JSRegistry already exists.'

    installPloneDefaultJS(self, out)
    
    installPloneDefaultCSS(self, out)
    
    return out.getvalue()





# the default-values-installers
def installPloneDefaultCSS(self, out):
    csstool = getToolByName(self, CSSTOOLNAME)    
    stylesheets = csstool.getResources()
    stylesheet_ids = [x.get('id', None) for x in stylesheets]
    if 'ploneColumns.css' not in stylesheet_ids:
        csstool.registerStylesheet('ploneColumns.css', media="screen", rendering='import')
    if 'plone.css' not in stylesheet_ids:
        csstool.registerStylesheet('plone.css', media="screen", rendering='import')
    if 'plonePrint.css' not in stylesheet_ids:
        csstool.registerStylesheet('plonePrint.css', media="print", rendering='import')
    if 'plonePresentation.css' not in stylesheet_ids:
        csstool.registerStylesheet('plonePresentation.css', media="projection", rendering='import')
    if 'ploneCustom.css' not in stylesheet_ids:
        csstool.registerStylesheet('ploneCustom.css', media="all", rendering='import')    
    if 'ploneTextSmall.css' not in stylesheet_ids:
        csstool.registerStylesheet('ploneTextSmall.css', media="screen", rel='alternate stylesheet', title='Small Text', rendering='link')
    if 'ploneTextLarge.css' not in stylesheet_ids:
        csstool.registerStylesheet('ploneTextLarge.css', media="screen", rel='alternate stylesheet', title='Large Text', rendering='link')
    print >> out, 'installed the Plone default styles'
    
    
def installPloneDefaultJS(self, out):
    """ Install all the jaascripts plne comes with normally"""
    jstool = getToolByName(self, JSTOOLNAME)    

    scripts = jstool.getResources()
    script_ids = [x.get('id', None) for x in scripts]

    if 'plone_javascript_variables.js' not in script_ids:
        jstool.registerScript('plone_javascript_variables.js')
        print >> out, 'installed the javascript variables'

    if 'plone_javascripts.js' not in script_ids:
        jstool.registerScript('plone_javascripts.js')
        print >> out, 'installed the global plone javascripts'

    if 'plone_menu.js' not in script_ids:
        jstool.registerScript('plone_menu.js', expression='not:portal/portal_membership/isAnonymousUser')
        print >> out, 'installed the menu-javascript'
