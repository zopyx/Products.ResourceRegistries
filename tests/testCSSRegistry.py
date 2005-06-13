#
# CSSRegistryTestCase
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from zExceptions import NotFound
from Testing import ZopeTestCase
from Products.ResourceRegistries.tests import CSSRegistryTestCase

from Products.ResourceRegistries.config import CSSTOOLNAME
from Products.ResourceRegistries.interfaces import ICSSRegistry
from Interface.Verify import verifyObject
from Products.CMFCore.utils import getToolByName

from Products.PloneTestCase.PloneTestCase import PLONE21
from DateTime import DateTime

class TestImplementation(CSSRegistryTestCase.CSSRegistryTestCase):

    def afterSetUp(self):
        pass

    def test_interfaces(self):
        tool = getattr(self.portal, CSSTOOLNAME)
        self.failUnless(ICSSRegistry.isImplementedBy(tool))
        self.failUnless(verifyObject(ICSSRegistry, tool))

class TestTool(CSSRegistryTestCase.CSSRegistryTestCase):

    def afterSetUp(self):
        pass

    def testToolExists(self):
        self.failUnless(CSSTOOLNAME in self.portal.objectIds())

    def testZMIForm(self):
        tool = getattr(self.portal, CSSTOOLNAME)
        self.setRoles(['Manager'])
        self.failUnless(tool.manage_cssForm())
        self.failUnless(tool.manage_cssComposition())
        #print tool.manage_cssComposition()

class TestSkin(CSSRegistryTestCase.CSSRegistryTestCase):

    def afterSetUp(self):
        pass

    def testSkins(self):
        skins = self.portal.portal_skins.objectIds()
        self.failUnless('ResourceRegistries' in skins)

    def testSkinExists(self):
        self.failUnless(getattr(self.portal, 'renderAllTheStylesheets' ))


class testZMIMethods(CSSRegistryTestCase.CSSRegistryTestCase):

    def afterSetUp(self):
        self.tool = getattr(self.portal, CSSTOOLNAME)
        self.tool.clearResources()

    def testAdd(self):
        self.tool.manage_addStylesheet(id='joe')
        self.assertEqual(len(self.tool.getResources()),1)
        self.failUnless(self.tool.getResources())


class TestStylesheetRegistration(CSSRegistryTestCase.CSSRegistryTestCase):

    def afterSetUp(self):
        self.tool = getattr(self.portal, CSSTOOLNAME)
        self.tool.clearResources()

    def testStoringStylesheet(self):
        self.tool.registerStylesheet('foo')

        self.assertEqual(len(self.tool.getResources()), 1)
        self.assertEqual(self.tool.getResources()[0].get('id'), 'foo')

    def testDefaultStylesheetAttributes(self):
        self.tool.registerStylesheet('foodefault')
        self.assertEqual(self.tool.getResources()[0].get('id'), 'foodefault')
        self.assertEqual(self.tool.getResources()[0].get('expression'), '')
        self.assertEqual(self.tool.getResources()[0].get('media'), '')
        self.assertEqual(self.tool.getResources()[0].get('rel'), 'stylesheet')
        self.assertEqual(self.tool.getResources()[0].get('title'), '')
        self.assertEqual(self.tool.getResources()[0].get('rendering'), 'import')
        self.failUnless(self.tool.getResources()[0].get('enabled'))


    def testStylesheetAttributes(self):        
        self.tool.registerStylesheet('foo', expression='python:1', media='print', rel='alternate stylesheet', title='Foo', rendering='inline',  enabled=0 )
        self.assertEqual(self.tool.getResources()[0].get('id'), 'foo')
        self.assertEqual(self.tool.getResources()[0].get('expression'), 'python:1')
        self.assertEqual(self.tool.getResources()[0].get('media'), 'print')
        self.assertEqual(self.tool.getResources()[0].get('rel'), 'alternate stylesheet')
        self.assertEqual(self.tool.getResources()[0].get('title'), 'Foo')
        self.assertEqual(self.tool.getResources()[0].get('rendering'), 'inline')
        self.failIf(self.tool.getResources()[0].get('enabled'))



    def testDisallowingDuplicateIds(self):
        self.tool.registerStylesheet('foo')
        self.assertRaises(ValueError , self.tool.registerStylesheet , 'foo')

    def testPloneCustomStaysOnTop(self):
        self.tool.registerStylesheet('foo')
        self.tool.registerStylesheet('ploneCustom.css')
        self.tool.registerStylesheet('bar')
        self.assertEqual(len(self.tool.getResources()), 3)
        self.assertEqual([s.get('id') for s in self.tool.getResources()], ['foo', 'bar', 'ploneCustom.css'] )

    def testUnregisterStylesheet(self):
        self.tool.registerStylesheet('foo')
        self.assertEqual(len(self.tool.getResources()), 1)
        self.assertEqual(self.tool.getResources()[0].get('id'), 'foo')
        self.tool.unregisterResource('foo')
        self.assertEqual(len(self.tool.getResources()), 0)

    def testStylesheetsDict(self):
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('ham')
        keys = self.tool.getResourcesDict().keys()
        keys.sort()
        res = ['ham','spam']
        res.sort()
        self.assertEqual(res,keys)
        self.assertEqual(self.tool.getResourcesDict()['ham']['id'], 'ham')



