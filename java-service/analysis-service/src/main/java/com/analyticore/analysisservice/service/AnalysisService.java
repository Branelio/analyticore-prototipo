package com.analyticore.analysisservice.service;

import com.analyticore.analysisservice.domain.Job;
import com.analyticore.analysisservice.domain.JobStatus;
import com.analyticore.analysisservice.domain.Sentiment;
import com.analyticore.analysisservice.repository.JobRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
public class AnalysisService {

    @Autowired
    private JobRepository jobRepository;

    public void analyzeText(UUID jobId) {
        // Usa `findById` para obtener el trabajo. Maneja el caso si no existe.
        jobRepository.findById(jobId).ifPresent(job -> {
            try {
                // 1. Actualiza el estado a "PROCESSING"
                job.setStatus(JobStatus.PROCESSING);
                jobRepository.save(job);

                // 2. Lógica de análisis (prototipo simple)
                String text = job.getTextToAnalyze().toLowerCase();
                String[] words = text.split("[\\s.,?!;:]+"); // Divide por espacios y puntuación

                // Análisis de Sentimiento
                long positiveCount = Arrays.stream(words).filter(w -> w.contains("bueno") || w.contains("excelente") || w.contains("fantastico")).count();
                long negativeCount = Arrays.stream(words).filter(w -> w.contains("malo") || w.contains("pesimo") || w.contains("horrible")).count();

                Sentiment sentiment = Sentiment.NEUTRAL;
                if (positiveCount > negativeCount) {
                    sentiment = Sentiment.POSITIVE;
                } else if (negativeCount > positiveCount) {
                    sentiment = Sentiment.NEGATIVE;
                }
                job.setSentiment(sentiment);

                // Extracción de Palabras Clave
                Set<String> stopWords = new HashSet<>(Arrays.asList("el", "la", "los", "las", "un", "una", "unos", "unas", "de", "y", "a", "en", "para", "es", "con", "que", "por"));
                String[] topKeywords = Arrays.stream(words)
                    .filter(w -> !stopWords.contains(w) && w.length() > 2) // Filtra stop words y palabras cortas
                    .collect(Collectors.groupingBy(w -> w, Collectors.counting())) // Cuenta la frecuencia de cada palabra
                    .entrySet().stream()
                    .sorted((e1, e2) -> e2.getValue().compareTo(e1.getValue())) // Ordena por frecuencia
                    .limit(5) // Toma las 5 más frecuentes
                    .map(java.util.Map.Entry::getKey)
                    .toArray(String[]::new);
                job.setKeywords(topKeywords);

                // 3. Actualiza el estado a "COMPLETED" y guarda los resultados
                job.setStatus(JobStatus.COMPLETED);
                jobRepository.save(job);
            } catch (Exception e) {
                // Si ocurre un error, actualiza el estado a "ERROR"
                job.setStatus(JobStatus.ERROR);
                jobRepository.save(job);
                System.err.println("Error analyzing job " + jobId + ": " + e.getMessage());
            }
        });
    }
}