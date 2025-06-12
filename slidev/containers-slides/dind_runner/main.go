// dind_runner/main.go
package main

import (
	"context"
	"encoding/json"
	"io"
	"log/slog"
	"net/http"
	"os"
	"os/exec"
	"strings"
	"syscall"
	"time"
	"unsafe"

	"github.com/creack/pty"
	"github.com/gorilla/websocket"
)

var logger *slog.Logger

func init() {
	// Set up structured logging with levels
	level := slog.LevelInfo
	if os.Getenv("DEBUG") == "1" {
		level = slog.LevelDebug
	}

	opts := &slog.HandlerOptions{
		Level: level,
	}

	handler := slog.NewTextHandler(os.Stdout, opts)
	logger = slog.New(handler)
}

type CommandRequest struct {
	Cmd   string `json:"cmd"`
	Debug bool   `json:"debug,omitempty"`
}

type TerminalMessage struct {
	Type string      `json:"type"`
	Data interface{} `json:"data"`
}

type ResizeMessage struct {
	Cols int `json:"cols"`
	Rows int `json:"rows"`
}

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		// Allow all origins for development - restrict in production
		return true
	},
}

func runHandler(w http.ResponseWriter, r *http.Request) {
	logger.Debug("Handling run request", "method", r.Method, "path", r.URL.Path)

	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	body, err := io.ReadAll(r.Body)
	if err != nil {
		logger.Error("Failed to read request body", "error", err)
		http.Error(w, "Failed to read request body", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	var input CommandRequest
	if err := json.Unmarshal(body, &input); err != nil {
		logger.Error("Failed to parse JSON", "error", err)
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	// Validate command is not empty
	if strings.TrimSpace(input.Cmd) == "" {
		logger.Warn("Empty command received")
		http.Error(w, "Command cannot be empty", http.StatusBadRequest)
		return
	}

	debugEnabled := input.Debug || os.Getenv("DEBUG") == "1"

	if debugEnabled {
		logger.Debug("Executing command", "cmd", input.Cmd)
	}

	// Create context with timeout to prevent hanging commands
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	cmd := exec.CommandContext(ctx, "sh", "-c", input.Cmd)
	out, err := cmd.CombinedOutput()

	if err != nil {
		logger.Error("Command execution failed", "cmd", input.Cmd, "error", err)
		if debugEnabled {
			logger.Debug("Command output", "output", string(out))
		}
		// Still return the output even if command failed (non-zero exit)
	} else if debugEnabled {
		logger.Debug("Command executed successfully", "output", string(out))
	}

	w.Header().Set("Content-Type", "text/plain")
	w.Write(out)
}

func terminalHandler(w http.ResponseWriter, r *http.Request) {
	logger.Debug("Handling terminal WebSocket request")

	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		logger.Error("Failed to upgrade WebSocket connection", "error", err)
		return
	}
	defer conn.Close()

	// Start a shell process with PTY
	cmd := exec.Command("/bin/bash")
	cmd.Env = append(os.Environ(),
		"TERM=xterm-256color",
		"PS1=\\u@\\h:\\w\\$ ",
	)

	// Create PTY
	ptmx, err := pty.Start(cmd)
	if err != nil {
		logger.Error("Failed to start PTY", "error", err)
		conn.WriteJSON(TerminalMessage{
			Type: "error",
			Data: "Failed to start terminal",
		})
		return
	}
	defer ptmx.Close()

	logger.Debug("Terminal session started", "pid", cmd.Process.Pid)

	// Handle WebSocket messages
	go func() {
		defer cmd.Process.Kill()
		for {
			var msg TerminalMessage
			if err := conn.ReadJSON(&msg); err != nil {
				logger.Debug("WebSocket read error", "error", err)
				return
			}

			switch msg.Type {
			case "input":
				if data, ok := msg.Data.(string); ok {
					ptmx.Write([]byte(data))
				}
			case "resize":
				if resizeData, ok := msg.Data.(map[string]interface{}); ok {
					cols, colsOk := resizeData["cols"].(float64)
					rows, rowsOk := resizeData["rows"].(float64)
					if colsOk && rowsOk {
						setWinsize(ptmx, int(cols), int(rows))
					}
				}
			}
		}
	}()

	// Stream PTY output to WebSocket
	buf := make([]byte, 1024)
	for {
		n, err := ptmx.Read(buf)
		if err != nil {
			if err != io.EOF {
				logger.Debug("PTY read error", "error", err)
			}
			break
		}

		if err := conn.WriteJSON(TerminalMessage{
			Type: "output",
			Data: string(buf[:n]),
		}); err != nil {
			logger.Debug("WebSocket write error", "error", err)
			break
		}
	}

	logger.Debug("Terminal session ended")
}

func setWinsize(ptmx *os.File, cols, rows int) {
	ws := &struct {
		Row    uint16
		Col    uint16
		Xpixel uint16
		Ypixel uint16
	}{
		Row: uint16(rows),
		Col: uint16(cols),
	}

	syscall.Syscall(
		syscall.SYS_IOCTL,
		ptmx.Fd(),
		syscall.TIOCSWINSZ,
		uintptr(unsafe.Pointer(ws)),
	)
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	status := map[string]interface{}{
		"status":    "healthy",
		"timestamp": time.Now().UTC().Format(time.RFC3339),
		"service":   "command-runner",
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(status)
}

func main() {
	logger.Info("Starting command runner server", "port", 8000)

	http.HandleFunc("/run", runHandler)
	http.HandleFunc("/terminal", terminalHandler)
	http.HandleFunc("/health", healthHandler)
	http.HandleFunc("/healthz", healthHandler)

	server := &http.Server{
		Addr:         ":8000",
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 40 * time.Second, // Longer than command timeout
		IdleTimeout:  60 * time.Second,
	}

	logger.Info("Server ready to accept connections")

	if err := server.ListenAndServe(); err != nil {
		logger.Error("Server failed to start", "error", err)
		os.Exit(1)
	}
}
