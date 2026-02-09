package com.ecommerce.integration.service;

import com.ecommerce.integration.client.MockApiClient;
import com.ecommerce.integration.model.Customer;
import com.ecommerce.integration.producer.CustomerProducerService;
import com.ecommerce.integration.repository.SyncStateRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class CustomerProducerServiceTest {

    @Mock
    private MockApiClient mockApiClient;

    @Mock
    private KafkaProducerService kafkaProducerService;

    @Mock
    private SyncStateRepository syncStateRepository;

    @InjectMocks
    private CustomerProducerService service;

    private List<Customer> customers;

    @BeforeEach
    void setup() {
        customers = List.of(
                Customer.builder().id("1").name("John").email("a@a.com").build(),
                Customer.builder().id("2").name("Jane").email("b@b.com").build()
        );
    }

    // ---------- FULL SYNC ----------

    @Test
    void fullSync_success() {
        when(mockApiClient.fetchAllCustomers()).thenReturn(customers);

        service.performFullSync();

        verify(kafkaProducerService).sendCustomerData(eq(customers), eq("INITIAL_FULL"), eq(true), eq(2));
        verify(syncStateRepository).updateLastSyncTime(eq("CUSTOMER"), any(), eq(2L));
    }

    @Test
    void fullSync_emptyList_noPublish_noStateUpdate() {
        when(mockApiClient.fetchAllCustomers()).thenReturn(List.of());

        service.performFullSync();

        verify(kafkaProducerService, never()).sendCustomerData(any(), any(), anyBoolean(), anyInt());
        verify(syncStateRepository, never()).updateLastSyncTime(any(), any(), anyLong());
    }

    @Test
    void fullSync_apiFailure() {
        when(mockApiClient.fetchAllCustomers()).thenThrow(new RuntimeException("API error"));

        assertThrows(RuntimeException.class, () -> service.performFullSync());

        verify(kafkaProducerService, never()).sendCustomerData(any(), any(), anyBoolean(), anyInt());
    }

    // ---------- INCREMENTAL SYNC ----------

    @Test
    void incrementalSync_success() {
        when(syncStateRepository.getLastSyncTime("CUSTOMER"))
                .thenReturn(Optional.of(LocalDateTime.now().minusMinutes(5)));
        when(mockApiClient.fetchCustomersSince(any())).thenReturn(customers);

        service.performIncrementalSync();

        verify(kafkaProducerService).sendCustomerData(eq(customers), eq("INCREMENTAL"), eq(false), eq(2));
        verify(syncStateRepository).updateLastSyncTime(eq("CUSTOMER"), any(), eq(2L));
    }

    @Test
    void incrementalSync_noNewCustomers_updatesStateOnly() {
        when(syncStateRepository.getLastSyncTime("CUSTOMER"))
                .thenReturn(Optional.of(LocalDateTime.now().minusMinutes(5)));
        when(mockApiClient.fetchCustomersSince(any())).thenReturn(List.of());

        service.performIncrementalSync();

        verify(kafkaProducerService, never()).sendCustomerData(any(), any(), anyBoolean(), anyInt());
        verify(syncStateRepository).updateLastSyncTime(eq("CUSTOMER"), any(), eq(0L));
    }

    // ---------- LARGE BATCH ----------

    @Test
    void fullSync_largeBatch_success() {
        List<Customer> large = new ArrayList<>();
        for (int i = 0; i < 100; i++) {
            large.add(Customer.builder().id(String.valueOf(i)).name("C" + i).build());
        }

        when(mockApiClient.fetchAllCustomers()).thenReturn(large);

        service.performFullSync();

        verify(kafkaProducerService).sendCustomerData(eq(large), eq("INITIAL_FULL"), eq(true), eq(100));
        verify(syncStateRepository).updateLastSyncTime(eq("CUSTOMER"), any(), eq(100L));
    }
}
