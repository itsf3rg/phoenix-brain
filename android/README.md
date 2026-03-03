# GigBoss Android Mobile Integration (App Store Prep)

This directory is reserved for the foundational Android application (React Native or Kotlin Native) responsible for the Spectral Scanning and Accessibility Service.

## Architecture Guidelines (Based on FareFetch V7 Insights)
Because Uber heavily obfuscates the pricing data (e.g., "Ghost Windows"), the mobile component MUST implement a robust `AccessibilityService` capable of:
1. Identifying when a Ride Request arrives via structural patterns (e.g., `id/glide_container` or notification intent), ignoring "brand strings" that may be intentionally missing.
2. Iterating through `accessibilityService.windows` rather than relying solely on the active `com.ubercab.driver` window for extraction.
3. Establishing a dual-channel telemetry connection:
   - Primary: Forwarding extracted OCR Strings to the Python Backend (`/parse_and_evaluate`) via REST HTTP methods.
   - Secondary: Logging network heartbeats periodically to ensure connectivity is active.

### Next Steps for Native Development:
- Base project via React Native (Expo) or Android Studio (Kotlin).
- Scaffold the `RideAccessibilityService` module.
- Implements `OkHttp3` to reliably send captured node trees to `http://127.0.0.1:8000/parse_and_evaluate`.
