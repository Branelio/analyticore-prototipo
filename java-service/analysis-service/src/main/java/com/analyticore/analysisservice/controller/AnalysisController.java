package com.analyticore.analysisservice.controller;

import com.analyticore.analysisservice.service.AnalysisService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;
import java.util.UUID;

@RestController
public class AnalysisController {

    @Autowired
    private AnalysisService analysisService;

    @PostMapping("/analyze")
    public ResponseEntity<String> analyzeJob(@RequestBody Map<String, UUID> body) {
        UUID jobId = body.get("jobId");
        if (jobId == null) {
            return ResponseEntity.badRequest().body("Job ID is required.");
        }

        // Inicia el análisis en un hilo separado. Esto es una simplificación para no bloquear el hilo de la API.
        // En un entorno de producción, se usaría un sistema de colas de mensajes (como RabbitMQ) para esto.
        new Thread(() -> analysisService.analyzeText(jobId)).start();

        return ResponseEntity.ok("Analysis started for job: " + jobId);
    }
}