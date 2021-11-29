package org.gluu.casa.plugins.helloworld;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class ConsentResponse {

    @JsonProperty("Consent")
    private List<Consent> consentList;

    public List<Consent> getConsentList() {
        return consentList;
    }
    
    public void setConsentList(List<Consent> l) {
        consentList = l;
    }

}