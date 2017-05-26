# Overview
The Gluu Server supports UMA protection for SCIM endpoints from Gluu Server CE 2.4.0 onwards. 
A machine based authorization method is used to obtain access tokens. SCIM/UMA is built
into the Gluu Server CE and does not require any special package or installation. 

## Requirements

* Install Gluu Server CE following the [Installation Guide](../installation-guide/index.md). The setup script prepares all 
configurations needed for SCIM UMA RS endpoints and SCIM UMA RP client; **RP** stands for requesting party, and **RS** stands for resource server. See terminology and definitions for UMA [here](https://docs.kantarainitiative.org/uma/rec-uma-core.html#introduction).

* Locate your SCIM RS and SCIM RP Client IDs. These are found in the file `/install/community-edition-setup/setup.properties.last` inside the chroot container of your Gluu CE installation. Use the following command to extract these quicky: `cat setup.properties.last | grep "scim_rs_client_id\|scim_rp_client_id"`.

* The UMA SCIM client requires JWKS. The keystore file is located at `/install/community-edition-setup/output/scim-rp.jks`. The password associated to this keystore is found in `setup.properties.last` and defaults to "*secret*".

**NOTE:** For versions earlier than v2.4.4, the JWKS file resides in `/install/community-edition-setup/output/scim-rp-openid-keys.json` instead.

## Configuration

* Activate UMA custom script in Gluu's CE web UI. Go to Configuration > Manage Custom Scripts, and in the tab for "UMA Authorization policies" check "Enabled" at the bottom.

![enable uma](../img/scim/enable_uma.png)

* Enable SCIM from Configuration > Organization Configuration

![enable scim](../img/scim/enable-scim.png)

* oxTrust SCIM UMA configuration is automatically updated while running 
the `setup.py` and the correct values are setup 
in the [oxtrust-config.json](https://github.com/GluuFederation/community-edition-setup/blob/master/templates/oxtrust-config.json#L122) file.
```
  "umaIssuer":"https://%(hostname)s",
  "umaClientId":"%(scim_rs_client_id)s",
  "umaClientKeyId":"",
  "umaResourceId":"1447184268430",
  "umaScope":"https://%(hostname)s/oxauth/seam/resource/restv1/uma/scopes/scim_access",
  "umaClientKeyStoreFile":"%(scim_rs_client_jks_fn)s",
  "umaClientKeyStorePassword":"%(scim_rs_client_jks_pass_encoded)s",
```
  `umaClientKeyId` can be updated with the `alias` from `scim-rp.jks` file; if it is not updated, the first key from the file is used automatically.

## Testing SCIM UMA

The following instructions depict how to test the SCIM configuration protected by UMA. It uses [SCIM-Client](https://github.com/GluuFederation/SCIM-Client) - a Java library also developed by Gluu intended for client applications. For a deeper insight into this topic please visit [User Management with SCIM](user-scim.md).

* Add the SSL certificate of your Gluu server to the JRE's `cacerts` certificate key store where your client application will run. There are lots of articles around the Web on how to import a certificate to the keystore. To get the certificate file (.crt), you may for instance open a browser and point to Gluu CE administrative console. Then, click in the icon on the left of the URL and see the certicate's details. You will be shown an option to export or save it to disk.

* If you are using Maven, below is how to add the SCIM-Client to your project:
```
<repositories>
  <repository>
    <id>gluu</id>
    <name>Gluu repository</name>
    <url>http://ox.gluu.org/maven</url>
  </repository>
</repositories>
...
<dependency>
  <groupId>gluu.scim.client</groupId>
  <artifactId>SCIM-Client</artifactId>
  <version>${scim.client.version}</version>
</dependency>
```

As a good practice, the SCIM-Client to use should match your Gluu CE version. For example, if you are running CE v3.0.1, you must also use SCIM-Client v3.0.1.

* Create a file with the following sample content. Here it is assumed you named the file scim-client.properties
```
json_string = {	\
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],	\
  "externalId": "12345",	\
  "userName": "newUser",	\
  "name": { "givenName": "json", "familyName": "json", "middleName": "N/A", "honorificPrefix": "", "honorificSuffix": ""},	\
  "displayName": "json json",	\
  "nickName": "json",	\
  "profileUrl": "http://www.gluu.org/",	\
  "emails": [	\
    {"value": "json@gluu.org", "type": "work", "primary": "true"},	\
    {"value": "json2@gluu.org", "type": "home", "primary": "false"}	\
  ],	\
  "addresses": [{"type": "work", "streetAddress": "621 East 6th Street Suite 200", "locality": "Austin", "region": "TX", "postalCode": "78701", "country": "US", "formatted": "621 East 6th Street Suite 200  Austin , TX 78701 US", "primary": "true"}],	\
  "phoneNumbers": [{"value": "646-345-2346", "type": "work"}],	\
  "ims": [{"value": "test_user", "type": "Skype"}],	\
  "userType": "CEO",	\
  "title": "CEO",	\
  "preferredLanguage": "en-us",	\
  "locale": "en_US",	\
  "active": "true",	\
  "password": "secret",	\
  "groups": [{"display": "Gluu Test Group", "value": "@!9B22.5F33.7D8D.B890!0001!880B.F95A!0003!60B7"}],	\
  "roles": [{"value": "Owner"}],	\
  "entitlements": [{"value": "full access"}],	\
  "x509Certificates": [{"value": "cert-12345"}]	\
}
```

The backslashes "\\" allow us to span the contents in several lines.

* Create a Java class using the code below (supply suitable values for calling the `umaInstance` method):

```
Properties p= new Properties();
p.load(new FileInputStream("scim-client.properties"));
String jsonPerson=p.getProperty("json_string");

Scim2Client client = Scim2Client.umaInstance(domain, umaMetaDataUrl, umaAatClientId, umaAatClientJksPath, umaAatClientJksPassword, umaAatClientKeyId);
client.createPersonString(jsonPerson, MediaType.APPLICATION_JSON);
```

**NOTE:** Take into consideration that when you re-install Gluu CE, UMA parameters and JWKS files are regenerated.

## SCIM 2.0 Test Mode (v2.4.4+)

Starting with CE v2.4.4, the "test mode" configuration will help developers test the SCIM 2.0 endpoints easier. Instead of UMA + SCIM-Client, in test mode a long-lived OAuth2 access token issued by the Gluu server is used to authorize with the SCIM 2.0 endpoints.

To enable test mode, do the following:

* Login to the oxTrust GUI  
* Navigate to `Configuration` > `JSON Configuration` > `OxTrust Configuration`, 
then locate the property `scimTestMode`.

![image](../img/scim/scim-test-mode-false.png)

* Set it to `true`.
* click the `Save Configuration` button. 
The Gluu server will then create a long-lived OAuth2 access token with a 
validity period of one year. Doing this will also switch the authentication 
scheme from UMA to OAuth2 Access Token.
* Click on  `JSON Configuration` > `OxTrust Configuration` in the left navigation pane. 
This will retrieve the access token and be displayed in the `scimTestModeAccessToken` property.

![image](../img/scim/scim-test-mode-true.png)

* If the access token has expired, just repeat the previous steps to create a new one.
 
The access token can then be used as the query string 
parameter `access_token` in accessing the SCIM 2.0 endpoints, for example:

![image](../img/scim/scim-test-mode-example.png)

You can verify the current authentication scheme of the SCIM 2.0 
endpoints by browsing its `ServiceProviderConfig`:

![image](../img/scim/scim-test-mode-config.png)

To exit test mode, just set `scimTestMode` back to `false` then 
 click the `Save Configuration` button. This will switch the 
authentication scheme from OAuth2 Access Token to UMA. If you try using 
your access token again, you will now get the `403 Unauthorized` error:

![image](../img/scim/scim-test-mode-403.png)

# Notes
SCIM is protected by UMA in Gluu Server Community Edition (CE). 
The usage of UMA requires HTTP GET and HTTP POST requests. Before testing, 
the Client making the requests must be added/registered in Gluu CE. The UMA 
configuration is available at `https://hostname/.well-known/uma-configuration`. 
The request to authorization endpoint must accompanied with  application/json content type. 

The example below shows the parameters used in a real-life use case  where the 
UMA RPT Token is authorized in oxAuth.

```
public RptAuthorizationResponse requestRptPermissionAuthorization(@HeaderParam("Authorization") String authorization,
    @HeaderParam("Host") String amHost, RptAuthorizationRequest rptAuthorizationRequest);
```

If the default openID SCIM Client is not used, the `inum` must be added to the
UMA Authorization Policy Custom Script.
