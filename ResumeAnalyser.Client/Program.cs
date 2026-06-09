using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using ResumeAnalyser.Client;
using ResumeAnalyser.Client.Services;

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

builder.Services.AddScoped(sp => new HttpClient { BaseAddress = new Uri(builder.HostEnvironment.BaseAddress) });

builder.Services.AddScoped(sp =>
{
    var http = sp.GetRequiredService<HttpClient>();
    var service = new ResumeService(http);
    var baseUri = new Uri(builder.HostEnvironment.BaseAddress);
    if (baseUri.Host == "localhost" || baseUri.Host == "127.0.0.1")
    {
        service.BaseUrl = "http://localhost:8000";
    }
    else
    {
        service.BaseUrl = "https://resumecheck-gy75.onrender.com";
    }
    return service;
});

await builder.Build().RunAsync();
