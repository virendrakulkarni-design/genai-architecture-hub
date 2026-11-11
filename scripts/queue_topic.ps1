# Helper script to queue a custom GenAI topic/keyword to upcoming_topics.json
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
    audience = "Enterprise GenAI Systems Engineers & Architects"
    title = "$Topic: Architecture, Latency Budgets & Enterprise Systems Design"
    lead = "Deep dive into $Topic: systems architecture, mathematical trade-offs, and production engineering realities."
    stats = [PSCustomObject]@{
        type = "info"
        title = "Systems Impact of $Topic:"
        items = @(
            "Adopting structured patterns for $Topic mitigates runtime bottlenecks by over 35%.",
            "Improves system observability and inference stability across distributed GPU clusters."
        )
    }
    mentalModel = [PSCustomObject]@{
        title = "1. The 60-Second Mental Model: $Topic"
        text = "Applying systems engineering rigor to $Topic ensures predictable, observable, and resilient GenAI infrastructure deployments."
    }
    diagram = "graph LR`n    Input[Input Tensor Stream] --> Engine[GenAI $Topic Kernel]`n    Engine --> Output[Optimized Representation]`n    style Engine fill:#10b981,stroke:#34d399,color:#fff"
    diagramCaption = "Figure: Operational Flow for $Topic"
    codeTitle = "enterprise_scaffold.py"
    codeContent = "# Production Architecture Implementation for $Topic`n# Enforces high tensor core throughput and memory bounds."
    takeaway = [PSCustomObject]@{
        title = "Key Takeaways"
        items = @(
            "Incorporate $Topic principles into model serving and training architecture reviews.",
            "Establish automated evaluation baselines before releasing to production."
        )
        badge = "Disciplined architecture around $Topic creates enterprise value."
    }
}

# Prepend so it is next in line
$updatedUpcoming = @($newEntry) + @($upcoming)
$jsonUpcoming = $updatedUpcoming | ConvertTo-Json -Depth 15
[System.IO.File]::WriteAllText($upcomingJsonPath, $jsonUpcoming, [System.Text.Encoding]::UTF8)

Write-Host "Successfully queued '$Topic' as the NEXT post to publish!" -ForegroundColor Green
Write-Host "Total queued topics: $($updatedUpcoming.Count)" -ForegroundColor Cyan
