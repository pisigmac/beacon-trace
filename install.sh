#!/usr/bin/env bash
set -e

# Beacon — Local-first observability for AI agents
# Usage: curl -fsSL https://raw.githubusercontent.com/pisigmac/beacon-trace/main/install.sh | bash

REPO="https://github.com/pisigmac/beacon-trace"
REPO_RAW="https://raw.githubusercontent.com/pisigmac/beacon-trace/main"
INSTALL_DIR="$HOME/.beacon/app"
BIN_DIR="$HOME/.local/bin"

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
CYAN="\033[0;36m"
RESET="\033[0m"

print_banner() {
  echo ""
  echo -e "${CYAN}${BOLD}"
  echo "  🔮 Beacon — AI Agent Observability"
  echo -e "${RESET}"
}

info()    { echo -e "  ${GREEN}✔${RESET}  $1"; }
warn()    { echo -e "  ${YELLOW}⚠${RESET}  $1"; }
error()   { echo -e "  ${RED}✘${RESET}  $1"; exit 1; }
step()    { echo -e "\n${BOLD}$1${RESET}"; }

# ── Dependency checks ────────────────────────────────────────────────────────

check_deps() {
  step "Checking dependencies..."

  command -v git  >/dev/null 2>&1 || error "git is required. Install it and re-run."
  command -v python3 >/dev/null 2>&1 || error "Python 3.8+ is required. Install it and re-run."
  command -v pip3 >/dev/null 2>&1 || command -v pip >/dev/null 2>&1 || error "pip is required. Install it and re-run."
  command -v node >/dev/null 2>&1 || error "Node.js 18+ is required. Install it from https://nodejs.org and re-run."
  command -v npm  >/dev/null 2>&1 || error "npm is required. Install it and re-run."

  PYTHON_VERSION=$(python3 -c 'import sys; print(sys.version_info.minor)')
  if [ "$PYTHON_VERSION" -lt 8 ]; then
    error "Python 3.8+ is required. Found: $(python3 --version)"
  fi

  info "git        $(git --version | awk '{print $3}')"
  info "python3    $(python3 --version | awk '{print $2}')"
  info "node       $(node --version)"
  info "npm        $(npm --version)"
}

# ── Clone or update repo ─────────────────────────────────────────────────────

clone_repo() {
  step "Setting up Beacon..."

  if [ -d "$INSTALL_DIR/.git" ]; then
    info "Existing install found at $INSTALL_DIR — updating..."
    git -C "$INSTALL_DIR" pull --quiet
  else
    info "Cloning from $REPO..."
    mkdir -p "$INSTALL_DIR"
    git clone --quiet "$REPO" "$INSTALL_DIR"
  fi
}

# ── Backend ──────────────────────────────────────────────────────────────────

install_backend() {
  step "Installing backend dependencies..."
  pip3 install --quiet -r "$INSTALL_DIR/backend/requirements.txt"
  info "Backend dependencies installed"

  pip3 install --quiet "$INSTALL_DIR/backend/sdk/python"
  info "Beacon Python SDK installed (beacon-trace)"
}

# ── Frontend ─────────────────────────────────────────────────────────────────

install_frontend() {
  step "Installing frontend dependencies..."
  npm install --prefix "$INSTALL_DIR/frontend" --silent
  info "Frontend dependencies installed"
}

# ── CLI launcher scripts ──────────────────────────────────────────────────────

install_launchers() {
  step "Installing beacon command..."

  mkdir -p "$BIN_DIR"

  # Main launcher
  cat > "$BIN_DIR/beacon" << EOF
#!/usr/bin/env bash
# Beacon launcher — starts backend + frontend
BEACON_DIR="$INSTALL_DIR"

case "\$1" in
  start)
    echo "🔮 Starting Beacon..."
    uvicorn backend.app.main:app --port \${BEACON_PORT:-8000} --host 0.0.0.0 &
    BACKEND_PID=\$!
    sleep 1
    npm run dev --prefix "\$BEACON_DIR/frontend" &
    FRONTEND_PID=\$!
    echo "  Backend  → http://localhost:\${BEACON_PORT:-8000}"
    echo "  Dashboard → http://localhost:3000"
    echo ""
    echo "  Press Ctrl+C to stop"
    trap "kill \$BACKEND_PID \$FRONTEND_PID 2>/dev/null" EXIT INT TERM
    wait
    ;;
  backend)
    cd "\$BEACON_DIR"
    uvicorn backend.app.main:app --port \${BEACON_PORT:-8000} --host 0.0.0.0
    ;;
  frontend)
    npm run dev --prefix "\$BEACON_DIR/frontend"
    ;;
  update)
    echo "🔮 Updating Beacon..."
    git -C "\$BEACON_DIR" pull
    pip3 install --quiet -r "\$BEACON_DIR/backend/requirements.txt"
  pip3 install --quiet "\$BEACON_DIR/backend/sdk/python"
    npm install --prefix "\$BEACON_DIR/frontend" --silent
    echo "✔ Beacon updated"
    ;;
  *)
    echo "Usage: beacon <command>"
    echo ""
    echo "Commands:"
    echo "  start      Start backend + dashboard"
    echo "  backend    Start backend only (port 8000)"
    echo "  frontend   Start dashboard only (port 3000)"
    echo "  update     Pull latest changes and reinstall"
    echo ""
    echo "Environment:"
    echo "  BEACON_PORT              Backend port (default: 8000)"
    echo "  BEACON_SLACK_WEBHOOK     Slack webhook URL for alerts"
    ;;
esac
EOF

  chmod +x "$BIN_DIR/beacon"
  info "Installed: $BIN_DIR/beacon"
}

# ── PATH check ────────────────────────────────────────────────────────────────

check_path() {
  if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    warn "$BIN_DIR is not in your PATH."
    echo ""
    echo "  Add this to your shell profile (~/.bashrc, ~/.zshrc, etc.):"
    echo ""
    echo -e "    ${CYAN}export PATH=\"\$HOME/.local/bin:\$PATH\"${RESET}"
    echo ""
  fi
}

# ── Done ──────────────────────────────────────────────────────────────────────

print_done() {
  echo ""
  echo -e "${GREEN}${BOLD}  Beacon installed successfully!${RESET}"
  echo ""
  echo "  Start Beacon:"
  echo -e "    ${CYAN}beacon start${RESET}"
  echo ""
  echo "  Dashboard:  http://localhost:3000"
  echo "  API:        http://localhost:8000"
  echo ""
  echo "  Instrument your agent:"
  echo -e "    ${CYAN}from beacon import trace${RESET}"
  echo -e "    ${CYAN}@trace(agent_id=\"my-agent\", api_url=\"http://localhost:8000\")${RESET}"
  echo ""
  echo "  Docs: $REPO"
  echo ""
}

# ── Main ──────────────────────────────────────────────────────────────────────

main() {
  print_banner
  check_deps
  clone_repo
  install_backend
  install_frontend
  install_launchers
  check_path
  print_done
}

main
