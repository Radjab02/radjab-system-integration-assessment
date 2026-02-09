package com.ecommerce.mock.soap;

import com.ecommerce.mock.model.DTOs.CustomerRequest;
import com.ecommerce.mock.model.DTOs.CustomerResponse;
import com.ecommerce.mock.service.CustomerService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ws.server.endpoint.annotation.Endpoint;
import org.springframework.ws.server.endpoint.annotation.PayloadRoot;
import org.springframework.ws.server.endpoint.annotation.RequestPayload;
import org.springframework.ws.server.endpoint.annotation.ResponsePayload;
import org.w3c.dom.Document;
import org.w3c.dom.Element;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.time.format.DateTimeFormatter;

@Endpoint
@RequiredArgsConstructor
@Slf4j
public class CustomerSoapEndpoint {

    private static final String NAMESPACE_URI = "http://ecommerce.com/crm/soap";
    private final CustomerService customerService;

    @PayloadRoot(namespace = NAMESPACE_URI, localPart = "AddCustomerRequest")
    @ResponsePayload
    public Element addCustomer(@RequestPayload Element request) throws Exception {
        log.info("SOAP AddCustomer request received");

        // Extract data from SOAP request
        String name = getElementValue(request, "name");
        String email = getElementValue(request, "email");
        String phone = getElementValue(request, "phone");
        String address = getElementValue(request, "address");

        // Create customer using service
        CustomerRequest customerRequest = CustomerRequest.builder()
                .name(name)
                .email(email)
                .phone(phone)
                .address(address)
                .build();

        CustomerResponse customer = customerService.createCustomer(customerRequest);
        log.info("SOAP Customer created: {}", customer.getId());

        // Build SOAP response
        return buildAddCustomerResponse(customer);
    }

    private String getElementValue(Element parent, String tagName) {
        org.w3c.dom.NodeList nodes = parent.getElementsByTagNameNS(NAMESPACE_URI, tagName);
        if (nodes.getLength() > 0) {
            return nodes.item(0).getTextContent();
        }
        return null;
    }

    private Element buildAddCustomerResponse(CustomerResponse customer) throws Exception {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        factory.setNamespaceAware(true);
        DocumentBuilder builder = factory.newDocumentBuilder();
        Document doc = builder.newDocument();

        // Create response element
        Element response = doc.createElementNS(NAMESPACE_URI, "AddCustomerResponse");
        doc.appendChild(response);

        // Create customer element
        Element customerElem = doc.createElementNS(NAMESPACE_URI, "customer");
        response.appendChild(customerElem);

        addElement(doc, customerElem, "id", customer.getId());
        addElement(doc, customerElem, "name", customer.getName());
        addElement(doc, customerElem, "email", customer.getEmail());
        if (customer.getPhone() != null) {
            addElement(doc, customerElem, "phone", customer.getPhone());
        }
        if (customer.getAddress() != null) {
            addElement(doc, customerElem, "address", customer.getAddress());
        }
        addElement(doc, customerElem, "createdDate", 
                customer.getCreatedDate().format(DateTimeFormatter.ISO_DATE_TIME));
        addElement(doc, customerElem, "status", customer.getStatus());

        // Add status and message
        addElement(doc, response, "status", "SUCCESS");
        addElement(doc, response, "message", "Customer created successfully");

        return response;
    }

    private void addElement(Document doc, Element parent, String name, String value) {
        Element element = doc.createElementNS(NAMESPACE_URI, name);
        element.setTextContent(value);
        parent.appendChild(element);
    }
}
