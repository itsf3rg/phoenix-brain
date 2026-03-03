package com.gigboss.network

import android.util.Log
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException

object BrainClient {
    private val client = OkHttpClient()
    private var baseUrl = "http://192.168.0.52:8000"

    fun updateServerUrl(ip: String) {
        baseUrl = "http://$ip:8000"
        Log.d("GigBoss", "Brain Client URL updated to $baseUrl")
    }

    fun sendPayload(rawText: String, platform: String) {
        val json = JSONObject()
        json.put("raw_text", rawText)
        json.put("platform", platform)

        val requestBody = json.toString().toRequestBody("application/json".toMediaTypeOrNull())

        val request = Request.Builder()
            .url("$baseUrl/parse_and_evaluate")
            .post(requestBody)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                Log.e("GigBoss", "Failed to connect to Brain AI: ${e.message}")
            }

            override fun onResponse(call: Call, response: Response) {
                if (!response.isSuccessful) {
                    Log.e("GigBoss", "Brain rejected payload: ${response.code}")
                } else {
                    Log.d("GigBoss", "Offer payload successfully evaluated by Brain.")
                }
                response.close()
            }
        })
    }
}
