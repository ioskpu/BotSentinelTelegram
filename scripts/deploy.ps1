#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Deployment script for Crypto Sentinel Bot

.DESCRIPTION
    Deploy to various platforms (Fly.io, Railway, Docker)

.PARAMETER Platform
    Deployment platform (fly, railway, docker, docker-prod)

.PARAMETER Service
    Service to deploy (api, dashboard, bot, all)

.PARAMETER Environment
    Deployment environment (staging, production)

.EXAMPLE
    .\deploy.ps1 -Platform fly -Service all -Environment production
#>

param(
    [ValidateSet("fly", "railway", "docker", "docker-prod")]
    [string]$Platform = "docker",
    
    [ValidateSet("api", "dashboard", "bot", "all")]
    [string]$Service = "all",
    
    [ValidateSet("staging", "production")]
    [string]$Environment = "staging",
    
    [string]$Tag = "latest",
    
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Set-Location $ProjectRoot

Write-Host "🚀 Crypto Sentinel Bot - Deployment" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Platform: $Platform | Service: $Service | Env: $Environment" -ForegroundColor Gray

if ($DryRun) {
    Write-Host "⚠️  DRY RUN MODE - No changes will be made" -ForegroundColor Yellow
}

function Test-Prerequisites {
    param([string]$Platform)
    
    switch ($Platform) {
        "fly" {
            if (-not (Get-Command "flyctl" -ErrorAction SilentlyContinue)) {
                Write-Host "❌ flyctl not found. Install from https://fly.io/docs/hands-on/install-flyctl/" -ForegroundColor Red
                return $false
            }
            
            # Check if logged in
            $result = flyctl auth whoami 2>&1
            if ($LASTEXITCODE -ne 0) {
                Write-Host "❌ Not logged in to Fly.io. Run: flyctl auth login" -ForegroundColor Red
                return $false
            }
            Write-Host "   ✅ Fly.io CLI ready (logged in as: $result)" -ForegroundColor Green
        }
        "railway" {
            if (-not (Get-Command "railway" -ErrorAction SilentlyContinue)) {
                Write-Host "❌ railway CLI not found. Install from https://docs.railway.app/develop/cli" -ForegroundColor Red
                return $false
            }
            Write-Host "   ✅ Railway CLI ready" -ForegroundColor Green
        }
        "docker" {
            if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
                Write-Host "❌ docker not found" -ForegroundColor Red
                return $false
            }
            Write-Host "   ✅ Docker ready" -ForegroundColor Green
        }
    }
    
    return $true
}

function Deploy-ToFly {
    param([string]$Service)
    
    Write-Host "`n☁️  Deploying to Fly.io..." -ForegroundColor Blue
    
    $configs = @{
        "api" = "fly.toml"
        "dashboard" = "deploy/fly.dashboard.toml"
        "bot" = "fly.toml"
    }
    
    $services = if ($Service -eq "all") { @("api", "dashboard") } else { @($Service) }
    
    foreach ($svc in $services) {
        $config = $configs[$svc]
        
        if (-not (Test-Path $config)) {
            Write-Host "   ⚠️  Config not found: $config, skipping $svc" -ForegroundColor Yellow
            continue
        }
        
        Write-Host "   Deploying $svc using $config..." -ForegroundColor Gray
        
        if ($DryRun) {
            Write-Host "   [DRY RUN] Would run: flyctl deploy --config $config" -ForegroundColor Yellow
        } else {
            flyctl deploy --config $config
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "   ✅ $svc deployed successfully" -ForegroundColor Green
            } else {
                Write-Host "   ❌ Failed to deploy $svc" -ForegroundColor Red
                return $false
            }
        }
    }
    
    return $true
}

