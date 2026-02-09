package com.ecommerce.integration.client;

import com.ecommerce.integration.model.ApiResponse;
import com.ecommerce.integration.model.Customer;
import com.ecommerce.integration.model.Product;
import com.fasterxml.jackson.databind.ObjectMapper;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.MediaType;

import java.time.LocalDateTime;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

class MockApiClientTest {

    private MockWebServer server;
    private MockApiClient client;
    private ObjectMapper mapper = new ObjectMapper().findAndRegisterModules();

    private static final String BASE_URL = "http://localhost:8080";
    private static final String CUSTOMERS_ENDPOINT = "/customers";
    private static final String PRODUCTS_ENDPOINT = "/products";

    @BeforeEach
    void setup() throws Exception {
        server = new MockWebServer();
        server.start();

        String baseUrl = server.url("/").toString();

        client = new MockApiClient(baseUrl, 1000);
        // Inject endpoints manually (since @Value not active in plain test)
        TestUtils.setField(client, "customersEndpoint", "/customers");
        TestUtils.setField(client, "productsEndpoint", "/products");
    }

    @AfterEach
    void tearDown() throws Exception {
        server.shutdown();
    }


    // --------------------------------------------------
    // FULL SYNC - CUSTOMERS (pagination)
    // --------------------------------------------------

    @Test
    void fetchAllCustomers_multiplePages_success() throws Exception {

        ApiResponse.CustomerPage page1 = ApiResponse.CustomerPage.builder()
                .data(List.of(customer("1"), customer("2")))
                .total(200)
                .build();

        ApiResponse.CustomerPage page2 = ApiResponse.CustomerPage.builder()
                .data(List.of(customer("3"), customer("4")))
                .total(200)
                .build();

        server.enqueue(new MockResponse()
                .setBody(mapper.writeValueAsString(page1))
                .addHeader("Content-Type", "application/json"));

        server.enqueue(new MockResponse()
                .setBody(mapper.writeValueAsString(page2))
                .addHeader("Content-Type", "application/json"));

        List<Customer> result = client.fetchAllCustomers();

        assertThat(result).hasSize(4);
    }

    @Test
    void fetchAllCustomers_emptyResponse() throws Exception {
        ApiResponse.CustomerPage page = ApiResponse.CustomerPage.builder()
                .data(List.of())
                .total(0)
                .build();

        server.enqueue(new MockResponse()
                .setBody(mapper.writeValueAsString(page))
                .addHeader("Content-Type", "application/json"));

        List<Customer> result = client.fetchAllCustomers();

        assertThat(result).isEmpty();
    }

    // --------------------------------------------------
    // INCREMENTAL - CUSTOMERS (filtering)
    // --------------------------------------------------

    @Test
    void fetchCustomersSince_filtersCorrectly() throws Exception {
        LocalDateTime since = LocalDateTime.now().minusDays(1);

        Customer oldC = customer("1");
        oldC.setCreatedDate(LocalDateTime.now().minusDays(2));

        Customer newC = customer("2");
        newC.setCreatedDate(LocalDateTime.now());

        ApiResponse.CustomerPage page = ApiResponse.CustomerPage.builder()
                .data(List.of(oldC, newC))
                .total(2)
                .build();

        server.enqueue(new MockResponse()
                .setBody(mapper.writeValueAsString(page))
                .addHeader("Content-Type", "application/json"));

        List<Customer> result = client.fetchCustomersSince(since);

        assertThat(result).hasSize(1);
    }

    // --------------------------------------------------
    // FULL SYNC - PRODUCTS
    // --------------------------------------------------

    @Test
    void fetchAllProducts_multiplePages_success() throws Exception {
        ApiResponse.ProductPage page1 = ApiResponse.ProductPage.builder()
                .data(List.of(product("1"), product("2")))
                .total(200)
                .build();

        ApiResponse.ProductPage page2 = ApiResponse.ProductPage.builder()
                .data(List.of(product("3"), product("4")))
                .total(200)
                .build();

        server.enqueue(new MockResponse()
                .setBody(mapper.writeValueAsString(page1))
                .addHeader("Content-Type", "application/json"));

        server.enqueue(new MockResponse()
                .setBody(mapper.writeValueAsString(page2))
                .addHeader("Content-Type", "application/json"));

        List<Product> result = client.fetchAllProducts();

        assertThat(result).hasSize(4);
    }

    // --------------------------------------------------
    // INCREMENTAL - PRODUCTS (filter)
    // --------------------------------------------------

    @Test
    void fetchProductsSince_filtersCorrectly() throws Exception {
        LocalDateTime since = LocalDateTime.now().minusDays(1);

        Product oldP = product("1");
        oldP.setLastUpdated(LocalDateTime.now().minusDays(2));

        Product newP = product("2");
        newP.setLastUpdated(LocalDateTime.now());

        ApiResponse.ProductPage page = ApiResponse.ProductPage.builder()
                .data(List.of(oldP, newP))
                .total(2)
                .build();

        server.enqueue(new MockResponse()
                .setBody(mapper.writeValueAsString(page))
                .addHeader("Content-Type", "application/json"));

        List<Product> result = client.fetchProductsSince(since);

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getId()).isEqualTo("2");
    }

    // --------------------------------------------------
    // ERROR HANDLING
    // --------------------------------------------------

    @Test
    void fetchAllCustomers_httpError_throws() {
        server.enqueue(new MockResponse().setResponseCode(500));

        assertThatThrownBy(() -> client.fetchAllCustomers())
                .isInstanceOf(Exception.class);
    }

    @Test
    void fetchAllProducts_httpError_throws() {
        server.enqueue(new MockResponse().setResponseCode(500));

        assertThatThrownBy(() -> client.fetchAllProducts())
                .isInstanceOf(Exception.class);
    }

    // --------------------------------------------------
    // Helpers
    // --------------------------------------------------

    private Customer customer(String id) {
        return Customer.builder()
                .id(id)
                .name("Customer " + id)
                .createdDate(LocalDateTime.now())
                .build();
    }

    private Product product(String id) {
        return Product.builder()
                .id(id)
                .productName("Product " + id)
                .lastUpdated(LocalDateTime.now())
                .build();
    }
}
