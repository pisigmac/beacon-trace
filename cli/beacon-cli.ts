#!/usr/bin/env node
import { execSync } from 'child_process'
import { createServer } from 'http'
import { readFileSync, existsSync } from 'fs'
import { resolve, join } from 'path'

const args = process.argv.slice(2)
const command = args[0]

function getDashboardPath() {
  // Try to find the dashboard build relative to this script
  const possiblePaths = [
    join(__dirname, '../frontend/dist'),
    join(__dirname, '../../frontend/dist'),
    join(process.cwd(), 'node_modules/beacon-dashboard/dist'),
  ]
  for (const p of possiblePaths) {
    if (existsSync(p)) return p
  }
  return null
}

function printHelp() {
  console.log(`
Beacon CLI

Usage:
  beacon start          Start the backend collector and dashboard
  beacon status         Check if the collector is running
  beacon version        Show version

Options:
  --port <number>       Backend port (default: 8000)
  --dashboard-port      Dashboard port (default: 3000)
`)
}

function start() {
  const backendPort = args.find((a, i) => a === '--port' && args[i + 1]) ? args[args.indexOf('--port') + 1] : '8000'
  const dashboardPort = args.find((a, i) => a === '--dashboard-port' && args[i + 1]) ? args[args.indexOf('--dashboard-port') + 1] : '3000'

  console.log(`🚀 Starting Beacon...`)
  console.log(`   Collector: http://localhost:${backendPort}`)
  console.log(`   Dashboard: http://localhost:${dashboardPort}`)

  // Start backend
  const backend = execSync(`cd backend && uvicorn app.main:app --port ${backendPort} --reload`, {
    cwd: process.cwd(),
    stdio: 'inherit',
    env: { ...process.env, PYTHONPATH: join(process.cwd(), 'backend') }
  })
}

function status() {
  try {
    const res = execSync('curl -s http://localhost:8000/health', { encoding: 'utf-8' })
    const data = JSON.parse(res)
    console.log(`✅ Collector is running (${data.service})`)
  } catch {
    console.log(`❌ Collector is not running on port 8000`)
    console.log(`   Run: beacon start`)
  }
}

switch (command) {
  case 'start':
    start()
    break
  case 'status':
    status()
    break
  case 'version':
    console.log('1.0.0')
    break
  default:
    printHelp()
}
