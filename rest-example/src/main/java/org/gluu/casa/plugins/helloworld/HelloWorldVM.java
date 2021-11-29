package org.gluu.casa.plugins.helloworld;

import java.util.List;

import javax.ws.rs.client.Entity;
import javax.ws.rs.client.Client;
import javax.ws.rs.client.WebTarget;
import javax.ws.rs.core.HttpHeaders;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

import org.apache.http.client.HttpClient;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.http.impl.conn.PoolingHttpClientConnectionManager;
import org.jboss.resteasy.client.jaxrs.ResteasyClientBuilder;
import org.jboss.resteasy.client.jaxrs.engines.ApacheHttpClient4Engine;

import org.gluu.casa.misc.Utils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.zkoss.bind.annotation.Init;
import org.zkoss.bind.annotation.NotifyChange;

public class HelloWorldVM {

    private Logger logger = LoggerFactory.getLogger(getClass());

    private Client getClient() {
        HttpClient httpClient = HttpClientBuilder.create().setConnectionManager(new PoolingHttpClientConnectionManager()).build();
        ApacheHttpClient4Engine engine = new ApacheHttpClient4Engine(httpClient);
        return new ResteasyClientBuilder().httpEngine(engine).build();
    }

    @Init
    public void init() {
        ConsentRequest req = new ConsentRequest();
        req.setCustomerid("boda@gmail.com");
        
        logger.info("Getting a JAX-RS webtarget");
        WebTarget target = getClient().target("https://idp.openitio.com/consent/").path("getUserConsents");
        
        logger.info("Sending post");
        Response response = target.request().header(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON)
            .post(Entity.json(req));

        ConsentResponse cr = response.readEntity(ConsentResponse.class);
        
        List<Consent> list = cr.getConsentList();
        logger.info("Received {} consents", list.size());
        logger.info("1st one is:  provider = {}; consentId = {}", list.get(0).getProvider(), list.get(0).getConsentId());
        
        response.close();
    }

}
