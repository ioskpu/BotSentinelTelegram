#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Build script for Crypto Sentinel Bot

.DESCRIPTION
    Builds frontend assets and Docker images

.PARAMETER Target
    What to build (frontend, docker, all)

.PARAMETER Tag
    Docker image tag

.PARAMETER Push
    Push images to registry after build

.PARAMETER Registry
    Docker registry URL

.EXAMPLE
    .\build.ps1 -Target all -Tag v1.0.0 -Push
#>

param(
    [ValidateSet("frontend", "docker", "all")]
    [string]$Target = "all",
    
    [string]$Tag = "latest",
    
    [switch]$Push,
    
    [string]$Registry = "",
    
    [switch]$NoCache
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Set-Location $ProjectRoot

Write-Host "🔨 Crypto Sentinel Bot - Build Script" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Target: $Target | Tag: $Tag" -ForegroundColor Gray

$BuildArgs = if ($NoCache) { "--no-cache" } else { "" }
$ImagePrefix = if ($Registry) { "$Registry/" } else { "" }

function Build-Frontend {
    Write-Host "`n📦 Building Frontend..." -ForegroundColor Blue
    
    if (-not (Test-Path "dashboard")) {
        Write-Host "❌ Dashboard directory not found!" -ForegroundColor Red
        return $false
    }
    
    Push-Location "dashboard"
    
    try {
        # Install dependencies
        if (-not (Test-Path "node_modules")) {
            Write-Host "   Installing dependencies..." -ForegroundColor Gray
            npm ci --legacy-peer-deps
        }
        
        # Run linting
        Write-Host "   Running linter..." -ForegroundColor Gray
        npm run lint 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "   ⚠️  Linting warnings found, continuing..." -ForegroundColor Yellow
        }
        
        # Run type check
        Write-Host "   Running type check..." -ForegroundColor Gray
        npm run type-check 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "   ⚠️  Type warnings found, continuing..." -ForegroundColor Yellow
        }
        
        # Build
        Write-Host "   Building production bundle..." -ForegroundColor Gray
        npm run build
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Frontend build complete!" -ForegroundColor Green
            
            # Show bundle size
            if (Test-Path "dist") {
                $size = (Get-ChildItem -Path "dist" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
                Write-Host "   📊 Bundle size: $([math]::Round($size, 2)) MB" -ForegroundColor Gray
            }
            return $true
        } else {
            Write-Host "   ❌ Frontend build failed!" -ForegroundColor Red
            return $false
        }
    }
    finally {
        Pop-Location
    }
}

function Build-DockerImages {
    Write-Host "`n🐳 Building Docker Images..." -ForegroundColor Blue
    
    $images = @(
        @{
            Name = "crypto-sentinel-api"
            Context = "."
            Dockerfile = "Dockerfile"
        },
        @{
            Name = "crypto-sentinel-dashboard"
            Context = "./dashboard"
            Dockerfile = "Dockerfile"
        }
    )
    
    $success = $true
    
    foreach ($image in $images) {
        $imageName = "${ImagePrefix}$($image.Name):$Tag"
        Write-Host "   Building $imageName..." -ForegroundColor Gray
        
        $buildCmd = "docker build $BuildArgs -t $imageName -f $($image.Context)/$($image.Dockerfile) $($image.Context)"
        Invoke-Expression $buildCmd
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $($image.Name) built successfully" -ForegroundColor Green
            
            # Also tag as latest if not already
            if ($Tag -ne "latest") {
                $latestName = "${ImagePrefix}$($image.Name):latest"
                docker tag $imageName $latestName
            }
        } else {
            Write-Host "   ❌ Failed to build $($image.Name)" -ForegroundColor Red
            $success = $false
        }
    }
    
    return $success
}

function Push-DockerImages {
    Write-Host "`n📤 Pushing Docker Images..." -ForegroundColor Blue
    
    if (-not $Registry) {
        Write-Host "   ⚠️  No registry specified, skipping push" -ForegroundColor Yellow
        return $true
    }
    
    $images = @(
        "crypto-sentinel-api",
        "crypto-sentinel-dashboard"
    )
    
    $success = $true
    
    foreach ($image in $images) {
        $imageName = "${ImagePrefix}${image}:$Tag"
        Write-Host "   Pushing $imageName..." -ForegroundColor Gray
        
        docker push $imageName
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $image pushed successfully" -ForegroundColor Green
        } else {
            Write-Host "   ❌ Failed to push $image" -ForegroundColor Red
            $success = $false
        }
    }
    
    return $success
}

# Execute build steps
$success = $true

switch ($Target) {
    "frontend" {
        $success = Build-Frontend
    }
    "docker" {
        $success = Build-DockerImages
    }
    "all" {
        $success = Build-Frontend
        if ($success) {
            $success = Build-DockerImages
        }
    }
}

# Push if requested
if ($success -and $Push) {
    $success = Push-DockerImages
}

# Summary
Write-Host "`n======================================" -ForegroundColor Cyan
if ($success) {
    Write-Host "✅ Build completed successfully!" -ForegroundColor Green
    
    Write-Host "`n📋 Built images:" -ForegroundColor Cyan
    docker images | Select-String "crypto-sentinel"
} else {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}
