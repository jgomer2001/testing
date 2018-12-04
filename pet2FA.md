# Use your pet as a second factor!

Make it bark at your computer to get access or if it supports NFC just get it close to your computer :D...

## How to set it up

1. Create a new cust script in oxTrust (person authn tab)

1. In script contents paste [this](./pets.py)

1. Save & check that `oxauth_script.log` shows the following: `Pet. Initialized successfully`

1. Copy [this](./pets.xhtml) custom page to `/opt/gluu/jetty/oxauth/custom/pages/auth` inside chroot

... no need for restarts

## How to test

Have a couple of testing users at hand, set attribute `secretAnswer` for some (I assume pet's name is stored there).

In an app create an authorization request using `acr` equal to the displayName used for script created, or use that `acr` to protect oxTrust (`Manage Authentication` > `Default Authentication method`).

## How it works

Please read all the script code first... it's full of comments

### Step 1

Flow starts with a call to `getPageForStep` with step=1, then `isValidAuthenticationMethod`

This makes the `login.xhtml` (the default SSO gluu form) to be parsed by JSF (in oxAuth)

This provokes a call `prepareForStep` see: https://github.com/GluuFederation/oxAuth/blob/version_3.1.4/Server/src/main/webapp/login.xhtml#L10

Then the form is rendered at the browser, after the button is pressed, `authenticate` is called

Then `getApiVersion`, `getExtraParametersForStep` and `getCountAuthenticationSteps`.

It ends here if user has no petname stored in profile. If the call to `authenticate` returned True, authorization is successful, otherwise denied.

### Step 2

If he had petname, flow starts again for step 2: `getPageForStep`, `isValidAuthenticationMethod`

Now the `/auth/pets.xhtml` comes to play... See the comments [there](./pets.xhtml)

calls proceeding are: `prepareForStep`, `authenticate`, `getApiVersion`, `getExtraParametersForStep` and `getCountAuthenticationSteps`.

Sometimes I see `getExtraParametersForStep` calls also after `getPageForStep` ... :-\
