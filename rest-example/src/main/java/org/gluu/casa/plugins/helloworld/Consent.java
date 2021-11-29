package org.gluu.casa.plugins.helloworld;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
public class Consent {
    private String consentId;
    private String provider;
    
    public String getConsentId() {
        return consentId;
    }
    
    public String getProvider() {
        return provider;
    }
    
    public void setConsentId(String id) {
        consentId = id;
    }
    
    public void setProvider(String p) {
        provider = p;
    }
    
}