class TestToolSecurity(CSSRegistryTestCase.CSSRegistryTestCase):

    def afterSetUp(self):
        self.tool = getattr(self.portal, CSSTOOLNAME)
        self.tool.clearResources()

    def testRegistrationSecurity(self):
        from AccessControl import Unauthorized
        self.assertRaises(Unauthorized, self.tool.restrictedTraverse , 'registerStylesheet')
        self.assertRaises(Unauthorized, self.tool.restrictedTraverse , 'unregisterResource')
        self.setRoles(['Manager'])
        try:
            self.tool.restrictedTraverse('registerStylesheet')
            self.tool.restrictedTraverse('unregisterResource')
        except Unauthorized:
            self.fail()


class TestToolExpression(CSSRegistryTestCase.CSSRegistryTestCase):

    def afterSetUp(self):
        self.tool = getattr(self.portal, CSSTOOLNAME)
        self.tool.clearResources()

    def testSimplestExpression(self):
        context = self.portal
        self.failUnless(self.tool.evaluateExpression('python:1', context ))
        self.failIf(self.tool.evaluateExpression('python:0', context ))
        self.failUnless(self.tool.evaluateExpression('python:0+1', context ))

    def testNormalExpression(self):
        context = self.portal
        self.failUnless(self.tool.evaluateExpression('object/absolute_url', context ))

    def testExpressionInFolder(self):
        self.folder.invokeFactory('Document', 'eggs')
        context = self.folder
        self.failUnless(self.tool.evaluateExpression('python:"eggs" in object.objectIds()', context ))

