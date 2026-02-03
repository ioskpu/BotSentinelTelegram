#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Development environment startup script for Crypto Sentinel Bot

.DESCRIPTION
    Starts all services in development mode with hot reload

.PARAMETER Service
    Specific service to start (api, bot, dashboard, all)

.PARAMETER Logs
    Show logs after starting

.EXAMPLE
    .\dev.ps1 -Service all -Logs
#>

param(
    [ValidateSet("api", "bot", "dashboard", "all")]
    [string]$Service = "all",
    
    [switch]$Logs,
    
    [switch]$Build,
    
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Set-Location $ProjectRoot

Write-Host "🚀 Crypto Sentinel Bot - Development Environment" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Check if .env exists
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "⚠️  .env file not found. Creating from .env.example..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "📝 Please edit .env with your actual values" -ForegroundColor Yellow
    } else {
        Write-Host "❌ No .env or .env.example found!" -ForegroundColor Red
        exit 1
    }
}

# Clean if requested
if ($Clean) {
    Write-Host "🧹 Cleaning up containers and volumes..." -ForegroundColor Yellow
    docker-compose down -v --remove-orphans
}

# Build if requested
if ($Build) {
    Write-Host "🔨 Building Docker images..." -ForegroundColor Blue
    docker-compose build --no-cache
}

function Start-AllServices {
    Write-Host "🐳 Starting all services with Docker Compose..." -ForegroundColor Green
    docker-compose up -d
    
    Write-Host "`n✅ Services started!" -ForegroundColor Green
    Write-Host "`n📊 Service URLs:" -ForegroundColor Cyan
    Write-Host "   - Dashboard: http://localhost:3000" -ForegroundColor White
    Write-Host "   - API:       http://localhost:8080" -ForegroundColor White
    Write-Host "   - API Docs:  http://localhost:8080/docs" -ForegroundColor White
    Write-Host "   - MongoDB:   mongodb://localhost:27017" -ForegroundColor White
    Write-Host "   - Redis:     redis://localhost:6379" -ForegroundColor White
}

function Start-ApiOnly {
    Write-Host "🔌 Starting API service..." -ForegroundColor Green
    docker-compose up -d mongodb redis api
    Write-Host "`n✅ API started at http://localhost:8080" -ForegroundColor Green
}

function Start-BotOnly {
    Write-Host "🤖 Starting Bot service..." -ForegroundColor Green
    docker-compose up -d mongodb redis bot
    Write-Host "`n✅ Bot started!" -ForegroundColor Green
}

function Start-DashboardOnly {
    Write-Host "📊 Starting Dashboard service..." -ForegroundColor Green
    
    # Check if dashboard directory exists
    if (-not (Test-Path "dashboard")) {
        Write-Host "❌ Dashboard directory not found!" -ForegroundColor Red
        exit 1
    }
    
    # Start dependencies first
    docker-compose up -d mongodb redis api
    
    # Start dashboard with hot reload using npm
    Push-Location "dashboard"
    
    if (-not (Test-Path "node_modules")) {
        Write-Host "📦 Installing dashboard dependencies..." -ForegroundColor Yellow
        npm install
    }
    
    Write-Host "🔄 Starting dashboard with hot reload..." -ForegroundColor Green
    npm run dev
    
    Pop-Location
}

# Start services based on selection
switch ($Service) {
    "api" { Start-ApiOnly }
    "bot" { Start-BotOnly }
    "dashboard" { Start-DashboardOnly }
    "all" { Start-AllServices }
}

# Show logs if requested
if ($Logs -and $Service -ne "dashboard") {
    Write-Host "`n📋 Showing logs (Ctrl+C to exit)..." -ForegroundColor Cyan
    
    switch ($Service) {
        "api" { docker-compose logs -f api }
        "bot" { docker-compose logs -f bot }
        "all" { docker-compose logs -f }
    }
}

Write-Host "`n💡 Useful commands:" -ForegroundColor Yellow
Write-Host "   docker-compose logs -f          # View all logs" -ForegroundColor Gray
Write-Host "   docker-compose logs -f api      # View API logs" -ForegroundColor Gray
Write-Host "   docker-compose ps               # List running services" -ForegroundColor Gray
Write-Host "   docker-compose down             # Stop all services" -ForegroundColor Gray
