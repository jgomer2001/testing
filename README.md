# Manual installation

This documents provides detailed instructions on how to deploy Credential Manager if you are using Gluu Server 3.0.2 or 3.1.1. If you are using 3.1.2 please follow the simpler process for this [here](installation.md).

## Requirements

To run this application you need:

1. A working Gluu Server installation with at least the following components installed: Apache, LDAP, oxAuth, and oxTrust.

2. An active [oxd](https://oxd.gluu.org) installation, version 3.1.1 or higher. See [oxd-setup below](#oxd-setup).

!!! Note
    Credential Manager must be installed in the same host as your Gluu Server, and should ideally reside within the Gluu Server chroot container. It is **recommended** to perform all the steps inside Gluu Server chroot.
    
## oxd setup

Install [oxd](https://www.gluu.org/docs/oxd/). Note that you need a [license](https://oxd.gluu.org) for it to run. You will be given 4 bits of data: license ID, public Key, public password, and license password. As stated in the docs, you have to provide license details in the `oxd-conf.json` file.

By default oxd needs to be installed on the same server where the app to be secured is running. If you enable oxd-https-extension, oxd can be installed on a separate server with network access.

Double check that dynamic registration of clients is enabled in your oxauth configuration. To do so, login to oxTrust and go to `Configuration` > `Json configuration` > `oxAuth configuration`. The  **dynamicRegistrationEnabled** property must be set to true.
  
## Update LDAP schema

Add the following three attributes to Gluu LDAP schema. These are needed for the application to work properly.

```
attributetype ( oxAttribute:<NUMERIC-ID> NAME 'oxPreferredMethod'
	DESC 'cred-manager - preferred method (acr) to use for user authentication'
	EQUALITY caseIgnoreMatch
	SUBSTR caseIgnoreSubstringsMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.15
	X-ORIGIN 'Gluu created attribute' )
	
attributetype ( oxAttribute:<NUMERIC-ID> NAME 'oxOTPDevices'
	DESC 'cred-manager - Json representation of OTP devices. Complementary to oxExternalUid attribute'
	EQUALITY caseIgnoreMatch
	SUBSTR caseIgnoreSubstringsMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.15
	X-ORIGIN 'Gluu created attribute' )
	
attributetype ( oxAttribute:<NUMERIC-ID> NAME 'oxMobileDevices'
	DESC 'cred-manager - Json representation of mobile devices. Complementary to mobile attribute'
	EQUALITY caseIgnoreMatch
	SUBSTR caseIgnoreSubstringsMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.15
	X-ORIGIN 'Gluu created attribute' )
````

For more information on how to add attributes, visit this [page](https://www.gluu.org/docs/ce/admin-guide/attribute/#add-the-attribute-to-ldap). Additionally, you have to associate the new attributes to the appropriate LDAP object class for user:

```
objectclass ( oxObjectClass:... NAME 'gluuPerson'
	...
	MAY ( ...$ oxPreferredMethod $ oxOTPDevices $ oxMobileDevices)
	...
```

Restart your LDAP service as indicated in the [attribute management page](https://www.gluu.org/docs/ce/admin-guide/attribute/#add-the-attribute-to-ldap).

## Create a new Jetty base

A Jetty base allows isolation among web applications as well as among configurations in the same Jetty server. Credential manager must run on its own dedicated base so you will have to create one. Use [these instructions](http://www.eclipse.org/jetty/documentation/current/quickstart-running-jetty.html) as a guide.

The following switch is recommended: `--add-to-start=jsp,servlets,ssl,http,deploy,https,console-capture`.

Make the SSL configurations required for your Jetty instance. This can be done in different ways. You can use [these instructions](http://www.eclipse.org/jetty/documentation/current/configuring-ssl.html) as a guide.

!!! Warning: 
    Running cred-manager over **SSL** is a requirement.

## Create a sample configuration file

Credential manager reads all its required runtime configurations from a file called `cred-manager.json`. This file is expected to reside inside a `conf` directory placed in a folder whose location is given by the Java system property *gluu.base*. If such system property is not present, the default value used is `/etc/gluu`. 

Please add the mentioned property to your Jetty base. This is usually done by inserting an entry in the `start.ini` file of the recently created jetty base directory, like this:

```
	...
	-Dgluu.base=/opt/gluu/jetty/cred-manager
```

Create the `conf` directory and copy a [sample configuration file](https://github.com/GluuFederation/cred-manager/blob/master/configurations/cred-manager.json) there.

Further on, in the [configuration section](#configuration-file), you will learn how to tweak this file to suit your needs.

Ensure the operating system that runs Jetty has read/write access to this file.

## Set location for logs

Additional to *gluu.base* cred-manager uses another system property: *log.base*. This one is used to determine where to write logs. Log files are stored inside a `log` directory relative to the folder pointed to by *log.base*. Both *gluu.base* and *log.base* can point to the same location.

The following is an example of a `start.ini` file

```
	...
	-Dgluu.base=/opt/gluu/jetty/cred-manager
	-Dlog.base=/opt/gluu/jetty/cred-manager
```	

The set up of these environment properties resemble the same pattern currently used in **oxAuth** and **oxTrust**.

## Add the "credmanager" custom scripts and dependencies

In oxTrust admin UI, add a new custom script named **credmanager** with the contents of file `cred-manager.py` found [here](https://github.com/GluuFederation/cred-manager/blob/master/configurations). To do so visit `Configuration` > `Manage custom scripts` > `Person authentication`. Use the appropriate file according to your Gluu server version.

Add the following configuration properties to the script:

* **supergluu_app_id**. As value use exactly the same you will provide for *"authz_redirect_uri"* in the [configuration file](#configuration-file). In most cases this is the URL where the cred-manager application will be published.
* **u2f_app_id**. As value use exactly the same you will provide for *"app_id"* under *"u2f_settings"* in the [configuration file](#configuration-file). In most cases this is the URL of your Gluu server host (aka *oxAuth issuer* URL).

Do not check "Enabled" yet. Just save your changes using the button provided at the bottom of the page.

Transfer the associated custom login pages of **credmanager** to your server:

* Inside chroot, create a directory named `cm` under `/opt/gluu/jetty/oxauth/custom/pages`. Copy the files with `xhtml` and `xml` extension found at [https://github.com/GluuFederation/cred-manager/blob/master/configurations](https://github.com/GluuFederation/cred-manager/blob/master/configurations) to the created folder. Use the version of files matching your Gluu server.

Add libraries required by the script:

* Copy this [jar file](http://search.maven.org/remotecontent?filepath=com/twilio/sdk/twilio/7.12.0/twilio-7.12.0-jar-with-dependencies.jar)(~7MB) to `/opt/gluu/jetty/oxauth/lib/ext` inside Gluu chroot. Ensure the operating system user that runs Jetty has read-access to it.

Finally, in the tab labeled "Client registration" add a new **credmanager** custom script using the contents of this [file](https://github.com/GluuFederation/cred-manager/blob/master/configurations/3.1.2/client_registration.py). 

Add the following configuration properties to the script:

* **client_redirect_uris**. As value use exactly the same you will provide for *"authz_redirect_uri"* in the [configuration file](#configuration-file). In most cases this is the URL where the cred-manager application will be published.

Check "enabled" and the press the "update button".

## Enable custom scripts for authentication methods

In oxTrust UI, navigate to `Configuration` > `Manage custom scripts`. Enable the custom scripts required for your particular case. For instance, if you plan to offer users the possibility to enroll u2f keys, enable the u2f script, if you want to support OTP sent via SMS, enable the Twilio script.

!!! Note: 
    If you haven't setup custom scripts before, the [User authentication intro](https://www.gluu.org/docs/ce/authn-guide/intro) and [Interception scripts page](https://www.gluu.org/docs/ce/admin-guide/custom-script) are important reading. A recommended practice is to enable one script, then add (enable) the associated method in cred-manager, and once you can enroll devices of this kind, continue with the rest of methods.

Ensure that settings of scripts are properly configured. It is advisable to:

* Check the contents of file `oxauth_script.log` (found at `/opt/gluu/jetty/oxauth/logs`). You should not see errors there but only successful initialization messages. Every time you enable a script, you have to wait one minute for the server to pick the changes.

* Test scripts are actually working fine. To see a script in action, you may change the authentication method used in oxTrust to test a certain script: go to `Manage authentication` > `Default authentication method` > `oxTrust acr`, and choose the name of the script of interest. Wait a couple of minutes and try to login in a different browser or private browsing session.

Once you are confident of the behavior of your custom scripts, proceed to enable the already listed script called **credmanager** under the "Person Authentication" tab. This script is a key requirement for the application to work. Just ensure the `oxauth_script.log` says it is inited correctly - no need to use it as oxTrust default authentication mechanism. Ensure the script properties are:

* **supergluu_app_id** (normally points to the URL where cred-manager will be accesible, e.g. `https://mygluuhost.com/cred-manager`)
* **u2f_app_id** (normally points to the server itself, e.g. `https://mygluuhost.com`)

Finally in the "Client registration" tab, enable the script labeled "Cred-manager Client Registration script". Make sure the property **client_redirect_uris** looks like `https://mygluuhost.com/cred-manager`.

### Additional settings

* If you plan to use Super Gluu or a TOTP/HOTP mobile app as authentication method, and you are running cred-manager outside the Gluu Server chroot, please create filesystem links so that files referenced by the custom scripts (Super Gluu or TOTP/HOTP) can be readable from outside the Gluu container. For instance, there is a property labeled *"otp_conf_file"* for the OTP script that references a file like `/etc/certs/otp_configuration.json`. You should create a link such that `/etc/certs/otp_configuration.json` actually points to `/opt/gluu-server-<version>/etc/certs/otp_configuration.json`.

* If you plan to use OTP messages sent by SMS as an authentication method for your users, also copy the jar file of Twilio 6.3 library found [here](http://search.maven.org/remotecontent?filepath=com/twilio/sdk/twilio-java-sdk/6.3.0/twilio-java-sdk-6.3.0-jar-with-dependencies.jar)(~4MB) to `/opt/gluu/jetty/oxauth/lib/ext` inside Gluu chroot. Ensure the operating system user that runs Jetty has read-access to it.

## Configuration File

Credential manager reads all its required runtime configurations from a file called `cred-manager.json`. Create your own as instructed [here](#create-a-sample-configuration-file).

Setting up this file is a one-time task. After the first successful application start, all administrative configurations can be performed through the UI of the application itself.

!!! Note: 
    Ensure that the operating system user that runs Jetty has read/write permissions over this file. Backup it up once you feel comfortable with the configuration of the application.

The following is an example of the contents of `cred-manager.json`. **Note:** The comments added make the file not a valid Json tree.

```
{
"ldap_settings":{
	"ox-ldap_location": "/etc/gluu/conf/ox-ldap.properties",	//Location of ox-ldap.properties file
	"salt" : "/etc/gluu/conf/salt", //Optional. location of salt properties file
	"applianceInum": "@!...",
	"orgInum": "@!..."
},
"enable_pass_reset": true,	//optional
"oxd_config": { 
	"host": "localhost",
	"port": 8099,
	"use_https_extension" : true,	//optional
	"authz_redirect_uri" : "..."  //must be the root URL for this webapp
},
"enabled_methods": [twilio_sms, super_gluu],	//optional
"u2f_settings" : {	//optional
	"u2f_relative_uri" : "restv1/fido-u2f-configuration",	//optional. Endpoint for registration of fido devices
	"app_id" : null		//optional. The U2F app ID
},
"branding_path" : "/opt/gluu/jetty/cred-manager/custom",	//optional. Used only if custom branding is required
"min_creds_2FA" : 2,	//optional
}
```

Most properties there are optional. The following is a minimalist example:

```
{
"ldap_settings":{
	"ox-ldap_location": "/etc/gluu/conf/ox-ldap.properties",
	"salt" : "/etc/gluu/conf/salt",
	"applianceInum": "@!...",
	"orgInum": "@!..."
},
"oxd_config": { 
	"host": "localhost",
	"port": 8099,
	"authz_redirect_uri" : "https://acme.info/cred-manager"
}
}
```

You can find a sample configuration file [here](https://github.com/GluuFederation/cred-manager/blob/master/configurations/cred-manager.json). 

Adjust the contents of this file to fit the needs of your organization. The remainder of this subsection gives useful hints to complete this task. The topic of custom branding will be regarded later.


### Meaning conveyed by the contents of `cred-manager.json`

The following are some important notes on how cred-manager uses the information found in the configuration file:

* cred-manager uses `ox-ldap.properties` file to lookup LDAP connection settings. Once connected to LDAP, cred-manager searches for:
	* displayName attribute in the `o` branch to determine the organization name to show in the UI
	* oxTrust's oxTrustConfCacheRefresh attribute to determine if a source backend LDAP is being used ("sourceConfigs" property inside the JSON content). If so, password reset won't be enabled regardless of the value of *"enable_pass_reset"*. 
	* oxAuth's oxAuthConfDynamic attribute to get:
		* the OIDC config endpoint (property "openIdConfigurationEndpoint" in JSON content)
		* the issuer attribute
		* dynamicRegistrationExpirationTime attribute

* If *"enable_pass_reset"* is not provided and there is no backend LDAP detected, a default value of false is assumed.

* If *"enabled_methods"* is not present, or has empty value or null, cred-manager will use all supported authentication methods (that is, all methods corresponding to the custom scripts enabled in the previous section). A method is ignored if its associated custom script has not been enabled yet. To quickly determine the active methods supported by your Gluu Server inspect the `acr_supported_values` property of the server's OIDC metadata document (e.g. `https://<host>/.well-known/openid-configuration`)

* *"authz_redirect_uri"* will be used as the return URL after the login process takes place at the IDP. For this, the root URL where the webapp will be accessible must be used. Don't mind about the trailing slash. 

* If *"u2f_relative_uri"* is not present, or has empty value or null, it will default to ".well-known/fido-u2f-configuration". The value of issuer property found in LDAP followed by a slash (/) will be prepended to this to get a correct endpoint URL for U2F devices enrolling.

* If *"app_id"* is not present, or has empty value or null, it will default to the *issuer* value in oxAuth's *oxAuthConfDynamic*. This string will be used as the facet for this application (in [U2F dev jargon](https://developers.yubico.com/U2F/App_ID.html)). In very uncommon circumstances you will have to supply a value here.

* If "min_creds_2FA" is not present it will default to 2. This property defines the minimum amount of credentials any user must enroll to be able to use second factor authentication.


### "Hidden" properties

These are extra properties that can be set in the JSON file to tweak certain behaviors. Mostly useful in development scenarios:

* *"gluu_version"*: cred-manager attempts to check the "Implementation-Version" entry in the `MANIFEST.MF` file inside `oxauth.war` to guess the Gluu version it is running on. Providing a value here obviates the need for inspecting the war file. When providing a value use a string (e.g. "3.1.2").

* *"log_level"*: Customizes the default logging level used by the application. If not provided, default value used is **"INFO"**. Valid values are: OFF, FATAL, ERROR, WARN, INFO, DEBUG, TRACE, ALL.

## Run the app

Copy the [.war file](http://ox.gluu.org/maven/org/xdi/cred-manager/) of cred-manager to your [jetty base webapps directory](installation.md#create-a-new-jetty-base). You can copy a exploded directory too.  Depending on previous setup, you may need to issue a command for starting the app, or if hot deployment is used (default behavior in Jetty) this is not needed.

Wait a few seconds while the app starts. Check the log file of the app (e.g. `/opt/gluu/jetty/cred-manager/logs/2017_10_31.jetty.log`). You should see a message that reads "WEBAPP INITIALIZED SUCCESSFULLY". Check the [troubleshooting guide](troubleshooting.md) if things are not going as expected.

When the application is started, oxd client registration takes place. This can be verified in oxTrust where a new client appears listed with a name similar to "cred-manager".

## Apply other configurations

* Note that after the first successful application start, all administrative configurations can be performed through the UI of the application itself. If, for some reason, you still want to edit the `cred-manager.json` file, an application restart is required to pick the changes. 

* Remember that you don't even need to provide "enabled_methods" in `cred-manager.json` if you just want to be able to use all credential types supported (currently limited to OTP device, verified mobile phone, U2F key, and super gluu device only).

* Ideally, not only cred-manager should use the **credmanager** script, but all applications under the SSO umbrella in your organization. This script allows to implement an authentication workflow based on credentials already enrolled by users and their preferences.  For this to happen, apply **credmanager** as the default authentication mechanism at the server level: in oxTrust go to `Manage authentication` > `Default authentication method` > `Default acr` and choose **credmanager**.
