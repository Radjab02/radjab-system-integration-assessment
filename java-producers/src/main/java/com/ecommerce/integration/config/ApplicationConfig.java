package com.ecommerce.integration.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.retry.annotation.EnableRetry;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * Configuration for Spring Retry and Scheduling
 */
@Configuration
@EnableRetry
@EnableScheduling
public class ApplicationConfig {
}
