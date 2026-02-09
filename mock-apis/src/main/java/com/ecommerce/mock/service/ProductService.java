package com.ecommerce.mock.service;

import com.ecommerce.mock.model.Product;
import com.ecommerce.mock.model.DTOs.ProductResponse;
import com.ecommerce.mock.repository.ProductRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class ProductService {

    private final ProductRepository productRepository;

    @Transactional(readOnly = true)
    public List<ProductResponse> getAllProducts(int page, int size, Boolean inStock) {
        log.debug("Fetching products - page: {}, size: {}, inStock: {}", page, size, inStock);
        
        if (inStock != null && inStock) {
            // Filter products with stock > 0
            List<Product> products = productRepository.findByStockQuantityGreaterThan(0);
            return products.stream()
                    .skip((long) page * size)
                    .limit(size)
                    .map(this::mapToResponse)
                    .collect(Collectors.toList());
        }
        
        Page<Product> productPage = productRepository.findAll(PageRequest.of(page, size));
        return productPage.getContent().stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public long getTotalProducts() {
        return productRepository.count();
    }

    private ProductResponse mapToResponse(Product product) {
        return ProductResponse.builder()
                .id(product.getId())
                .productName(product.getProductName())
                .sku(product.getSku())
                .stockQuantity(product.getStockQuantity())
                .price(product.getPrice())
                .category(product.getCategory())
                .lastUpdated(product.getLastUpdated())
                .build();
    }
}
