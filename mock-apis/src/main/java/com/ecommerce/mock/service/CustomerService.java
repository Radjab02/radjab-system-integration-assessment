package com.ecommerce.mock.service;

import com.ecommerce.mock.model.Customer;
import com.ecommerce.mock.model.DTOs.CustomerRequest;
import com.ecommerce.mock.model.DTOs.CustomerResponse;
import com.ecommerce.mock.repository.CustomerRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class CustomerService {

    private final CustomerRepository customerRepository;

    @Transactional(readOnly = true)
    public List<CustomerResponse> getAllCustomers(int page, int size) {
        log.debug("Fetching customers - page: {}, size: {}", page, size);
        Page<Customer> customerPage = customerRepository.findAll(PageRequest.of(page, size));
        return customerPage.getContent().stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public long getTotalCustomers() {
        return customerRepository.count();
    }

    @Transactional
    public CustomerResponse createCustomer(CustomerRequest request) {
        log.debug("Creating customer: {}", request.getEmail());
        
        if (customerRepository.existsByEmail(request.getEmail())) {
            throw new IllegalArgumentException("Customer with email " + request.getEmail() + " already exists");
        }

        Customer customer = Customer.builder()
                .id(generateCustomerId())
                .name(request.getName())
                .email(request.getEmail())
                .phone(request.getPhone())
                .address(request.getAddress())
                .status(Customer.CustomerStatus.ACTIVE)
                .build();

        Customer savedCustomer = customerRepository.save(customer);
        log.info("Customer created with ID: {}", savedCustomer.getId());
        
        return mapToResponse(savedCustomer);
    }

    private String generateCustomerId() {
        return "CUST" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
    }

    private CustomerResponse mapToResponse(Customer customer) {
        return CustomerResponse.builder()
                .id(customer.getId())
                .name(customer.getName())
                .email(customer.getEmail())
                .phone(customer.getPhone())
                .address(customer.getAddress())
                .createdDate(customer.getCreatedDate())
                .status(customer.getStatus().name())
                .build();
    }
}
