package com.ecommerce.integration.service;

import com.ecommerce.integration.client.MockApiClient;
import com.ecommerce.integration.model.Product;
import com.ecommerce.integration.producer.InventoryProducerService;
import com.ecommerce.integration.repository.SyncStateRepository;
import com.ecommerce.integration.service.KafkaProducerService;
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
class InventoryProducerServiceTest {

    @Mock
    private MockApiClient apiClient;

    @Mock
    private KafkaProducerService kafkaProducerService;

    @Mock
    private SyncStateRepository syncStateRepository;

    @InjectMocks
    private InventoryProducerService service;

    private List<Product> products;

    @BeforeEach
    void setup() {
        products = List.of(
                Product.builder().id("1").productName("Item1").build(),
                Product.builder().id("2").productName("Item2").build()
        );
    }

    // ---------- FULL SYNC ----------

    @Test
    void fullSync_success() {
        when(apiClient.fetchAllProducts()).thenReturn(products);

        service.performFullSync();

        verify(kafkaProducerService).sendInventoryData(eq(products), eq("INITIAL_FULL"), eq(true), eq(2));
        verify(syncStateRepository).updateLastSyncTime(eq("PRODUCT"), any(), eq(2L));
    }

    @Test
    void fullSync_empty_noPublish_noStateUpdate() {
        when(apiClient.fetchAllProducts()).thenReturn(List.of());

        service.performFullSync();

        verify(kafkaProducerService, never()).sendInventoryData(any(), any(), anyBoolean(), anyInt());
        verify(syncStateRepository, never()).updateLastSyncTime(any(), any(), anyLong());
    }

    @Test
    void fullSync_apiFailure() {
        when(apiClient.fetchAllProducts()).thenThrow(new RuntimeException("API error"));

        assertThrows(RuntimeException.class, () -> service.performFullSync());
    }

    // ---------- INCREMENTAL ----------

    @Test
    void incremental_success() {
        when(syncStateRepository.getLastSyncTime("PRODUCT"))
                .thenReturn(Optional.of(LocalDateTime.now().minusMinutes(5)));
        when(apiClient.fetchProductsSince(any())).thenReturn(products);

        service.performIncrementalSync();

        verify(kafkaProducerService).sendInventoryData(eq(products), eq("INCREMENTAL"), eq(false), eq(2));
        verify(syncStateRepository).updateLastSyncTime(eq("PRODUCT"), any(), eq(2L));
    }

    @Test
    void incremental_empty_updatesStateOnly() {
        when(syncStateRepository.getLastSyncTime("PRODUCT"))
                .thenReturn(Optional.of(LocalDateTime.now().minusMinutes(5)));
        when(apiClient.fetchProductsSince(any())).thenReturn(List.of());

        service.performIncrementalSync();

        verify(kafkaProducerService, never()).sendInventoryData(any(), any(), anyBoolean(), anyInt());
        verify(syncStateRepository).updateLastSyncTime(eq("PRODUCT"), any(), eq(0L));
    }

    // ---------- LARGE BATCH ----------

    @Test
    void fullSync_largeBatch_success() {
        List<Product> large = new ArrayList<>();
        for (int i = 0; i < 100; i++) {
            large.add(Product.builder().id(String.valueOf(i)).productName("P" + i).build());
        }

        when(apiClient.fetchAllProducts()).thenReturn(large);

        service.performFullSync();

        verify(kafkaProducerService).sendInventoryData(eq(large), eq("INITIAL_FULL"), eq(true), eq(100));
        verify(syncStateRepository).updateLastSyncTime(eq("PRODUCT"), any(), eq(100L));
    }
}
