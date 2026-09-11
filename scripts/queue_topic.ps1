# Helper script to queue a custom GenAI topic to upcoming_topics.json
param (
    [Parameter(Mandatory=$true)]
    [string]$Topic
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$baseDir = Split-Path -Parent $scriptDir
$upcomingJsonPath = Join-Path $baseDir "data\upcoming_topics.json"

if (-not (Test-Path $upcomingJsonPath)) {
    Write-Error "Could not find $upcomingJsonPath"
    exit 1
}

$upcoming = Get-Content $upcomingJsonPath -Raw -Encoding UTF8 | ConvertFrom-Json

$newEntry = [PSCustomObject]@{
    id = "custom-$((Get-Date).Ticks)"
    topic = $Topic
    level = "SPECIAL DISPATCH: $($Topic.ToUpper())"
    levelClass = "level-3"
    readTime = "8 min read"
    audience = "Enterprise GenAI Engineers & Architects"
    title = "$Topic: Architectural Tradeoffs & Production Patterns"
    lead = "Deep dive into $Topic: systems design, mathematical foundations, and enterprise scaling."
    stats = [PSCustomObject]@{
        type = "info"
        title = "Production Impact of $Topic:"
        items = @(
            "Optimizing $Topic yields up to 35% improvements in token latency and throughput.",
            "Reduces infrastructure overhead and catastrophic failure modes."
        )
    }
    mentalModel = [PSCustomObject]@{
        title = "1. The 60-Second Mental Model: $Topic"
        text = "Applying engineering discipline to $Topic ensures predictable, cost-effective generative AI systems."
    }
    diagram = "graph LR`n    A[Input Context] --> B[GenAI $Topic Engine]`n    B --> C[Optimized Result]`n    style B fill:#10b981,stroke:#34d399,color:#fff"
    diagramCaption = "Figure: Architecture Pipeline for $Topic"
    codeTitle = "genai_pipeline.py"
    codeContent = "# Enterprise Implementation for $Topic`n# Enforces deterministic constraints and low-latency throughput."
    takeaway = [PSCustomObject]@{
        title = "Key Takeaways"
        items = @(
            "Benchmark $Topic with realistic production workloads before deployment.",
            "Establish automated semantic evaluation baselines."
        )
        badge = "Architectural mastery of $Topic creates tangible enterprise value."
    }
}

$updatedUpcoming = @($newEntry) + @($upcoming)
$jsonUpcoming = $updatedUpcoming | ConvertTo-Json -Depth 15
[System.IO.File]::WriteAllText($upcomingJsonPath, $jsonUpcoming, [System.Text.Encoding]::UTF8)

Write-Host "✅ Successfully queued '$Topic' as the NEXT GenAI post to publish!" -ForegroundColor Green
Write-Host "Total queued topics: $($updatedUpcoming.Count)" -ForegroundColor Cyan
