package com.gigboss

import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.gigboss.network.BrainClient

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val ipInput = findViewById<EditText>(R.id.ipAddressInput)
        val saveButton = findViewById<Button>(R.id.saveIpButton)
        val enableServiceButton = findViewById<Button>(R.id.enableServiceButton)
        
        // Load saved IP
        val sharedPrefs = getSharedPreferences("GigBossPrefs", MODE_PRIVATE)
        val savedIp = sharedPrefs.getString("brain_ip", "192.168.0.52")
        ipInput.setText(savedIp)
        BrainClient.updateServerUrl(savedIp!!)

        saveButton.setOnClickListener {
            val ip = ipInput.text.toString()
            sharedPrefs.edit().putString("brain_ip", ip).apply()
            BrainClient.updateServerUrl(ip)
            Toast.makeText(this, "Brain IP Saved & Updated", Toast.LENGTH_SHORT).show()
        }

        enableServiceButton.setOnClickListener {
            // Direct intent to Accessibility Settings to reduce friction
            val intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
            val componentName = "$packageName/com.gigboss.service.RideAccessibilityService"
            intent.putExtra(":settings:fragment_args_key", componentName)
            startActivity(intent)
        }
    }
}
