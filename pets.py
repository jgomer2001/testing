# oxAuth is available under the MIT License (2008). See http://opensource.org/licenses/MIT for full text.
# Copyright (c) 2016, Gluu
#
# Author: Your name here
#

# JAVA IMPORTS SECTION:
# You can import virtually any Java class in oxauth classpath scope, that is /opt/gluu/jetty/oxauth/custom/libs/*.jar,
# oxauth.war#WEB-INF/lib/*.jar, oxauth.war#WEB-INF/classes/*
# 
# Most useful classes reside in ox-prefixed jars. Those are generated when oxauth war is built
# Basically the classes found in repos https://github.com/GluuFederation/oxauth and https://github.com/GluuFederation/oxcore

from org.xdi.oxauth.service import AuthenticationService
from org.xdi.oxauth.security import Identity
from org.xdi.model.custom.script.type.auth import PersonAuthenticationType
from org.xdi.service.cdi.util import CdiUtil
from org.xdi.util import StringHelper
from org.xdi.oxauth.util import ServerUtil

from org.gluu.jsf2.message import FacesMessages
from javax.faces.application import FacesMessage

# This one is from core Java
from java.util import Arrays

# OTHER IMPORTS SECTION:
# I don't know what kind of stuff can go here. I guess whatever python packages are installed in chroot or 
# maybe only what jython jar file offers?
import java

