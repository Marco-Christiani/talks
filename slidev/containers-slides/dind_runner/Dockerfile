# dind_runner/Dockerfile
FROM docker:dind

RUN apk add --no-cache go bash tini curl tmux nano vim neovim

RUN mkdir /app
WORKDIR /app
COPY main.go go.mod go.sum /app/

RUN go build -o runner main.go

RUN cat <<EOF > /app/.tmux.conf
set -g mouse on
set -g terminal-overrides 'xterm*:smcup@:rmcup@'

# Visual indicators for panes
set -g pane-active-border-style 'fg=colour208,bg=default'
set -g pane-border-style 'fg=colour238,bg=default'

# New window with Ctrl+T
bind -n C-t new-window
# Switch windows with Ctrl+PageUp/PageDown
bind -n C-PageUp previous-window
bind -n C-PageDown next-window
# Close window with Ctrl+W
bind -n C-w kill-window

# Split panes
bind -n C-M-Right split-window -h  # Ctrl+Alt+Right for vertical split
bind -n C-M-Down split-window -v   # Ctrl+Alt+Down for horizontal split


# Status bar configuration
set -g status-position bottom
set -g status-bg colour235
set -g status-fg colour136
set -g status-left '[#S] '
set -g status-right '#{?client_prefix,⌨ ,}%H:%M '
set -g window-status-current-format '#[bg=colour240]#[fg=colour255] #I:#W '
set -g window-status-format ' #I:#W '

# Show pane numbers longer
set -g display-panes-time 2000

# ------------------------------------------------------------------
set -g mouse on

# Enable scroll wheel in copy mode
bind -n WheelUpPane if-shell -F -t = "#{mouse_any_flag}" "send-keys -M" "if -Ft= '#{pane_in_mode}' 'send-keys -M' 'select-pane -t=; copy-mode -e; send-keys -M'"
bind -n WheelDownPane select-pane -t= \; send-keys -M

# Increase scrollback history
set -g history-limit 10000

# Enable vi mode for copy mode (optional)
setw -g mode-keys vi

# Better colors
set -g default-terminal "screen-256color"

# Status bar styling
set -g status-bg colour235
set -g status-fg colour136
set -g status-left '[#S] '
set -g status-right '%H:%M '
set -g window-status-current-format '#[bg=colour240,fg=colour255] #I:#W '
set -g window-status-format ' #I:#W '

# Pane border colors
set -g pane-active-border-style 'fg=colour208'
set -g pane-border-style 'fg=colour238'

# Enable focus events (for vim/neovim)
set -g focus-events on

# Don't rename windows automatically
set-option -g allow-rename off
EOF

RUN cat <<'EOF' > /app/start.sh && chmod +x /app/start.sh
#!/bin/bash
set -e

echo "[+] Starting dockerd..."
dockerd-entrypoint.sh &
trap 'kill $(jobs -p)' EXIT

echo "[+] Waiting for Docker daemon to be ready..."
until docker info >/dev/null 2>&1; do
  sleep 0.2
done

echo "[+] Docker is ready. Starting runner..."
exec /app/runner
EOF

HEALTHCHECK --interval=5s --timeout=3s --start-period=10s --retries=3 \
    CMD (docker info > /dev/null && curl -f http://127.0.0.1:8000/health) || exit 1
ENTRYPOINT ["/sbin/tini", "--", "/app/start.sh"]
