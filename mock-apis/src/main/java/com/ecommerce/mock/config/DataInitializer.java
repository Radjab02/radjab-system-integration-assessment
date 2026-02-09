package com.ecommerce.mock.config;

import com.ecommerce.mock.model.Customer;
import com.ecommerce.mock.model.Product;
import com.ecommerce.mock.repository.CustomerRepository;
import com.ecommerce.mock.repository.ProductRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;

@Component
@RequiredArgsConstructor
@Slf4j
public class DataInitializer implements CommandLineRunner {

    private final CustomerRepository customerRepository;
    private final ProductRepository productRepository;

    @Override
    public void run(String... args) {
        log.info("Initializing sample data...");
        initializeCustomers();
        initializeProducts();
        log.info("Sample data initialization complete");
    }

    private void initializeCustomers() {
        List<Customer> customers = Arrays.asList(
                Customer.builder()
                        .id("CUST001")
                        .name("John Doe")
                        .email("john.doe@example.com")
                        .phone("+1234567890")
                        .address("123 Main St, New York, NY 10001")
                        .createdDate(LocalDateTime.of(2024, 1, 15, 10, 30))
                        .status(Customer.CustomerStatus.ACTIVE)
                        .build(),

                Customer.builder()
                        .id("CUST002")
                        .name("Jane Smith")
                        .email("jane.smith@example.com")
                        .phone("+1987654321")
                        .address("456 Oak Ave, Los Angeles, CA 90001")
                        .createdDate(LocalDateTime.of(2024, 2, 1, 14, 20))
                        .status(Customer.CustomerStatus.ACTIVE)
                        .build(),

                Customer.builder()
                        .id("CUST003")
                        .name("Robert Johnson")
                        .email("robert.j@example.com")
                        .phone("+1555666777")
                        .address("789 Pine Rd, Chicago, IL 60601")
                        .createdDate(LocalDateTime.of(2024, 1, 20, 9, 15))
                        .status(Customer.CustomerStatus.ACTIVE)
                        .build(),

                Customer.builder()
                        .id("CUST004")
                        .name("Emily Brown")
                        .email("emily.brown@example.com")
                        .phone("+1444555666")
                        .address("321 Elm St, Houston, TX 77001")
                        .createdDate(LocalDateTime.of(2024, 2, 5, 11, 45))
                        .status(Customer.CustomerStatus.INACTIVE)
                        .build(),

                Customer.builder()
                        .id("CUST005")
                        .name("Michael Wilson")
                        .email("m.wilson@example.com")
                        .phone("+1777888999")
                        .address("555 Maple Dr, Phoenix, AZ 85001")
                        .createdDate(LocalDateTime.of(2024, 1, 10, 16, 30))
                        .status(Customer.CustomerStatus.ACTIVE)
                        .build()
        );

        customerRepository.saveAll(customers);
        log.info("Initialized {} customers", customers.size());
    }

    private void initializeProducts() {
        List<Product> products = Arrays.asList(
                Product.builder()
                        .id("PROD001")
                        .productName("Laptop Pro 15")
                        .sku("LPT-PRO-15-BLK")
                        .stockQuantity(45)
                        .price(new BigDecimal("1299.99"))
                        .category("Electronics")
                        .lastUpdated(LocalDateTime.of(2024, 2, 5, 9, 15))
                        .build(),

                Product.builder()
                        .id("PROD002")
                        .productName("Wireless Mouse")
                        .sku("MSE-WRL-BLU")
                        .stockQuantity(150)
                        .price(new BigDecimal("29.99"))
                        .category("Accessories")
                        .lastUpdated(LocalDateTime.of(2024, 2, 6, 11, 30))
                        .build(),

                Product.builder()
                        .id("PROD003")
                        .productName("USB-C Cable 2m")
                        .sku("CBL-USBC-2M")
                        .stockQuantity(0)
                        .price(new BigDecimal("15.99"))
                        .category("Accessories")
                        .lastUpdated(LocalDateTime.of(2024, 2, 4, 16, 45))
                        .build(),

                Product.builder()
                        .id("PROD004")
                        .productName("Mechanical Keyboard RGB")
                        .sku("KBD-MECH-RGB")
                        .stockQuantity(78)
                        .price(new BigDecimal("149.99"))
                        .category("Accessories")
                        .lastUpdated(LocalDateTime.of(2024, 2, 7, 8, 20))
                        .build(),

                Product.builder()
                        .id("PROD005")
                        .productName("27-inch Monitor 4K")
                        .sku("MON-27-4K")
                        .stockQuantity(23)
                        .price(new BigDecimal("599.99"))
                        .category("Electronics")
                        .lastUpdated(LocalDateTime.of(2024, 2, 6, 14, 10))
                        .build(),

                Product.builder()
                        .id("PROD006")
                        .productName("Webcam HD 1080p")
                        .sku("WCM-HD-1080")
                        .stockQuantity(0)
                        .price(new BigDecimal("89.99"))
                        .category("Electronics")
                        .lastUpdated(LocalDateTime.of(2024, 2, 3, 10, 0))
                        .build(),

                Product.builder()
                        .id("PROD007")
                        .productName("Headset Wireless")
                        .sku("HDS-WRL-BLK")
                        .stockQuantity(112)
                        .price(new BigDecimal("129.99"))
                        .category("Audio")
                        .lastUpdated(LocalDateTime.of(2024, 2, 7, 7, 45))
                        .build()
        );

        productRepository.saveAll(products);
        log.info("Initialized {} products", products.size());
    }
}
