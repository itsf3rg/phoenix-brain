package com.gigboss.service

import android.accessibilityservice.AccessibilityService
import android.graphics.Bitmap
import android.hardware.HardwareBuffer
import android.util.Log
import android.view.Display
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import com.gigboss.network.BrainClient
import com.gigboss.ocr.OCRProcessor
import kotlinx.coroutines.*
import java.util.concurrent.Executor

class RideAccessibilityService : AccessibilityService() {

    private val UBER_PACKAGE = "com.ubercab.driver"
    private val LYFT_PACKAGE = "com.lyft.android.driver"
    private var lastScanTime = 0L
    private var latestEventSource: AccessibilityNodeInfo? = null
    
    // Project Phoenix Rising: Hybrid Polling Coroutine Scope
    private val serviceJob = Job()
    private val serviceScope = CoroutineScope(Dispatchers.Main + serviceJob)
    private var activePollJob: Job? = null

    override fun onServiceConnected() {
        super.onServiceConnected()
        Log.d("GigBoss", "Accessibility Service Connected. Project Phoenix Native Scanner Armed.")
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event == null) return

        val pkg = event.packageName?.toString() ?: ""
        
        // Immediate Trigger: Capture the full active window tree.
        val rootNode = rootInActiveWindow

        if (pkg == LYFT_PACKAGE && rootNode != null) {
             val currentTime = System.currentTimeMillis()
             if (currentTime - lastScanTime > 1500) {
                 lastScanTime = currentTime
                 performNativeScan("lyft", rootNode)
             }
        } 
        // Project Phoenix: Trigger on Uber or decoupled System UI overlays
        else if (pkg == UBER_PACKAGE || pkg == "com.android.systemui" || pkg == "android") {
             event.source?.let { latestEventSource = it }
             startHybridPolling("uber")
        }
    }

    private fun startHybridPolling(platform: String) {
        // Debounce: Do not take overlapping screenshots
        if (activePollJob?.isActive == true) return
        
        activePollJob = serviceScope.launch {
             Log.d("GigBoss", "Initiating OCR Screenshot Grab for $platform")
             
             // Minor delay to ensure the UI animation has settled before snapping
             delay(400)
             
             takeScreenshot(Display.DEFAULT_DISPLAY, Executor { command -> command.run() }, object : TakeScreenshotCallback {
                 override fun onSuccess(screenshot: ScreenshotResult) {
                     val hardwareBuffer = screenshot.hardwareBuffer
                     val colorSpace = screenshot.colorSpace
                     val bitmap = Bitmap.wrapHardwareBuffer(hardwareBuffer, colorSpace)
                     
                     if (bitmap != null) {
                         serviceScope.launch {
                             val squashedPayload = OCRProcessor.processImageToSquashedString(bitmap)
                             
                             Log.d("GigBoss", "OCR RESULT DUMP: $squashedPayload")
                             
                             if (squashedPayload.contains("$") || squashedPayload.contains("min", ignoreCase = true) || squashedPayload.contains("mi", ignoreCase = true)) {
                                 Log.d("GigBoss", "OCR SIGNATURE DETECTED. Dispatching payload.")
                                 BrainClient.sendPayload(squashedPayload, platform)
                             }
                             
                             bitmap.recycle() // Prevent Memory Leaks
                         }
                     }
                     hardwareBuffer.close()
                 }

                 override fun onFailure(errorCode: Int) {
                     Log.e("GigBoss", "Screenshot Capture Failed with code: $errorCode")
                 }
             })
        }
    }

    private fun performNativeScan(platform: String, node: AccessibilityNodeInfo): String {
        return "NATIVE SCAN DEPRECATED"
    }

    override fun onDestroy() {
        super.onDestroy()
        serviceJob.cancel()
    }

    override fun onInterrupt() {}
}