class TestStylesheetCooking(CSSRegistryTestCase.CSSRegistryTestCase):

    def afterSetUp(self):
        self.tool = getattr(self.portal, CSSTOOLNAME)
        self.tool.clearResources()

    def testStylesheetCooking(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')

        self.assertEqual(len(self.tool.getResources()), 3)
        self.assertEqual(len(self.tool.cookedresources), 1)
        self.assertEqual(len(self.tool.concatenatedresources.keys()), 4)

    def testStylesheetCookingValues(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')

        self.assertEqual(self.tool.concatenatedresources[self.tool.cookedresources[0].get('id')], ['ham', 'spam', 'eggs'] )


    def testGetEvaluatedStylesheetsCollapsing(self ):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')
        self.assertEqual(len(self.tool.getEvaluatedResources(self.folder)) , 1 )

    def testMoreComplexStylesheetsCollapsing(self ):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam',           expression='string:spam')
        self.tool.registerStylesheet('spam spam',      expression='string:spam')
        self.tool.registerStylesheet('spam spam spam', expression='string:spam')
        self.tool.registerStylesheet('eggs')
        self.assertEqual(len(self.tool.getEvaluatedResources(self.folder)) , 3 )
        ids = [item.get('id') for item in self.tool.getEvaluatedResources(self.folder)]
        self.failUnless('ham' in ids )
        self.failUnless('eggs' in ids )
        self.failIf('spam' in ids )
        self.failIf('spam spam' in ids )
        self.failIf('spam spam spam' in ids )

    def testConcatenatedStylesheetsHaveNoMedia(self ):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam',media='print')
        self.assertEqual(len(self.tool.getEvaluatedResources(self.folder)), 1 )
        self.failIf(self.tool.getEvaluatedResources(self.folder)[0].get('media'))

    def testGetEvaluatedStylesheetsWithExpression(self ):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam',expression='python:1')
        self.assertEqual(len(self.tool.getEvaluatedResources(self.folder)), 2 )

    def testGetEvaluatedStylesheetsWithFailingExpression(self ):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam',expression='python:0')
        self.assertEqual(len(self.tool.getEvaluatedResources(self.folder)), 1 )

    def testGetEvaluatedStylesheetsWithContextualExpression(self ):
        self.folder.invokeFactory('Document', 'eggs')
        self.tool.registerStylesheet('spam',expression='python:"eggs" in object.objectIds()')
        self.assertEqual(len(self.tool.getEvaluatedResources(self.folder)), 1 )

    def testCollapsingStylesheetsLookup(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam',           expression='string:ham')
        self.tool.registerStylesheet('spam spam',      expression='string:ham')
        evaluated = self.tool.getEvaluatedResources(self.folder)
        self.assertEqual(len(evaluated), 2)

    def testRenderingIsInTheRightOrder(self):
        self.tool.registerStylesheet('ham' , expression='string:ham')
        self.tool.registerStylesheet('spam', expression='string:spam')
        evaluated = self.tool.getEvaluatedResources(self.folder)
        evaluatedids = [item['id'] for item in evaluated]
        self.failUnless(evaluatedids[0]=='ham')
        self.failUnless(evaluatedids[1]=='spam')

    def testConcatenatedSheetsAreInTheRightOrderToo(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')
        evaluated = self.tool.getEvaluatedResources(self.folder)
        results = self.tool.concatenatedresources[evaluated[0]['id']]
        self.failUnless(results[0]=='ham')
        self.failUnless(results[1]=='spam')
        self.failUnless(results[2]=='eggs')

    def testRenderingStylesheetLinks(self):
        self.tool.registerStylesheet('ham',                 rendering='link')
        self.tool.registerStylesheet('ham 2 b merged',      rendering='link')
        self.tool.registerStylesheet('spam', expression='string:ham', rendering='link')
        self.tool.registerStylesheet('simple.css',          rendering='inline')
        all = getattr(self.portal, 'renderAllTheStylesheets')()
        self.failUnless('background-color' in all)
        self.failUnless('<link' in all)
        self.failUnless('/spam' in all)
        self.failIf('/simple.css' in all)


    def testReenderingConcatenatesInline(self):
        self.tool.registerStylesheet('simple.css',  rendering='inline')
        self.tool.registerStylesheet('simple2.css', rendering='inline')
        all = getattr(self.portal, 'renderAllTheStylesheets')()
        self.failUnless('background-color' in all)
        self.failUnless('blue' in all)

    def testDifferentMediaAreCollapsed(self):
        self.tool.registerStylesheet('simple.css',  media='print')
        self.tool.registerStylesheet('simple2.css', media='all')
        self.assertEqual(len(self.tool.getEvaluatedResources(self.folder)),1)


    def testRenderingWorksInMainTemplate(self):

        renderedpage = getattr(self.portal, 'index_html')()
        self.failIf('background-color' in renderedpage)

        self.tool.registerStylesheet('simple.css', rendering='inline')

        renderedpage = getattr(self.portal, 'index_html')()
        self.failUnless('background-color' in renderedpage)


class TestStylesheetMoving(CSSRegistryTestCase.CSSRegistryTestCase):

    def afterSetUp(self):
        self.tool = getattr(self.portal, CSSTOOLNAME)
        self.tool.clearResources()

    def testStylesheetMoveDown(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')

        self.assertEqual([s.get('id') for s in self.tool.getResources()], ['ham', 'spam', 'eggs'] )

        self.tool.moveResourceDown('spam')
        self.assertEqual([s.get('id') for s in self.tool.getResources()], ['ham', 'eggs', 'spam'] )

    def testStylesheetMoveDownAtEnd(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')

        self.assertEqual([s.get('id') for s in self.tool.getResources()], ['ham', 'spam', 'eggs'] )

        self.tool.moveResourceDown('eggs')
        self.assertEqual([s.get('id') for s in self.tool.getResources()], ['ham', 'spam', 'eggs'] )

    def testStylesheetMoveUp(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')

        self.assertEqual([s.get('id') for s in self.tool.getResources()], ['ham', 'spam', 'eggs'] )

        self.tool.moveResourceUp('spam')
        self.assertEqual([s.get('id') for s in self.tool.getResources()], ['spam', 'ham', 'eggs'] )

    def testStylesheetMoveUpAtStart(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')

        self.assertEqual([s.get('id') for s in self.tool.getResources()], ['ham', 'spam', 'eggs'] )

        self.tool.moveResourceUp('ham')
        self.assertEqual([s.get('id') for s in self.tool.getResources()], ['ham', 'spam', 'eggs'] )

    def testStylesheetMoveIllegalId(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')

        self.assertEqual([s.get('id') for s in self.tool.getResources()], ['ham', 'spam', 'eggs'] )

        self.assertRaises(NotFound, self.tool.moveResourceUp, 'foo')

    def testStylesheetMoveToBottom(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')

        self.assertEqual([s.get('id') for s in self.tool.getResources()], ['ham', 'spam', 'eggs'] )

        self.tool.moveResourceToBottom('ham')
        self.assertEqual([s.get('id') for s in self.tool.getResources()], ['spam', 'eggs', 'ham'] )

    def testStylesheetMoveToTop(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')

        self.assertEqual([s.get('id') for s in self.tool.getResources()], ['ham', 'spam', 'eggs'] )

        self.tool.moveResourceToTop('eggs')
        self.assertEqual([s.get('id') for s in self.tool.getResources()], ['eggs', 'ham', 'spam'] )

    def testStylesheetMoveBefore(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')
        self.tool.registerStylesheet('bacon')

        self.assertEqual([s.get('id') for s in self.tool.getResources()], ['ham', 'spam', 'eggs', 'bacon'] )

        self.tool.moveResourceBefore('bacon', 'ham')
        self.assertEqual([s.get('id') for s in self.tool.getResources()], ['bacon', 'ham', 'spam', 'eggs'] )

        self.tool.moveResourceBefore('bacon', 'eggs')
        self.assertEqual([s.get('id') for s in self.tool.getResources()], ['ham', 'spam', 'bacon', 'eggs'] )

    def testStylesheetMoveAfter(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')
        self.tool.registerStylesheet('bacon')

        self.assertEqual([s.get('id') for s in self.tool.getResources()], ['ham', 'spam', 'eggs', 'bacon'] )

        self.tool.moveResourceAfter('bacon', 'ham')
        self.assertEqual([s.get('id') for s in self.tool.getResources()], ['ham', 'bacon', 'spam', 'eggs'] )

        self.tool.moveResourceAfter('bacon', 'spam')
        self.assertEqual([s.get('id') for s in self.tool.getResources()], ['ham', 'spam', 'bacon', 'eggs'] )

    def testStylesheetMove(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')
        self.tool.registerStylesheet('bacon')

        self.assertEqual([s.get('id') for s in self.tool.getResources()], ['ham', 'spam', 'eggs', 'bacon'] )

        self.tool.moveResource('ham', 2)
        self.assertEqual([s.get('id') for s in self.tool.getResources()], ['spam', 'eggs', 'ham', 'bacon'] )

        self.tool.moveResource('bacon', 0)
        self.assertEqual([s.get('id') for s in self.tool.getResources()], ['bacon', 'spam', 'eggs', 'ham'] )

class TestTraversal(CSSRegistryTestCase.CSSRegistryTestCase):

    def afterSetUp(self):
        self.tool = getattr(self.portal, CSSTOOLNAME)
        self.tool.clearResources()
        self.tool.registerStylesheet('simple.css')

    def testGetItemTraversal(self):
        self.failUnless(self.tool['simple.css'])

    def testGetItemTraversalContent(self):
        self.failUnless('background-color' in str(self.tool['simple.css']))

    def testRestrictedTraverseContent(self):
        self.failUnless('background-color' in str(self.portal.restrictedTraverse('portal_css/simple.css')))


    def testRestrictedTraverseComposition(self):
        self.tool.registerStylesheet('simple2.css')
        styles = self.tool.getEvaluatedResources(self.portal)
        self.assertEqual(len(styles), 1)
        magicId = styles[0].get('id')

        content = str(self.portal.restrictedTraverse('portal_css/%s' % magicId))
        self.failUnless('background-color' in content)
        self.failUnless('blue' in content)


    def testCompositesWithBrokedId(self):
        self.tool.registerStylesheet('nonexistant.css')
        stylesheets = self.tool.getEvaluatedResources(self.portal)
        self.assertEqual(len(stylesheets), 1)
        magicId = stylesheets[0].get('id')
        content = str(self.portal.restrictedTraverse('portal_css/%s' % magicId))

    def testMediadescriptorsInConcatenatedStylesheets(self):
        self.tool.registerStylesheet('simple2.css', media='print')
        styles = self.tool.getEvaluatedResources(self.portal)
        self.assertEqual(len(styles), 1)
        magicId = styles[0].get('id')

        content = str(self.portal.restrictedTraverse('portal_css/%s' % magicId))

        self.failUnless("@media print" in content)
        self.failUnless("background-color : red" in content)
        self.failUnless("H1 { color: blue; }" in content)

class TestPublishing(CSSRegistryTestCase.CSSRegistryTestCase):
    """Integration tests. - testing http headers etc."""
    def afterSetUp(self):
        self.tool = getattr(self.portal, CSSTOOLNAME)
        self.tool.clearResources()
        self.toolpath = '/'+self.tool.absolute_url(1)
        self.portalpath = '/'+ getToolByName(self.portal,'portal_url')(1)
        self.tool.registerStylesheet('plone_styles.css')
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Document','index_html')
        self.setRoles(['Member'])

    def testPublishCSSThroughTool(self):
        response = self.publish(self.toolpath+'/plone_styles.css')
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getHeader('Content-Type'), 'text/css')

    def testPublishNonMagicCSSThroughTool(self):
        #this one fails because of the broken traversal hook
        self.setRoles(['Manager'])
        body = '''<dtml-var "'joined' + 'string'">'''
        self.portal.addDTMLMethod('testmethod', file=body)
        self.tool.registerStylesheet('testmethod')
        response = self.publish(self.toolpath+'/testmethod')
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getHeader('Content-Type'), 'text/css')

    def testPublishPageWithInlineCSS(self):
        response = self.publish(self.portalpath)
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getHeader('Content-Type'), 'text/html;charset=utf-8')
        self.tool.clearResources()
        # test that the main page retains its content-type
        self.setRoles(['Manager'])
        body = """<dtml-call "REQUEST.RESPONSE.setHeader('Content-Type', 'text/css')">/*and some css comments too*/ """
        self.portal.addDTMLMethod('testmethod', file=body)
        self.tool.registerStylesheet('testmethod', rendering='inline')
        response = self.publish(self.portalpath)
        self.assertEqual(response.getHeader('Content-Type'), 'text/html;charset=utf-8')
        self.assertEqual(response.getStatus(), 200)

class TestDebugMode(CSSRegistryTestCase.CSSRegistryTestCase):

    def afterSetUp(self):
        self.tool = getattr(self.portal, CSSTOOLNAME)
        self.tool.clearResources()
        self.portalpath = '/'+ getToolByName(self.portal,'portal_url')(1)
        self.toolpath = '/'+self.tool.absolute_url(1)


    def testDebugModeSplitting(self ):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.assertEqual(len(self.tool.getEvaluatedResources(self.folder)), 1 )
        self.tool.setDebugMode(True)
        self.tool.cookResources()
        #print self.tool.getEvaluatedResources(self.folder)
        self.assertEqual(len(self.tool.getEvaluatedResources(self.folder)), 2 )

    def testDebugModeSplitting(self ):
        self.tool.registerStylesheet('ham')
        # publish in normal mode
        response = self.publish(self.toolpath+'/ham')
        now = DateTime()
        soon = now + 7
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getHeader('Expires'), soon.strftime('%a, %d %b %Y %H:%M:%S %Z'))
        # set debug mode
        self.tool.setDebugMode(True)
        self.tool.cookResources()
        # publish in debug mode
        response = self.publish(self.toolpath+'/ham')
        self.failIfEqual(response.getHeader('Expires'), soon.strftime('%a, %d %b %Y %H:%M:%S %Z'))
        self.assertEqual(response.getHeader('Expires'), now.strftime('%a, %d %b %Y %H:%M:%S %Z'))

class TestCSSDefaults(CSSRegistryTestCase.CSSRegistryTestCase):

    def afterSetUp(self):
        self.tool = getattr(self.portal, CSSTOOLNAME)

    def testClearingStylesheets(self):
        self.failUnless(self.tool.getResources())
        self.tool.clearResources()
        self.failIf(self.tool.getResources())

    def testDefaultsInstall(self):
        stylesheetids = [item['id'] for item in self.tool.getResources()]
        self.failUnless('plone.css' in stylesheetids)
        self.failUnless('ploneColumns.css' in stylesheetids)
        self.failUnless('ploneCustom.css' in stylesheetids)

    def testTraverseToConcatenatedDefaults(self):
        stylesheets = self.tool.getEvaluatedResources(self.portal)
        for s in stylesheets:
            try:
                magicId = s.get('id')
                self.portal.restrictedTraverse('portal_css/%s' % magicId)
            except KeyError:
                self.fail()

    def testCallingOfConcatenatedStylesheets(self):
        stylesheets = self.tool.getEvaluatedResources(self.portal)
        for s in stylesheets:
            if 'ploneStyles' in s.get('id'):
                output = self.portal.restrictedTraverse('portal_css/%s' % s.get('id'))
                break
        if not output:
            self.fail()
        o = str(output)[:]
        self.failIf("&lt;dtml-call" in o)
        self.failIf("&amp;dtml-fontBaseSize;" in o)
        self.failUnless('** Plone style sheet for CSS2-capable browsers.' in o)





def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestImplementation))
    suite.addTest(makeSuite(TestTool))
    suite.addTest(makeSuite(TestSkin))
    suite.addTest(makeSuite(testZMIMethods))
    suite.addTest(makeSuite(TestStylesheetRegistration))
    suite.addTest(makeSuite(TestToolSecurity))
    suite.addTest(makeSuite(TestToolExpression))
    suite.addTest(makeSuite(TestStylesheetCooking))
    suite.addTest(makeSuite(TestPublishing))
    suite.addTest(makeSuite(TestStylesheetMoving))
    suite.addTest(makeSuite(TestTraversal))
    suite.addTest(makeSuite(TestDebugMode))

    if not PLONE21:
        # we must not test for the defaults in Plone 2.1 because they are all different
        # Plone2.1 has tests in CMFPlone/tests for defaults and migrations
        suite.addTest(makeSuite(TestCSSDefaults))

    return suite

if __name__ == '__main__':
    framework()
