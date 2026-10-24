// Runs one chat completion through Microsoft.Extensions.AI's OpenTelemetry
// client and exports the span over OTLP/HTTP to scripts/fixtures/otlp_receiver.py
// listening on port 4318. Needs OPENAI_API_KEY.

using Microsoft.Extensions.AI;
using OpenAI;
using OpenTelemetry;
using OpenTelemetry.Exporter;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;

using var tracerProvider = Sdk.CreateTracerProviderBuilder()
    .SetResourceBuilder(ResourceBuilder.CreateDefault().AddService("spanlint-fixtures"))
    .AddSource("Experimental.Microsoft.Extensions.AI")
    .AddOtlpExporter(options =>
    {
        options.Protocol = OtlpExportProtocol.HttpProtobuf;
        options.Endpoint = new Uri("http://127.0.0.1:4318/v1/traces");
    })
    .Build();

var apiKey = Environment.GetEnvironmentVariable("OPENAI_API_KEY")
    ?? throw new InvalidOperationException("OPENAI_API_KEY is not set");

IChatClient client = new OpenAIClient(apiKey)
    .GetChatClient("gpt-4o-mini")
    .AsIChatClient()
    .AsBuilder()
    .UseOpenTelemetry(configure: otel => otel.EnableSensitiveData = true)
    .Build();

await client.GetResponseAsync(
    "Say hi in one word.",
    new ChatOptions { Temperature = 0, MaxOutputTokens = 16 });
