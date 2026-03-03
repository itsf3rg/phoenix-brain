package com.gigboss.ocr

import android.graphics.Bitmap
import android.util.Log
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import kotlinx.coroutines.tasks.await

object OCRProcessor {
    private const val TAG = "OCRProcessor"
    
    // Initialize the ML Kit Latin text recognizer
    private val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)

    /**
     * Processes an Android Bitmap screenshot using Google ML Kit.
     * Returns a "squashed" String containing all recognized text blocks, 
     * separated by spaces, matching the format of the old 'collectTextFlat'
     * native parser, ensuring downstream Python regex compatibility.
     */
    suspend fun processImageToSquashedString(bitmap: Bitmap): String {
        return try {
            val image = InputImage.fromBitmap(bitmap, 0)
            val result = recognizer.process(image).await()
            
            val sb = StringBuilder()
            
            for (block in result.textBlocks) {
                // Remove line breaks to create a continuous data stream
                val cleanBlock = block.text.replace("\n", " ").trim()
                sb.append(cleanBlock).append(" ")
            }
            
            val squashed = sb.toString().trim()
            Log.d(TAG, "OCR Squashed Dump: $squashed")
            squashed
            
        } catch (e: Exception) {
            Log.e(TAG, "OCR Processing failed: ${e.message}")
            ""
        }
    }
}
