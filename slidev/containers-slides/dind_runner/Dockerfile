# dind_runner/Dockerfile
FROM docker:dind

RUN apk add --no-cache go bash tini curl tmux nano vim neovim

# RUN apk add --no-cache tzdata && ln -s /usr/share/zoneinfo/America/New_York /etc/localtime

RUN mkdir /app
WORKDIR /app
COPY main.go go.mod go.sum /app/

RUN go build -o runner main.go

RUN cat <<EOF > /root/.tmux.conf
set-option -g default-shell /bin/bash
set -g default-terminal "tmux-256color"
set -g mouse on
set -g history-limit 10000

# Enable vi mode for copy mode
setw -g mode-keys vi

# Copy selections to the outside world via OSC 52
set -g set-clipboard on
set -as terminal-features ',tmux-256color:clipboard'

# Show pane numbers longer
set -g display-panes-time 2000

# Enable focus events (for vim/neovim)
set -g focus-events on

# Don't rename windows automatically
set-option -g allow-rename off

# Status bar styling
set -g status-position bottom
set -g status-bg colour235
set -g status-fg colour136
set -g status-left '[#S] '
set -g status-right '#{?client_prefix,* ,}%H:%M '
set -g window-status-current-format '#[bg=colour240,fg=colour255] #I:#W '
set -g window-status-format ' #I:#W '

# Pane border colors
set -g pane-active-border-style 'fg=colour208'
set -g pane-border-style 'fg=colour238'

# Visual indicators for panes
set -g pane-active-border-style 'fg=colour208,bg=default'
set -g pane-border-style 'fg=colour238,bg=default'

# Key binds --------------------------------------------------------------------

# Enable scroll wheel in copy mode
bind -n WheelUpPane if-shell -F -t = "#{mouse_any_flag}" "send-keys -M" "if -Ft= '#{pane_in_mode}' 'send-keys -M' 'select-pane -t=; copy-mode -e; send-keys -M'"
bind -n WheelDownPane select-pane -t= \; send-keys -M

# <Alt+n> next window
bind-key -n M-n next-window
# <Alt+p> previous window
bind-key -n M-p previous-window

# <prefix+,> swap window backward
bind-key -T prefix "," swap-window -t -1 -d
# <prefix+.> swap window forward
bind-key -T prefix "." swap-window -t +1 -d

# Split panes
# <Alt+s> split window vertically
bind-key -n M-s    split-window -v -c "#{pane_current_path}"
bind-key -T prefix s split-window -v -c "#{pane_current_path}"

# <Alt+v> split window horizontally
bind-key -n M-v    split-window -h -c "#{pane_current_path}"
bind-key -T prefix v split-window -h -c "#{pane_current_path}"

# prefix+j/k pane up/down (use Alt-j/k in vim)
bind-key -T prefix j select-pane -D
bind-key -T prefix k select-pane -U

# prefix+l/h pane right/left for continuity
bind-key -T prefix l select-pane -R
bind-key -T prefix h select-pane -L

# <Alt+Left/Right/Down/Up> pane resize
# -r argument makes it repeatable
bind-key -n M-'Left' resize-pane -L 5
bind-key -r -T prefix 'Left' resize-pane -L 5
bind-key -n M-'Right' resize-pane -R 5
bind-key -r -T prefix 'Right' resize-pane -R 5
bind-key -n M-'Down' resize-pane -D 5
bind-key -r -T prefix 'Down' resize-pane -D 5
bind-key -n M-'Up' resize-pane -U 5
bind-key -r -T prefix 'Up' resize-pane -U 5

# <Alt+z> Toggle zoom pane
bind-key -nr M-z resize-pane -Z

# <Alt+.> swap pane backward
bind-key -n M-"." swap-pane -D
# <Alt+,> swap pane forward
bind-key -n M-"," swap-pane -U
EOF

RUN cat <<'EOF' > /root/.bashrc
export TERM="tmux-256color"
export PS1="\\u@\\h:\\w\\$ "
tz() {
    apk add alpine-conf
    setup-timezone -z America/New_York
}

nvim() {
    apk add git lazygit fzf curl neovim ripgrep alpine-sdk --update
    git clone https://github.com/LazyVim/starter ~/.config/nvim
    cd ~/.config/nvim
    exec nvim
}
EOF

RUN cat <<'EOF' > /root/.bash_profile
[[ -f ~/.bashrc ]] && source ~/.bashrc
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
