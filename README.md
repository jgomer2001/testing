# Credential Manager 

# What is credential manager?

A web application that will allow users to self service the management of their various credentials. A user may handle any combination of credentials types such as:
* U2F security keys
* OTP
* Super Gluu devices
* Mobile phone numbers (for delivering passcodes via SMS)

The management consists of enrolling new credentials (devices), and updating or deleting existing ones. Also, the application will allow users to choose  their preferred method for authentication: whether using basic password only or enabling two-factor authentication with the usage of already enrolled devices.

# Project's scope

Initially this project is aimed at delivering a MVP which will be available for users of Gluu's support portal and the oxd license management portal. This will allow us to elicit valuable feedback from customers to enrich the capabilities of the web app itself. 

For this MVP no license is needed, however, the app requires oxd (a licensed middleware component).

This [file](https://trello-attachments.s3.amazonaws.com/57150e91a415045e27c57ad0/594155c64b012a416ca2e8dc/abf35915d9ba6ab467b06117dbf43dca/cred-manager-mockups.png) is the mockup of credential manager and depicts to a good extent how it will look like and the functionalities it is expected to include. Note the representation of credential types mentioned above and the existence of two roles: a *regular user*, and an *administrator user*.


# Requirements

## The actors

A *regular user* will be able to do management of its own credentials, as well as using login and logout functionalities.

An *admin user* (who is a Gluu server administrator) has access to the same functionalities. He is also allowed to set up configurations needed for credential manager. These functionalities will not be accessible by the UI itself and will take place by tweaking configuration files. The app will have a help page for admins to learn how to configure credential manager behavior.


## Functional requirements


### 2FA behavior and preferred method

Second-factor authn will come into play only after a user has added at least two credentials in the app. Otherwise, the effective mechanism that takes place is user+password authn.

As an example, assume the admin user of a credential manager installation has enabled the following for his organization: supergluu, google authenticator, and U2F keys. Thus, users of that particular installation have to add any of the following before being able to set his preferred authentication method (and taking advantage of 2FA):

* 2 U2F keys
* 1 U2F key and 1 mobile app
* 2 mobile apps

where "mobile app" can be any of: supergluu, google authenticator.

If a user has added none or only one credential, he will be warned that he cannot set a preferred method other than password until he takes appropriate action. 

Whenever the condition is met (at least two enrolled credentials), he will be advised to change his preferred method.

See [Available authentication methods](#available-authentication-methods) for more on this regard.

### Home page contents

The landing page of the app (after user's authentication takes place) will show the summary of credentials added so far. For every credential type enabled by the admin (e.g. mobile phone, U2F key), the user will see:

* Number of enrolled credentials of this type
* The nicknames of such credentials
* A link/button to a [full-view page](#full-view-page) for this type of credentials

Additionally, in this page users can:

* Choose their preferred method for authn (only if the 2FA criterion is met, see above)
* Change their passwords (if the admin has enabled this functionality). Particularly, when typing a new password, the app will hint users about the strength of such password.

The following sub-sections list data needed to **enroll** credentials according to type:

#### Mobile phone number

* Nickname for this phone number
* Mobile phone number
* A code sent via SMS

#### U2F security keys

* Nickname for key

See additional considerations [here](#fido-u2f-restrictions)

#### Super Gluu

* Nickname for device

*Note:* Super gluu mobile app must be installed on device beforehand.

#### Google Authenticator

* Nickname for device

*Note:* Mobile app must be installed on device beforehand.


### Full-view page

Every credential type will have a proper page so that users can list or alter credentials of that type. For listing, the following attributes will be displayed:
* Nickname
* Date-time added
* Last used date-time
* Phone number (only for this type of credential)

*Notes:*
* Updating a credential involves assigning a different nickname for the credential. For changing additional attributes, the user will have to delete that credential and do enrollment once more.

* Deleting a credential only requires prompting the user for completing the action. This action cannot be undone. Also, this may potentially restore the preferred authn mechanism to "password".

### Use of identifier-first authentication

To instruct the IDP (Gluu server) to present the user with certain authentication method, an appropriate `acr_value` must be passed in the `Get authorization URL` step of OIDC. For this to happen, the application must "identify" the user beforehand to be able to determine which preferred method to pass (i.e. lookup in LDAP).

Hence, when a user tries to visit the home page of credential manager, this flow occurs:
* A form field is presented to the user asking to enter his username. Then he/she presses a "next" button
* A new field appears where user can choose the authn method wanted for this session. This list is populated with values applicable for the current cred. manager installation (see [Available authentication methods](#available-authentication-methods)). Default selected method corresponds to the already-set preferred method for this user or "password" if he has none.
* User presses a "next" button and is taken to the SSO form where authentication takes place according to `acr_value` passed

### Application configuration details

#### Available authentication methods 

This [image](https://github.com/GluuFederation/cred-manager/raw/master/imgs/arch_detailed.jpg) gives a good perspective of the runtime context of the application. As oxAuth is required (and hence, a Gluu Server CE installation),  methods supported for authentication vary depending on customer setup. As a result, credential manager will be able to offer (at most) only methods already supported by the gluu server, namely, those listed in the `acr_values_supported` property of the OpenID Connect configuration metadata URL.

#### Configuration file

In a single file written in JSON format, the admin will be able to:

* Constraint the authentication mechanisms supported (a subset from U2F, Super Gluu, OTP, SMS) taking into account the methods already supported by the local Gluu CE installation
* Enable password reset (if this is not the case, the UI will hide any detail about this functionality for users)
* oxd settings: host, port, oxid
* OpenID connect metadata URL
* SCIM v2 service URL
* Settings for SMS delivery (e.g. twilio account)
* Settings for local LDAP connection

## Non-functional requirements

### UI
Credential manager must run and look consistently on a variety of devices, whether desktop or mobile, regardless of underlying browser, operating system, or screen size. The app is expected to deliver a comfortable experience in terms of usability and responsiveness.

In `https://erasmusdev.gluu.org/cred-manager/user.zul` there is a small UI prototype for credential manager.

### FIDO U2F restrictions
* Only certain browsers allow enrollment of U2F security keys. The user should be alerted if his browser does not support this capability.
* Only computers with USB port availability will allow enrolling U2F security keys.

## Requirements to be included in future versions

### UI customizations

To enable branding, credential manager should be customizable so that customers can make it match their own existing web design. This should be performed by adding CSS and images (logos, icons) to the app.

### E-mail notifications

### Auditing capabilities

### Connected apps and sites

### Profile management


# Technical decisions

With exception of e-mail messaging, all considerations stated [here](Technical-considerations) still apply for the MVP.

Also, design and implementation decisions taken should follow these principles:
* Flexibility: this app will require adding functionalities and doing enhancements specially after its inception, so this is a fact to keep in mind
* Simplicity: this also favors the evolution of the app and helps keeping the project manageable

# Project plan

The following describes the activities proposed to fulfil delivery of MVP version of credential manager:

|Activities			| 		|dates|
|------------------------------|-----------------------|---------------|
|Definition of application's general requirements||Jun 7-16|
|Revision of compatible UI frameworks for app||Jun 12-15|
|Revision of projects to reuse for app implementation||Jun 15-21|
|Create UI prototype and feedback session||Jun 19-26|
|Refine scope for MVP||26-30|

Every activity in the following table contains a respective testing phase:

|Activities			|notes|proposed dates*|
|------------------------------|-----------------------|---------------|
|Code app's front-end|most relevant aspects only|Jul 3-7|
|	UI components|||
|	presentation logic|||
|
|Architecture of back-end solution||Jul 10-12|

	Define interfaces of key components
	Define structure of configuration files

User login/logout functionality	Jul 13-14
(identifier-first authn using password only) 
	
Enrollment of credentials (adding only)	Jul 17-28
	Phone SMS
	OTP
	Super gluu
	Security key

Additional actions on credentials (deleting, editing)	Jul 31-Ago 4

Management of preferred authn method	Ago 7-9

Password reset functionality	Ago 10-11

Configuration and deployment in remote testing environment (`erasmusdev`) Ago 14-16

Testing on remote environment and fixes Ago 17-22

Last round of enhancements, tests, and fixes	Ago 22-25

Write doc pages for admin	Ago 28-29

QA tests: *TBD*

Integrations
	Gluu's support portal: *TBD*
	oxd license management portal:	*TBD*

(*) *All dates are 2017*