# The name in parenthesis is one of the classes listed here
# https://github.com/GluuFederation/oxCore/blob/version_3.1.4/oxService/src/main/java/org/xdi/model/custom/script/CustomScriptType.java#L43-L54
# Those are the different kinds of cust scripts the server supports. For 2FA scripts, PersonAuthenticationType is used
# (they are all listed in oxTrust "person authentication" tab)
class PersonAuthentication(PersonAuthenticationType):

    # I am not sure where/when this method is called
    def __init__(self, currentTimeMillis):
        self.currentTimeMillis = currentTimeMillis

    # Every time a script is reloaded, this method is called
    # A script is reloaded upon oxAuth startup, when it is altered or enabled in oxTrust, or when the underlying file storing the script  
    # contents changes in disk.
    # Unfortunately oxTrust form cannot detect which script has changed upon form submission, so it triggers reload for ALL
    #
    # configurationAttributes is an instance of java.util.Map<String, org.xdi.model.SimpleCustomProperty> (it's like a python assoc array maybe?)
    # SimpleCustomProperty is this bean: https://github.com/GluuFederation/oxCore/blob/version_3.1.4/oxUtil/src/main/java/org/xdi/model/SimpleCustomProperty.java
    # In summary, configurationAttributes contains name and value of the parameters for this script
    #
    # This method can be used for initialization stuff, and should return True if initialization succeeded
    def init(self, configurationAttributes):
    
        # print statements are very important. Prefixing the statements with the name of the script is
        # a good practice since oxauth_script.log reports the mix of all scripts
        print "Pet. Initialized successfully"
        return True   

    # This is called when the script is disabled, deleted, or reloaded
    def destroy(self, configurationAttributes):
        print "Basic. Destroyed successfully"
        return True

    # Gluu supports two "API versions" (1|2). Numer 2 allows to do step overriding: scripts get executed in steps linearly: 1, 2....
    # When using API 2, you can alter the next upcoming step (by using the getNextStep method). This script does not have
    # such but for instance casa uses it all time, that way you can "go back" to try an alternative credential type.
    def getApiVersion(self):
        return 1

    # In conjuction with getAlternativeAuthenticationMethod this allows to do acr overriding :O !
    # Which means you can at some point "jump" to a different script. There is no way to enforce control of what 
    # happens after the jump (you cannot make the flow return to back this script for instance).
    # This must return False if overriding should take place
    def isValidAuthenticationMethod(self, usageType, configurationAttributes):
        return True


    # This is called only if isValidAuthenticationMethod returned False.
    # This method must return the new acr to take.
    #
    # I don't know what usageType is about really: https://github.com/GluuFederation/oxCore/blob/version_3.1.4/oxUtil/src/main/java/org/xdi/model/AuthenticationScriptUsageType.java
    def getAlternativeAuthenticationMethod(self, usageType, configurationAttributes):
        return None

    # This is usually called after a form (xhtml) was presented to the user to retrieve some data. Forms normally do a POST
    # to the /postlogin endpoint, so this is the handler
    #
    # requestParameters is an instance of java.util.Map<String, String[]>, while step is an integer that
    # represents the step of the flow you are at now
    #
    # This method must return True if authentication passed successfully (at least in the current step)
    def authenticate(self, configurationAttributes, requestParameters, step):
                    
        print "Pet. Authenticate for step %s" % step

        # CdiUtil is an utility that allows to obtain a reference to an oxAuth Weld bean by passing its type
        # See https://github.com/GluuFederation/oxCore/blob/version_3.1.4/oxService/src/main/java/org/xdi/service/cdi/util/CdiUtil.java

        identity = CdiUtil.bean(Identity)
        # In this lookup, we obtained a reference to an object of this class:
        # https://github.com/GluuFederation/oxAuth/blob/version_3.1.4/Server/src/main/java/org/xdi/oxauth/security/Identity.java
        # which derives from https://github.com/GluuFederation/oxCore/blob/version_3.1.4/oxService/src/main/java/org/xdi/model/security/Identity.java

        if step == 1:
            # In 2FA, normally the first step is just doing the user+password check, this is what I do here.
            
            # Below we obtain the user+pass entered in the form login.xhtml, note that these form fields are bound to expressions #{credentials.username}
            # and #{credentials.password} respectively (this is called EL expressions in JSF), and means that setters of properties
            # username and password in java bean credentials will be set to the values typed once form is submitted.
            # See https://github.com/GluuFederation/oxAuth/blob/version_3.1.4/Server/src/main/webapp/login.xhtml#L59-L66
            #
            # identity is a request-scoped bean, so calling this in a step further in the flow won't retrieve what the user provided
            
            credentials = identity.getCredentials()
            user_name = credentials.getUsername()
            user_password = credentials.getPassword()
            
            # The following service bean allows us to authenticate the individual
            authenticationService = CdiUtil.bean(AuthenticationService)
            # See https://github.com/GluuFederation/oxAuth/blob/version_3.1.4/Server/src/main/java/org/xdi/oxauth/service/AuthenticationService.java#L120
            logged_in = authenticationService.authenticate(user_name, user_password)

            if not logged_in:
                print "Pet. Username and password were invalid"
            else:
                # Here I'll check if logged user has some pet name stored in his entry, otherwise a variable will be set to 
                # flag that the flow will ends earlier (no second factor)

                # Obtain the subject, user is an instance of https://github.com/GluuFederation/oxAuth/blob/version_3.1.4/common/src/main/java/org/xdi/oxauth/model/common/User.java
                # which derives from https://github.com/GluuFederation/oxAuth/blob/version_3.1.4/common/src/main/java/org/xdi/oxauth/model/common/SimpleUser.java
                # and https://github.com/GluuFederation/oxCore/blob/version_3.1.4/oxLdapSample/src/main/java/org/gluu/ldap/SimpleUser.java

                user = authenticationService.getAuthenticatedUser()
                print "Pet. User %s is authenticated" % user.getUserId()

                # I assume you are storing pet's name in secretAnswer attribute
                pet = user.getAttribute("secretAnswer")
                if pet == None:
                    print "Pet. No pet for this user"
                else:
                    print "Pet. Flow will proceed with second factor challenge"
                    # Store pet name for later use
                    identity.setWorkingParameter("pet_name", pet)
                    # I think one can only store strings, but it's not so terrible

            return logged_in

        if step == 2:
            # Here the pet's name is check for a match. Check prepareForStep first
            
            # Retrieve from the request the petName entered
            pet = ServerUtil.getFirstValue(requestParameters, "PetForm:petName")
            userPet = identity.getWorkingParameter("pet_name")
            
            if pet != None and userPet != None:
                if StringHelper.equalsIgnoreCase(pet, userPet):
                   print "Pet. Right pet name!, granting access"
                   return True
                else:
                   print "Pet. Wrong pet name!"
            else:
                print "Pet. No pet name was entered, or the session expired"
                # Ideally here, you should be able to set the message error appearing in the page, but it has never worked for me, so
                # I commented the code:
                # facesMessages = CdiUtil.bean(FacesMessages)
                # facesMessages.setKeepMessages()
                # facesMessages.clear()
                # facesMessages.add(FacesMessage.SEVERITY_ERROR, "Wrong pet name!")
            
            return False


    # This is called just before the forms are shown for the current step. It's normally employed to set variables that
    # intercommunicate steps or some other pre-processing
    # Signature matches that of authenticate method
    def prepareForStep(self, configurationAttributes, requestParameters, step):
        
        # It's very common most scripts do nothing when preparing for step (specially step = 1)
        print "Pet. Prepare for Step %s" %step
        return True


    # Return value is a java.util.List<String> 
    def getExtraParametersForStep(self, configurationAttributes, step):
        # If I don't do this, I cannot retrieve the pet name in authenticate method (step 2)
        return Arrays.asList("pet_name")


    # This method determines how many steps the authentication flow may have
    # It doesn't have to be a constant value
    def getCountAuthenticationSteps(self, configurationAttributes):
    
        identity = CdiUtil.bean(Identity)
        # halts the flow at 1 or 2 depending on the existence of pet_name
        return 1 if identity.getWorkingParameter("pet_name") == None else 2


    # The xhtml page to render upon each step of the flow
    # returns a string relative to oxAuth webapp root
    def getPageForStep(self, configurationAttributes, step):
        if step == 1:
            # Empty string implies using the default Gluu SSO form (/login.xhtml)
            return ""
        else:
            # This page should be placed at /opt/gluu/jetty/oxauth/custom/pages
            return "/auth/pets.xhtml"

    # This is unknown terrain for me
    def logout(self, configurationAttributes, requestParameters):
        return True
