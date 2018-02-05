# SCIM API

Gluu Server Community Edition supports the System for Cross-domain Identity Management (SCIM) version 2.0 out of the box, operated using HTTP `GET`, `PUT`, `POST` and `DELETE` commands. SCIM uses a (disabled by default) REST API for these operations. 

To enable SCIM open the oxTrust administration interface and navigate to `Organization Configuration` > `System Configuration`.

![organization-menu](../img/oxtrust/organization-menu.png)

Find `SCIM Support` and select `Enabled`.

![enable](../img/scim/enable.png)

Then enable the protection mode you want for your API, see details [here](../user-management/scim2.md#api-protection).

## HTTP verbs

As a summary these are the HTTP verbs a SCIM server speaks:

|HTTP Method|Description	|
|--------|------------------------------|
|GET|Retrieves one or more resources (e.g. Users/Groups)|
|POST|Creates new resources, executes searches, send bulk requests (batches)|
|PUT|Modifies resources by adding and replacing attributes|
|DELETE|Deletes a resource|

## Resource types

The following resources are supported:

|Resource|Schema URI|Notes|
|-|-|-|
|User|urn:ietf:params:scim:schemas:core:2.0:User|See section 4.1 of RFC 7643|
|Group|urn:ietf:params:scim:schemas:core:2.0:Group|See section 4.2 of RFC 7643|
|Fido devices|urn:ietf:params:scim:schemas:core:2.0:FidoDevice|Represents a [fido credential](../user-management/scim2.md#fido-devices) enrolled by a user|

The following resource extensions are defined:

|Resource|Schema URI|Attributes|
|-|-|-|
|User|urn:ietf:params:scim:schemas:extension:gluu:2.0:User|Attributes can be assigned dynamically via oxTrust|

To learn about the specific capabilities of our server, visit the `/ServiceProvider`, `/ResourceTypes`,  and `/Schemas` endpoints (see below). These endpoints are not protected so you can use a web browser to check. 

## SCIM Endpoints

The following table summarizes the available endpoints in Gluu implementation of SCIM service

|Endpoint|Resource			|HTTP methods		|Description	|
|-|-|-|-|
|[/Users](#users-endpoint)|User|GET, POST, PUT, DELETE|Retrieve, add, modify and delete Users|
|[/Groups](#groups-endpoint)|Group|GET, POST, PUT, DELETE|Retrieve, add, modify and delete Groups|
|[/FidoDevices](#fido-devices-endpoint)|Fido devices|GET, PUT, DELETE|Retrieve, modify and delete Fido devices|
|[/Bulk](#bulk-operation-endpoint)||POST|Applies operations of different kind to a set of resources|
|[/ServiceProvider](#service-provider-configuration-endpoints)||GET|Retrieve service provider configuration|
|[/ResourceTypes](#service-provider-configuration-endpoints)||GET|Retrieve supported resource types|
|[/Schemas](#service-provider-configuration-endpoints)||GET|Retrieve supported schemas info|

!!! Note:
    Actual endpoint URLs are prefixed accordingly with the root URL of SCIM API. As an example, the user's endpoint URL to use in your application should be `https://your.gluu-host.com/identity/restv1/scim/v2/Users`.

SCIM 2.0 is governed by the [SCIM:Core Schema](https://tools.ietf.org/html/rfc7643) and [SCIM:Protocol](https://tools.ietf.org/html/rfc7644) spec docs. The latter contains full details about the API structure, so use it as a reference in your development tasks. 

### Definitions

This section summarizes data model definitions useful to understand what values to supply when interacting with the different endpoints of the API. For more detailed information please:

* See [SCIM:Core Schema](https://tools.ietf.org/html/rfc7643)
* Inspect the contents of the `/Schemas` endpoint. Use a browser for this (none of the service provider configuration endpoints are protected).

#### General

#### About users

#### About groups

#### About Fido devices

### `/Groups`

##### Security

##### GET

###### Parameters

##### POST

###### Parameters

##### Response


### Service Provider Configuration Endpoints

Thesee are three endpoints that facilitate discovery of features of the service itself and about the schema used - in other words, service metadata. Please check section 4 of RFC 7644 for more information.
   
#### `/ServiceProvider`

##### Security
This endpoint is not protected

##### GET

###### Parameters

None (no query params).

##### Response

Information about the capabilities of the server in Json format as decribed in section 5 of RFC 7643.

Status code 200 is returned for a normal response.
   
#### `/ResourceTypes`

##### Security
This endpoint is not protected

##### GET

###### Parameters

None (no query params).

##### Response

Information about the types of resources available in the service (e.g., Users and Groups) in form of a [ListResponse](#listresponse). 

It's possible to request the information for a single resource type by adding a resource name suffix to the URL, for instance `/ResourceTypes/User` for users. In this case, a json is returned according to section 6 of RFC 7643.

Status code 200 is returned for a normal response.
   
#### `/Schemas`

##### Security
This endpoint is not protected

##### GET

###### Parameters

None (no query params).

##### Response

Retrieves the schemas in use by available resources and which are accepted by the service provider.

Output data is in form of a [ListResponse](#listresponse), however it's possible to request the information for a single resource type by adding a schema URI suffix to the URL, for instance `/Schemas/urn:ietf:params:scim:schemas:core:2.0:Group` for groups. In this case, a json is returned according to section 7 of RFC 7643.

Status code 200 is returned for a normal response.

----------
