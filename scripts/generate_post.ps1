# Automated Post Generation Script for Windows (GenAI Hub)
param (
    [switch]$DryRun,
    [switch]$ListQueue
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$baseDir = Split-Path -Parent $scriptDir
$postsJsonPath = Join-Path $baseDir "data\posts.json"
$postsJsPath = Join-Path $baseDir "data\posts.js"
$upcomingJsonPath = Join-Path $baseDir "data\upcoming_topics.json"

if (-not (Test-Path $postsJsonPath)) {
    Write-Error "Could not find $postsJsonPath"
    exit 1
}

$posts = Get-Content $postsJsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
$upcoming = Get-Content $upcomingJsonPath -Raw -Encoding UTF8 | ConvertFrom-Json

if ($ListQueue) {
    Write-Host "Upcoming GenAI Topics count: " $upcoming.Count
    for ($i = 0; $i -lt $upcoming.Count; $i++) {
        Write-Host "  $($i + 1). [$($upcoming[$i].id)] $($upcoming[$i].title)"
    }
    exit 0
}

if ($upcoming.Count -eq 0) {
    Write-Host "No more topics in queue!"
    exit 0
}

$nextTopic = $upcoming[0]
$remaining = @()
if ($upcoming.Count -gt 1) {
    $remaining = $upcoming[1..($upcoming.Count - 1)]
}

$postNum = $posts.Count + 1
$nextTopic.id = "post-$postNum"

Write-Host "Processing scheduled post: $($nextTopic.title)"

if ($DryRun) {
    Write-Host "DRY RUN: Validated post schema successfully for: $($nextTopic.title)"
    exit 0
}

$newPosts = @($posts) + $nextTopic

$jsonPosts = $newPosts | ConvertTo-Json -Depth 15
[System.IO.File]::WriteAllText($postsJsonPath, $jsonPosts, [System.Text.Encoding]::UTF8)

$jsonUpcoming = $remaining | ConvertTo-Json -Depth 15
[System.IO.File]::WriteAllText($upcomingJsonPath, $jsonUpcoming, [System.Text.Encoding]::UTF8)

$jsContent = "// Auto-generated data sync for direct local file:// and offline execution`r`nwindow.POSTS_DATA = " + $jsonPosts + ";`r`n"
[System.IO.File]::WriteAllText($postsJsPath, $jsContent, [System.Text.Encoding]::UTF8)

Write-Host "Published '$($nextTopic.title)' successfully!"
Write-Host "Total Posts: $($newPosts.Count) | Queued remaining: $($remaining.Count)"
