using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Components.Forms;
using ResumeAnalyser.Client.Models;

namespace ResumeAnalyser.Client.Services
{
    public class ResumeService
    {
        private readonly HttpClient _http;
        
        // Default to localhost for local testing, can be set dynamically
        public string BaseUrl { get; set; } = "http://localhost:8000";

        // Stores the last analysis result for dashboard rendering
        public AnalysisResult? LastResult { get; set; }

        public ResumeService(HttpClient http)
        {
            _http = http;
        }

        public async Task<AnalysisResult> AnalyseAsync(IBrowserFile file, string jobDescription)
        {
            using var content = new MultipartFormDataContent();
            
            // Allow up to 5MB file size
            var fileStream = file.OpenReadStream(maxAllowedSize: 5 * 1024 * 1024);
            var fileContent = new StreamContent(fileStream);
            
            // Determine content type
            var contentType = string.IsNullOrEmpty(file.ContentType) ? "application/octet-stream" : file.ContentType;
            fileContent.Headers.ContentType = new MediaTypeHeaderValue(contentType);
            
            content.Add(fileContent, "resume", file.Name);
            content.Add(new StringContent(jobDescription), "job_description");

            var response = await _http.PostAsync($"{BaseUrl}/api/analyse", content);
            
            if (!response.IsSuccessStatusCode)
            {
                var errorMsg = await response.Content.ReadAsStringAsync();
                throw new HttpRequestException($"API Error ({response.StatusCode}): {errorMsg}");
            }
            
            var result = await response.Content.ReadFromJsonAsync<AnalysisResult>();
            return result ?? throw new InvalidOperationException("API returned empty analysis result.");
        }

        public async Task<byte[]> DownloadReportAsync(AnalysisResult result)
        {
            var response = await _http.PostAsJsonAsync($"{BaseUrl}/api/report", result);
            
            if (!response.IsSuccessStatusCode)
            {
                var errorMsg = await response.Content.ReadAsStringAsync();
                throw new HttpRequestException($"API Error ({response.StatusCode}): {errorMsg}");
            }
            
            return await response.Content.ReadAsByteArrayAsync();
        }
    }
}