function Deploy-ToRailway {
    param([string]$Service)
    
    Write-Host "`n🚂 Deploying to Railway..." -ForegroundColor Blue
    
    if ($DryRun) {
        Write-Host "   [DRY RUN] Would run: railway up" -ForegroundColor Yellow
    } else {
        railway up
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Deployed to Railway successfully" -ForegroundColor Green
        } else {
            Write-Host "   ❌ Failed to deploy to Railway" -ForegroundColor Red
            return $false
        }
    }
    
    return $true
}

function Deploy-ToDocker {
    param([string]$Service, [bool]$Production)
    
    $composeFile = if ($Production) { "deploy/docker-compose.prod.yml" } else { "docker-compose.yml" }
    $envLabel = if ($Production) { "Production" } else { "Development" }
    
    Write-Host "`n🐳 Deploying with Docker Compose ($envLabel)..." -ForegroundColor Blue
    
    if (-not (Test-Path $composeFile)) {
        Write-Host "   ❌ Compose file not found: $composeFile" -ForegroundColor Red
        return $false
    }
    
    $services = if ($Service -eq "all") { "" } else { $Service }
    
    # Pull latest images for production
    if ($Production) {
        Write-Host "   Pulling latest images..." -ForegroundColor Gray
        if (-not $DryRun) {
            docker-compose -f $composeFile pull $services
        }
    }
    
    # Build if needed
    Write-Host "   Building services..." -ForegroundColor Gray
    if ($DryRun) {
        Write-Host "   [DRY RUN] Would run: docker-compose -f $composeFile build $services" -ForegroundColor Yellow
    } else {
        docker-compose -f $composeFile build $services
    }
    
    # Deploy
    Write-Host "   Starting services..." -ForegroundColor Gray
    if ($DryRun) {
        Write-Host "   [DRY RUN] Would run: docker-compose -f $composeFile up -d $services" -ForegroundColor Yellow
    } else {
        docker-compose -f $composeFile up -d $services
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Docker deployment successful" -ForegroundColor Green
            
            # Show running containers
            Write-Host "`n   Running containers:" -ForegroundColor Cyan
            docker-compose -f $composeFile ps
        } else {
            Write-Host "   ❌ Docker deployment failed" -ForegroundColor Red
            return $false
        }
    }
    
    return $true
}

function Show-DeploymentInfo {
    param([string]$Platform)
    
    Write-Host "`n📋 Deployment Info:" -ForegroundColor Cyan
    
    switch ($Platform) {
        "fly" {
            Write-Host "   Run 'flyctl status' to check deployment status" -ForegroundColor Gray
            Write-Host "   Run 'flyctl logs' to view logs" -ForegroundColor Gray
        }
        "railway" {
            Write-Host "   Run 'railway logs' to view logs" -ForegroundColor Gray
            Write-Host "   Run 'railway open' to open dashboard" -ForegroundColor Gray
        }
        "docker" {
            Write-Host "   Run 'docker-compose logs -f' to view logs" -ForegroundColor Gray
            Write-Host "   Run 'docker-compose ps' to check status" -ForegroundColor Gray
        }
        "docker-prod" {
            Write-Host "   Run 'docker-compose -f deploy/docker-compose.prod.yml logs -f' to view logs" -ForegroundColor Gray
        }
    }
}

# Check prerequisites
Write-Host "`n🔍 Checking prerequisites..." -ForegroundColor Blue
if (-not (Test-Prerequisites -Platform $Platform)) {
    exit 1
}

# Execute deployment
$success = $false

switch ($Platform) {
    "fly" {
        $success = Deploy-ToFly -Service $Service
    }
    "railway" {
        $success = Deploy-ToRailway -Service $Service
    }
    "docker" {
        $success = Deploy-ToDocker -Service $Service -Production $false
    }
    "docker-prod" {
        $success = Deploy-ToDocker -Service $Service -Production $true
    }
}

# Show result
Write-Host "`n====================================" -ForegroundColor Cyan
if ($success) {
    Write-Host "✅ Deployment completed!" -ForegroundColor Green
    Show-DeploymentInfo -Platform $Platform
} else {
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    exit 1
}
